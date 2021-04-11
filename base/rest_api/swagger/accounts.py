from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from api.serializers import LoginSerializer, UserSerializer, PasswordEditSerializer
from swagger.utils import ResponseSerializer


def login_swagger(view):
    description = 'POST request to make login'

    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": "8a30369c93895d07ecd830fffb8c0d293a70ea15",
            "success": [
                "professor1@ua.pt logado com sucesso!"
            ],
            "errors": [],
            "data": {
                "user": {
                    "first_name": "professor1",
                    "last_name": "DETI",
                    "email": "professor1@ua.pt",
                    "date_joined": "2020-09-26T18:53:51.670086Z"
                }
            }
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": None,
            "success": [],
            "errors": [
                "Credencias para o login inválidas!"
            ],
            "data": []
        }
    })

    return swagger_auto_schema(
        method='post',
        operation_description=description,
        operation_summary=description,
        request_body=LoginSerializer,
        responses={200: success_response, 400: bad_response}
    )(view)


def register_swagger(view):
    description = "POST request to register new user"

    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": "3b5ca38c6b3a887199d04db3e97897c61798f2e7",
            "success": [
                "O utilizador foi criado com sucesso!"
            ],
            "errors": [],
            "data": {
                "email": "rafa223222222@ua.pt",
                "first_name": "xdd",
                "last_name": "waw"
            }
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": None,
            "success": [],
            "errors": [
                "Já existe um utilizador com esse email! O utilizador não foi adicionado à base de dados!"
            ],
            "data": []
        }
    })

    return swagger_auto_schema(
        method='post',
        operation_description=description,
        operation_summary=description,
        request_body=UserSerializer,
        responses={200: success_response, 400: bad_response}
    )(view)


def profile_swagger(view):
    description = ''
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": "4550e6e7aa88db97d8206a11f9280adc72f56103",
            "success": [],
            "errors": [],
            "data": {
                "email": "professor1@ua.pt",
                "first_name": "professor1",
                "last_name": "DETI"
            }
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": "4550e6e7aa88db97d8206a11f9280adc72f56103",
            "success": [],
            "errors": [
                "Erro ao obter o perfil do utilizador"
            ],
            "data": []
        }
    })

    return swagger_auto_schema(
        method='get',
        operation_description=description,
        operation_summary=description,
        responses={200: success_response, 400: bad_response}
    )(view)


def edit_profile_swagger(view):
    description = 'PUT request to update an user (None body field is required)'
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": "218b41c6a696168bec7b4d175363f6c003d9660f",
            "success": [
                "O utilizador foi editado com sucesso!"
            ],
            "errors": [],
            "data": {
                "email": "professor1@ua.pt",
                "first_name": "professor1",
                "last_name": "DETI"
            }
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": "d4c9dcc0bee1ba387621560a884eee35f4cc3b13",
            "success": [],
            "errors": [
                "Já existe um utilizador com esse email! O utlizador não foi editado!"
            ],
            "data": []
        }
    })
    return swagger_auto_schema(
        method='put',
        operation_description=description,
        operation_summary=description,
        request_body=UserSerializer,
        responses={200: success_response, 400: bad_response}
    )(view)


def edit_password_swagger(view):
    description = "PUT request to update an user password"
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": "c4da8a24c5d241350ced201eda76068fbef3457e",
            "success": [
                "Palavra passe atualizada com sucesso"
            ],
            "errors": [],
            "data": []
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": "c4da8a24c5d241350ced201eda76068fbef3457e",
            "success": [],
            "errors": [
                "A palavra passe atual é inválida"
            ],
            "data": []
        }
    })
    return swagger_auto_schema(
        method='put',
        operation_description=description,
        operation_summary=description,
        request_body=PasswordEditSerializer,
        responses={200: success_response, 400: bad_response}
    )(view)


def logout_swagger(view):
    description = "Deletes the token associated with that user"
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": None,
            "success": [
                "Logout efetuado com sucesso!"
            ],
            "errors": [],
            "data": []
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": "9bac56593c101c62023d6662707b92c692cc378d",
            "success": [],
            "errors": [
                "Erro ao fazer logout!"
            ],
            "data": []
        }
    })
    return swagger_auto_schema(
        method='get',
        operation_description=description,
        operation_summary=description,
        responses={200: success_response, 400: bad_response}
    )(view)
