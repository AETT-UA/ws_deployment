from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_401_UNAUTHORIZED

from api.serializers import AttendanceStatusSerializer, CourseUnitSerializer, \
    StudentSerializer, AttendanceSimpleSerializer, CourseUnitSimpleSerializer, StudentNmecSerializer
from api.views.utils import serializer_not_valid_response, create_response
from logs import general_log
from logs.logs_decorator import log_operations_time, log_and_catch_view
from rest.queries import attendance as attendance_queries
from rest.queries.utils import get_token
from swagger.attendance import create_attendance_sheet_swagger, attendance_status_swagger, \
    students_in_attendance_sheet_swagger, course_units_swagger, attendance_sheet_student_registration_swagger, \
    attendance_sheet_student_deletion_swagger, attendance_sheets_swagger, attendance_info_swagger


@cache_control(public=True, max_age=60 * 60 * 24)
@course_units_swagger
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
@log_operations_time
@log_and_catch_view((Exception, "Erro ao obter todas as cadeiras", HTTP_400_BAD_REQUEST))
def course_units(request):
    """
    Get all course units available
    :param request: Http Request
    :return: Course units data and operations status wrapped on response's object
    """
    data, success, errors = attendance_queries.course_units()

    data = CourseUnitSerializer(data, many=True).data

    response = create_response(data=data, success=success, errors=errors, status=HTTP_200_OK,
                               token=get_token(request.user))
    general_log.debug(
        f"{__name__}->{course_units.__name__} {response.__dict__}")

    return response


@csrf_exempt
@api_view(["GET"])
@log_operations_time
@log_and_catch_view((Exception, "Erro ao obter as cadeiras do docente", HTTP_400_BAD_REQUEST))
def course_units_my(request):
    """
    Get all course units available assign to a teacher
    :param request: Http Request
    :return: Course units data and operations status wrapped on response's object
    """
    user = request.user
    token = get_token(user)
    data, success, errors = attendance_queries.course_units_my(user)

    data = CourseUnitSerializer(data, many=True).data

    status = HTTP_200_OK if len(errors) == 0 else HTTP_400_BAD_REQUEST

    response = create_response(data=data, success=success, errors=errors, status=status,
                               token=token)
    general_log.debug(
        f"{__name__}->{course_units.__name__} {response.__dict__}")

    return response


@create_attendance_sheet_swagger
@csrf_exempt
@api_view(["POST"])
@log_operations_time
@log_and_catch_view((Exception, "Erro ao criar nova folha de presenças", HTTP_400_BAD_REQUEST))
def create_attendance_sheet(request):
    """
    Create an attendance_sheet
    :param request: Http Request
    :return: Operations status wrapped on response's object
    """
    user = request.user
    token = get_token(user)
    data = request.data

    course_unit_id_serializer = CourseUnitSimpleSerializer(data=data)

    if not course_unit_id_serializer.is_valid():
        return serializer_not_valid_response(course_unit_id_serializer, create_attendance_sheet.__name__, token)

    data, success, errors = attendance_queries.create_attendance_sheet(
        user, course_unit_id_serializer.validated_data)

    status = HTTP_200_OK if len(errors) == 0 else HTTP_400_BAD_REQUEST

    response = create_response(
        data=data, token=token, success=success, errors=errors, status=status)
    general_log.debug(
        f"{__name__}->{create_attendance_sheet.__name__} {response.__dict__}")

    return response


@attendance_status_swagger
@csrf_exempt
@api_view(["POST"])
@log_operations_time
@log_and_catch_view((Exception, "Erro ao mudar o estado da folha de presenças", HTTP_400_BAD_REQUEST))
def attendance_status(request, sheet_id):
    """
    Change the activation status of an attendance sheet
    :param request: Http Request
    :param sheet_id: Attendance sheet's ID
    :return: Operations status wrapped on response's object
    """
    user = request.user
    token = get_token(user)

    attendance_status_serializer = AttendanceStatusSerializer(
        data=request.data)

    if not attendance_status_serializer.is_valid():
        return serializer_not_valid_response(attendance_status_serializer, attendance_status.__name__, token)

    data, success, errors = attendance_queries.attendance_status(user, sheet_id,
                                                                 attendance_status_serializer.validated_data.get(
                                                                     'status'))

    status = HTTP_200_OK if len(errors) == 0 else HTTP_400_BAD_REQUEST
    if not data.get('is_authorized'):
        status = HTTP_401_UNAUTHORIZED

    response = create_response(
        token=token, success=success, errors=errors, status=status)
    general_log.debug(
        f"{__name__}->{attendance_status.__name__} {response.__dict__}")

    return response


