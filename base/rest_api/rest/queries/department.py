from api.models import CourseUnit, Department
from logs import general_log
from logs.logs_decorator import log_operations_time, log_and_catch_query


@log_operations_time
@log_and_catch_query((Exception, "Erro ao obter todos os departamentos"))
def all_departments():
    """
    Get all departments from db
    :return: tuple with
        - Departments data
        - list of success messages
        - list of error messages
    """
    success = []
    data = Department.objects.all().order_by('id')

    success.append("Departamentos obtidos com sucesso")
    general_log.debug(f"{__name__}->{all_departments.__name__} {success[-1]}")

    return data, success, []


@log_operations_time
@log_and_catch_query((Exception, "Erro ao obter todas as unidades curriculares por departamento"))
def course_units_by_department(department_id: int):
    """
    Get all curricular units per department from db
    :return: tuple with
        - Curricular units per department data
        - list of success messages
        - list of error messages
    """
    success = []
    data = CourseUnit.objects.filter(department__id=department_id).order_by('id')

    success.append("Unidades curriculares obtidas com sucesso")
    general_log.debug(f"{__name__}->{course_units_by_department.__name__} {success[-1]}")

    return data, success, []
