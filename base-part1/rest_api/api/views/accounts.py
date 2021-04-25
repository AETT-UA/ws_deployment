from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from api.serializers import LoginSerializer, UserSerializer, change_serializer_to_non_required, PasswordEditSerializer
from api.views.utils import serializer_not_valid_response, create_response
from logs import general_log
from logs.logs_decorator import log_operations_time, log_and_catch_view
from rest.queries import accounts as accounts_queries
from rest.queries.utils import get_token
from swagger.accounts import login_swagger, register_swagger, profile_swagger, edit_profile_swagger, \
    edit_password_swagger, logout_swagger


@login_swagger
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@log_operations_time
@log_and_catch_view((Exception, "Erro ao fazer login!", HTTP_400_BAD_REQUEST))
def login(request):
    """
    POST request to make login
    :param request: Http Request
    :return: User logged in info wrapped on response's object
    """
    login_serializer = LoginSerializer(data=request.data)

    if not login_serializer.is_valid():
        return serializer_not_valid_response(login_serializer, login.__name__)

    data, success, errors = accounts_queries.login(login_serializer.validated_data)
    query_status = len(errors) == 0

    status_code = HTTP_200_OK if query_status else HTTP_400_BAD_REQUEST
    token = data.get('token') if query_status else None
    data = {'user': UserSerializer(data.get('user'), ignore_fields=["password"]).data} if query_status else None

    response = create_response(token=token, success=success, errors=errors, data=data, status=status_code)
    general_log.debug(f"{__name__}->{login.__name__} {response.__dict__}")

    return response


@register_swagger
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@log_operations_time
@log_and_catch_view(
    (Exception, "Erro ao registar novo utilizador!", HTTP_400_BAD_REQUEST)
)
def register(request):
    """
    POST request to register new user
    :param request: Http Request
    :return: error or success messages and status code
    """
    user_serializer = UserSerializer(data=request.data)
    data = []

    if not user_serializer.is_valid():
        return serializer_not_valid_response(user_serializer, register.__name__)

    query_data, success, errors = accounts_queries.register(user_serializer.validated_data)
    query_status = len(errors) == 0

    status_code = HTTP_200_OK if query_status else HTTP_400_BAD_REQUEST

    if query_status:
        data = UserSerializer(query_data.get('user'), ignore_fields=['password']).data
    token = query_data.get('token')

    response = create_response(data=data, token=token, success=success, errors=errors,
                               status=status_code)
    general_log.debug(f"{__name__}->{register.__name__} {response.__dict__}")

    return response


@profile_swagger
@csrf_exempt
@api_view(["GET"])
@log_operations_time
@log_and_catch_view((Exception, "Erro ao obter o perfil do utilizador", HTTP_400_BAD_REQUEST))
def profile(request):
    """
    Get user profile data
    :param request: Http Request
    :return: User profile data  wrapped on response's object
    """
    success, errors = [], []
    user = request.user

    data = UserSerializer(user, ignore_fields=['password']).data

    response = create_response(data=data, success=success, errors=errors, status=HTTP_200_OK, token=get_token(user))
    general_log.debug(f"{__name__}->{profile.__name__} {response.__dict__}")

    return response


@edit_profile_swagger
@csrf_exempt
@api_view(["PUT"])
@log_operations_time
@log_and_catch_view((Exception, "Erro ao editar o perfil do utilizador", HTTP_400_BAD_REQUEST))
def edit_profile(request):
    """
    PUT request to update an user
    :param request: Http Request
    :return: error or success messages and status code
    """
    user = request.user
    token = get_token(user)
    data = []

    user_serializer = change_serializer_to_non_required(UserSerializer(data=request.data))

    if not user_serializer.is_valid():
        return serializer_not_valid_response(user_serializer, edit_profile.__name__, token=token)

    query_data, success, errors = accounts_queries.edit_profile(user, user_serializer.validated_data)
    query_status = len(errors) == 0

    if query_status:
        data = UserSerializer(query_data.get('user'), ignore_fields=['password']).data
    status = HTTP_200_OK if query_status else HTTP_400_BAD_REQUEST

    response = create_response(data=data, success=success, errors=errors, status=status, token=token)
    general_log.debug(f"{__name__}->{edit_profile.__name__} {response.__dict__}")

    return response


@edit_password_swagger
@csrf_exempt
@api_view(["PUT"])
@log_operations_time
@log_and_catch_view((Exception, "Erro ao editar a palavra passe do utilizador", HTTP_400_BAD_REQUEST))
def edit_password(request):
    """
    PUT request to update an user password
    :param request: Http Request
    :return: error or success messages and status code
    """
    user = request.user
    token = get_token(user)

    password_edit_serializer = PasswordEditSerializer(data=request.data)

    if not password_edit_serializer.is_valid():
        return serializer_not_valid_response(password_edit_serializer, edit_password.__name__, token)

    _, success, errors = accounts_queries.edit_password(user, password_edit_serializer.validated_data)

    status = HTTP_200_OK if len(errors) == 0 else HTTP_400_BAD_REQUEST

    response = create_response(token=token, success=success, errors=errors, status=status)
    general_log.debug(f"{__name__}->{edit_password.__name__} {response.__dict__}")

    return response


@logout_swagger
@csrf_exempt
@api_view(["GET"])
@log_operations_time
@log_and_catch_view((Exception, "Erro ao fazer logout!", HTTP_400_BAD_REQUEST))
def logout(request):
    """
    Deletes the token associated with that user
    :param request: Who has made the request
    :return: Error or success messages and status code
    """
    data, success, errors = accounts_queries.logout(request.auth.key)

    response = create_response(success=success, status=HTTP_200_OK)
    general_log.debug(f"{__name__}->{logout.__name__} {response.__dict__}")

    return response