@students_in_attendance_sheet_swagger
@csrf_exempt
@api_view(["GET"])
@log_operations_time
@log_and_catch_view((Exception, "Erro ao obter os alunos registados na folha de presença", HTTP_400_BAD_REQUEST))
def students_in_attendance_sheet(request, sheet_id):
    """
    Get students registered on an attendance sheet
    :param request: Http Request
    :param sheet_id: Attendance sheet's ID
    :return: Students nmecs and operations status wrapped on response's object
    """
    user = request.user
    token = get_token(user)

    query_data, success, errors = attendance_queries.students_in_attendance_sheet(
        user, sheet_id)

    status = HTTP_200_OK if len(errors) == 0 else HTTP_400_BAD_REQUEST
    if not query_data.get('is_authorized'):
        status = HTTP_401_UNAUTHORIZED

    data = StudentSerializer(query_data.get(
        'data', {}).get('students'), many=True).data
    response = create_response(
        data=data, token=token, success=success, errors=errors, status=status)
    general_log.debug(
        f"{__name__}->{students_in_attendance_sheet.__name__} {response.__dict__}")

    return response


@attendance_sheet_student_registration_swagger
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@log_operations_time
@log_and_catch_view((Exception, "Erro ao registar-se na aula", HTTP_400_BAD_REQUEST))
def attendance_sheet_student_registration(request, sheet_id):
    """
    Register a user in an attendance sheet
    :param request: Http Request
    :param sheet_id: Attendance sheet's ID
    :return: Operations status wrapped on response's object
    """
    user = request.user
    token = get_token(user)

    student_registration_serializer = StudentSerializer(data=request.data)

    if not student_registration_serializer.is_valid():
        return serializer_not_valid_response(student_registration_serializer,
                                             attendance_sheet_student_registration.__name__)

    _, success, errors = attendance_queries.attendance_sheet_student_registration(sheet_id, token,
                                                                                  student_registration_serializer.validated_data)

    status = HTTP_200_OK if len(errors) == 0 else HTTP_400_BAD_REQUEST

    response = create_response(
        token=token, success=success, errors=errors, status=status)
    general_log.debug(
        f"{__name__}->{attendance_sheet_student_registration.__name__} {response.__dict__}")

    return response


@attendance_sheet_student_deletion_swagger
@csrf_exempt
@api_view(["DELETE"])
@log_operations_time
@log_and_catch_view((Exception, "Erro ao eliminar registo(s) de aluno(s)", HTTP_400_BAD_REQUEST))
def attendance_sheet_student_deletion(request, sheet_id):
    """
    Remove a student from an attendance sheet
    :param request: Http Request
    :param sheet_id: Attendance sheet's ID
    :return: Operations status wrapped on response's object
    """
    user = request.user
    token = get_token(user)

    student_registration_serializer = StudentNmecSerializer(data=request.data)

    if not student_registration_serializer.is_valid():
        return serializer_not_valid_response(student_registration_serializer,
                                             attendance_sheet_student_registration.__name__, token)

    _, success, errors = attendance_queries.attendance_sheet_student_deletion(user, sheet_id,
                                                                              student_registration_serializer.validated_data)

    status = HTTP_200_OK if len(errors) == 0 else HTTP_400_BAD_REQUEST

    response = create_response(
        token=token, success=success, errors=errors, status=status)
    general_log.debug(
        f"{__name__}->{attendance_sheet_student_deletion.__name__} {response.__dict__}")

    return response


@attendance_sheets_swagger
@csrf_exempt
@api_view(["GET"])
@log_operations_time
@log_and_catch_view((Exception, "Erro ao obter as folhas de presença", HTTP_400_BAD_REQUEST))
def attendance_sheets(request, course_id):
    """
    Get all attendances of a user in a given CourseUnit
    :param request: Http Request
    :param course_id: Course unit's ID
    :return: Attendances data and operations status wrapped on response's object
    """
    user = request.user
    token = get_token(user)

    data, success, errors = attendance_queries.attendance_sheets(
        user, course_id)
    status = HTTP_200_OK if len(errors) == 0 else HTTP_400_BAD_REQUEST

    data = {"course_unit": course_id,
            "attendances": AttendanceSimpleSerializer(data, many=True).data}

    response = create_response(
        data=data, success=success, errors=errors, status=status, token=token)
    general_log.debug(
        f"{__name__}->{attendance_sheets.__name__} {response.__dict__}")

    return response


@attendance_info_swagger
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
@log_operations_time
@log_and_catch_view((Exception, "Erro ao obter as informações da folha de presenças", HTTP_400_BAD_REQUEST))
def attendance_info(request, sheet_id):
    """
    Get attendance info
    :param request: Http Request
    :param sheet_id: Sheet's ID
    :return: Sheet data and operations status wrapped on response's object
    """
    user = request.user
    token = get_token(user)

    data, success, errors = attendance_queries.attendance_info(sheet_id)
    query_status = len(errors) == 0

    status = HTTP_200_OK if query_status else HTTP_400_BAD_REQUEST

    response = create_response(
        data=data, success=success, errors=errors, status=status, token=token)
    general_log.debug(
        f"{__name__}->{attendance_info.__name__} {response.__dict__}")

    return response
