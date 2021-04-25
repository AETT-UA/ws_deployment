from api.models import Attendance, CourseUnit, Student
from logs import general_log
from logs.logs_decorator import log_operations_time, log_and_catch_query
from django.db import transaction
from rest.queries.utils import generate_random_id


@log_operations_time
@log_and_catch_query(
    (Exception, "Erro ao obter todas as cadeiras")
)
def course_units():
    """
    Get all course units available persisted in DB
    :return: tuple with
        - Course units data
        - list of success messages
        - list of error messages
    """
    success = []
    data = CourseUnit.objects.all().order_by('name')

    success.append("Cadeiras obtidas com sucesso")
    general_log.debug(f"{__name__}->{course_units.__name__} {success[-1]}")

    return data, success, []


@log_operations_time
@log_and_catch_query(
    (Exception, "Erro ao obter as cadeiras do docente")
)
def course_units_my(user):
    """
    Get all course units assign to a teacher available persisted in DB
    :return: tuple with
        - Course units data
        - list of success messages
        - list of error messages
    """
    success = []
    data = set([attendance.course_unit for attendance in
                Attendance.objects.filter(creator=user).order_by('course_unit__name')])

    success.append("Cadeiras do docente obtidas com sucesso")
    general_log.debug(f"{__name__}->{course_units.__name__} {success[-1]}")

    return data, success, []


@log_operations_time
@log_and_catch_query(
    (CourseUnit.DoesNotExist, "Cadeira selecionada não existe"),
    (Exception, "Erro ao criar folha de presenças")
)
def create_attendance_sheet(creator, data):
    """
    Function to create attendance_sheet in DB
    :param creator: creator of the attendance_sheet
    :param data: data for attendance_sheet creation (in this case course's ID)
    :return: tuple with
        - Dictionary with lesson's ID
        - list of success messages
        - list of error messages
    """
    success = []

    with transaction.atomic():
        course = CourseUnit.objects.get(id=data.get('course_unit'))

        while True:
            random_id = generate_random_id()
            if not Attendance.objects.filter(id=random_id).exists():
                break

        Attendance.objects.create(id=random_id, creator=creator, course_unit=course, summary=data.get('summary'))

        success.append("Folha de presenças criada com sucesso")
        general_log.debug(
            f"{__name__}->{create_attendance_sheet.__name__} {success[-1]}")

    return {"attendance_id": random_id}, success, []


@log_operations_time
@log_and_catch_query(
    (Attendance.DoesNotExist, "Folha de presenças não existe"),
    (Exception, "Erro ao mudar o estado da folha de presenças")
)
def attendance_status(user, sheet_id, status):
    """
    Change the activation status of an attendance sheet and persist the changes in DB
    :param user: Request's user
    :param sheet_id: Attendance sheet's ID
    :param status: Activation status
    :return: tuple with
    - Empty dictionary
    - list of success messages
    - list of error messages
    """
    success, errors, is_authorized = [], [], True

    attendance = Attendance.objects.get(id=sheet_id)

    if attendance.creator == user:
        attendance.is_active = status
        attendance.save()

        success.append("Estado da folha de presenças mudado com sucesso")
        general_log.debug(
            f"{__name__}->{attendance_status.__name__} {success[-1]}")

    else:
        is_authorized = False
        errors.append("Apenas o criador desta folha de presenças pode mudar o estado da mesma")
        general_log.error(
            f"{__name__}->{attendance_status.__name__} {errors[-1]}")

    return {'is_authorized': is_authorized}, success, errors


@log_operations_time
@log_and_catch_query(
    (Attendance.DoesNotExist, "Folha de presenças não existe"),
    (Exception, "Erro ao obter os alunos registados na folha de presença")
)
def students_in_attendance_sheet(user, sheet_id):
    """
    Get students registered on an attendance sheet saved on DB
    :param user: Http Request
    :param sheet_id: Attendance sheet's ID
    :return: tuple with
    - Students nmecs
    - list of success messages
    - list of error messages
    """
    data, success, errors, is_authorized = {}, [], [], True

    attendance = Attendance.objects.get(id=sheet_id)

    if attendance.creator == user:
        data['data'] = {'students': attendance.students.all()}
        success.append(
            "Alunos registados na folha de presença obtidos com sucesso")
        general_log.debug(
            f"{__name__}->{students_in_attendance_sheet.__name__} {success[-1]}")

    else:
        is_authorized = False
        errors.append("Apenas o criador desta folha pode obter os alunos registados na mesma")
        general_log.error(
            f"{__name__}->{students_in_attendance_sheet.__name__} {errors[-1]}")

    data['is_authorized'] = is_authorized

    return data, success, errors


