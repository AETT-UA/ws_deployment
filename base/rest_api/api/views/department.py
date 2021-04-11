from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from api.serializers import DepartmentSerializer, CourseUnitSerializer
from api.views.utils import create_response
from logs import general_log
from logs.logs_decorator import log_operations_time, log_and_catch_view
from rest.queries.utils import get_token
from rest.queries import department as department_queries
from swagger.department import all_departments_swagger, course_units_by_department_swagger


@all_departments_swagger
@csrf_exempt
@api_view(["GET"])
@log_operations_time
@permission_classes((AllowAny,))
@log_and_catch_view((Exception, "Erro ao todos os departamentos", HTTP_400_BAD_REQUEST))
def all_departments(request):
    """
    Get all departments
    :param request: Http Request
    :return: Departments data wrapped on response's object
    """
    user = request.user
    token = get_token(user)
    data, success, errors = department_queries.all_departments()

    data = DepartmentSerializer(data, many=True).data

    status = HTTP_200_OK if len(errors) == 0 else HTTP_400_BAD_REQUEST

    response = create_response(data=data, success=success, errors=errors, status=status,
                               token=token)
    general_log.debug(f"{__name__}->{all_departments.__name__} {response.__dict__}")

    return response


@course_units_by_department_swagger
@csrf_exempt
@api_view(["GET"])
@log_operations_time
@permission_classes((AllowAny,))
@log_and_catch_view((Exception, "Erro ao todas as unidades curriculares por departamento", HTTP_400_BAD_REQUEST))
def course_units_by_department(request, department_id: int):
    """
    Get all course units per department
    :param request: Http Request
    :param department_id: Department id
    :return: Curricular units data wrapped on response's object
    """
    user = request.user
    token = get_token(user)
    data, success, errors = department_queries.course_units_by_department(department_id)

    data = CourseUnitSerializer(data, many=True).data

    status = HTTP_200_OK if len(errors) == 0 else HTTP_400_BAD_REQUEST

    response = create_response(data=data, success=success, errors=errors, status=status,
                               token=token)
    general_log.debug(f"{__name__}->{course_units_by_department.__name__} {response.__dict__}")

    return response