@log_operations_time
@log_and_catch_query(
    (Attendance.DoesNotExist, "Folha de presenças não existe"),
    (Exception, "Erro ao registar-se na aula")
)
def attendance_sheet_student_registration(sheet_id, token, student):
    """
    Register a user in an attendance sheet
    :param sheet_id: Attendance sheet's ID
    :param token: Request's user token
    :param student: dictionary with student's data
    :return: tuple with
    - Empty dictionary
    - list of success messages
    - list of error messages
    """
    success, errors = [], []

    attendance = Attendance.objects.get(id=sheet_id)

    if attendance.is_active or token is not None:
        nmec, name = student.get('nmec'), student.get('name')
        student = Student.objects.update_or_create(nmec=nmec, defaults={'name': name})[0]
        attendance.students.add(student)
        attendance.save()

        success.append(
            f"Aluno(s) registado(s) com sucesso na folha de presenças")
        general_log.debug(
            f"{__name__}->{attendance_sheet_student_registration.__name__} {success[-1]}")

    else:
        errors.append(
            "A folha de presenças encontra-se encerrada. Não é possivel submeter o registo")
        general_log.error(
            f"{__name__}->{attendance_sheet_student_registration.__name__} {errors[-1]}")

    return [], success, errors


@log_operations_time
@log_and_catch_query(
    (Attendance.DoesNotExist, "Folha de presenças não existe"),
    (Exception, "Erro ao eliminar registo(s) de aluno(s)")
)
def attendance_sheet_student_deletion(user, sheet_id, data):
    """
    Remove a student from an attendance sheet and persist the changes
    :param user: Http Request user
    :param sheet_id: Attendance sheet's ID
    :param data: Dictionary with a lits of nmecs to be removed
    :return: Operations status wrapped on response's object
    """
    success, errors = [], []

    nmecs = data.get('nmecs')
    attendance = Attendance.objects.get(id=sheet_id)

    if attendance.creator != user:
        errors.append(
            "Apenas o criador desta folha pode remover registos de alunos na mesma")
        general_log.error(
            f"{__name__}->{students_in_attendance_sheet.__name__} {errors[-1]}")

    else:
        with transaction.atomic():
            for nmec in nmecs:
                student = Student.objects.filter(nmec=nmec)

                if student.exists():
                    attendance.students.remove(student[0])

        success.append("Registo(s) de aluno(s) eliminados com sucesso")
        general_log.debug(
            f"{__name__}->{attendance_sheet_student_registration.__name__} {success[-1]}")

    return [], success, errors


@log_operations_time
@log_and_catch_query(
    (Exception, "Erro ao obter as folhas de presença")
)
def attendance_sheets(user, course_id):
    """
    Get attendance sheets available persisted in DB (if user is defined, returns the attendance sheets
    associated with that user
    :param user: Specified user
    :param course_id: Course unit's ID
    :return: tuple with
        - Attendance sheets data
        - list of success messages
        - list of error messages
    """
    success = []
    data = Attendance.objects.filter(creator=user, course_unit_id=course_id)

    success.append("Folhas de presença obtidas com sucesso")
    general_log.debug(
        f"{__name__}->{attendance_sheets.__name__} {success[-1]}")

    return data, success, []


@log_operations_time
@log_and_catch_query(
    (Attendance.DoesNotExist, "Folha de presenças não existe"),
    (Exception, "Erro ao obter as informações da folha de presenças")
)
def attendance_info(sheet_id):
    """
    Get attendance info
    :param sheet_id: Sheet's ID
    :return: tuple with
        - Attendance sheets data
        - list of success messages
        - list of error messages
    """
    success, errors = [], []
    attendance = Attendance.objects.get(id=sheet_id)

    creator = attendance.creator
    data = {
        'timestamp': attendance.register_timestamp,
        'course_unit_name': attendance.course_unit.name,
        'creator_name': f'{creator.first_name} {creator.last_name}',
        'summary': attendance.summary,
        'is_active': attendance.is_active
    }

    success.append("Folha de presenças obtida com sucesso")
    general_log.debug(f"{__name__}->{attendance_info.__name__} {success[-1]}")

    return data, success, errors
