from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from api.serializers import AttendanceSerializer, AttendanceStatusSerializer, StudentNmecSerializer, StudentSerializer
from swagger.utils import ResponseSerializer


def course_units_swagger(view):
    description = "Create an attendance_sheet"
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": "486d0c6c03d0d26b6173d17a681bb07001e8c2a8",
            "success": [
                "Cadeiras obtidas com sucesso"
            ],
            "errors": [],
            "data": [
                {
                    "id": 0,
                    "name": "PI"
                },
                {
                    "id": 1,
                    "name": "MAS"
                },
                {
                    "id": 2,
                    "name": "ITW"
                },
                {
                    "id": 3,
                    "name": "TPW"
                }
            ]
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": "486d0c6c03d0d26b6173d17a681bb07001e8c2a8",
            "success": [],
            "errors": [
                "Erro ao obter todas as cadeiras"
            ],
            "data": []
        }
    })
    return swagger_auto_schema(
        method='get',
        operation_summary=description,
        operation_description=description,
        responses={200: success_response, 400: bad_response}
    )(view)


def create_attendance_sheet_swagger(view):
    description = "Create an attendance_sheet"
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": "5c0f7483a931b8a599d6ae71e3b1bbb7cb1483f7",
            "success": [
                "Folha de presenças criada com sucesso"
            ],
            "errors": [],
            "data": {
                "attendance_id": "arQXBs"
            }
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": "ae088506cdb1976db1ba6544798c96158be4b191",
            "success": [],
            "errors": [
                "Cadeira selecionada não existe"
            ],
            "data": []
        }
    })
    return swagger_auto_schema(
        method='post',
        operation_summary=description,
        operation_description=description,
        request_body=AttendanceSerializer,
        responses={200: success_response, 400: bad_response}
    )(view)


def attendance_status_swagger(view):
    description = "Change the activation status of an attendance sheet"
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": "e5f71fc5600549441584ae438257efd03b2db15b",
            "success": [
                "Estado da folha de presenças mudado com sucesso"
            ],
            "errors": [],
            "data": []
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": "e5f71fc5600549441584ae438257efd03b2db15b",
            "success": [],
            "errors": [
                "Folha de presenças não existe"
            ],
            "data": []
        }
    })

    unauthorized_response = openapi.Response('Unauthorized response', ResponseSerializer, examples={
        'application/json': {
            "token": "dd24d17253dad6b4f8903d4dca8a66d602420b17",
            "success": [],
            "errors": [
                "Apenas o criador desta folha de presenças pode mudar o estado da mesma"
            ],
            "data": []
        }
    })
    return swagger_auto_schema(
        method='post',
        operation_summary=description,
        operation_description=description,
        request_body=AttendanceStatusSerializer,
        responses={200: success_response, 400: bad_response, 401: unauthorized_response}
    )(view)


def students_in_attendance_sheet_swagger(view):
    description = "Get students registered on an attendance sheet"
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": "e5ebc189e5501b240f1604bbfe13c10bc82512f4",
            "success": [
                "Alunos registados na folha de presença obtidos com sucesso"
            ],
            "errors": [],
            "data": [
                {
                    "nmec": 80028,
                    "name": "80028",
                    "timestamp": "2020-10-08T21:52:46.225370Z"
                },
                {
                    "nmec": 80029,
                    "name": "80029",
                    "timestamp": "2020-10-08T21:52:46.238218Z"
                },
                {
                    "nmec": 80218,
                    "name": "80218",
                    "timestamp": "2020-10-08T21:52:46.624520Z"
                },
                {
                    "nmec": 80279,
                    "name": "80279",
                    "timestamp": "2020-10-08T21:52:46.723406Z"
                },
                {
                    "nmec": 80431,
                    "name": "80431",
                    "timestamp": "2020-10-08T21:52:45.847875Z"
                },
                {
                    "nmec": 80439,
                    "name": "80439",
                    "timestamp": "2020-10-08T21:52:45.900321Z"
                },
                {
                    "nmec": 80531,
                    "name": "80531",
                    "timestamp": "2020-10-08T21:52:46.175050Z"
                },
                {
                    "nmec": 80962,
                    "name": "80962",
                    "timestamp": "2020-10-08T21:52:45.924982Z"
                },
                {
                    "nmec": 81123,
                    "name": "81123",
                    "timestamp": "2020-10-08T21:52:46.374496Z"
                },
                {
                    "nmec": 81329,
                    "name": "81329",
                    "timestamp": "2020-10-08T21:52:46.776467Z"
                }
            ]
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": "e9f356ce39a492f976902fe706ad147f7e637484",
            "success": [],
            "errors": [
                "Apenas o criador desta folha pode obter os alunos registados na mesma"
            ],
            "data": []
        }
    })

    unauthorized_response = openapi.Response('Unauthorized response', ResponseSerializer, examples={
        'application/json': {
            "token": "dd24d17253dad6b4f8903d4dca8a66d602420b17",
            "success": [],
            "errors": [
                "Apenas o criador desta folha pode obter os alunos registados na mesma"
            ],
            "data": []
        }
    })
    return swagger_auto_schema(
        method='get',
        operation_summary=description,
        operation_description=description,
        responses={200: success_response, 400: bad_response, 401: unauthorized_response}
    )(view)


def attendance_sheet_student_registration_swagger(view):
    description = "Register a user in an attendance sheet"
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": None,
            "success": [
                "Aluno com nº mec 88984 registado com sucesso na folha de presenças"
            ],
            "errors": [],
            "data": []
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": None,
            "success": [],
            "errors": [
                "A folha de presenças encontra-se encerrada. Não é possivel submeter o registo"
            ],
            "data": []
        }
    })
    return swagger_auto_schema(
        method='post',
        operation_summary=description,
        operation_description=description,
        request_body=StudentSerializer,
        responses={200: success_response, 400: bad_response}
    )(view)


def attendance_sheet_student_deletion_swagger(view):
    description = "Remove a student from an attendance sheet"
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": "d87d795d314c35d937aa0947e0c46c0ab0540890",
            "success": [
                "Registo(s) de aluno(s) eliminados com sucesso"
            ],
            "errors": [],
            "data": []
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": "d87d795d314c35d937aa0947e0c46c0ab0540890",
            "success": [],
            "errors": [
                "Folha de presenças não existe"
            ],
            "data": []
        }
    })
    return swagger_auto_schema(
        method='delete',
        operation_summary=description,
        operation_description=description,
        request_body=StudentNmecSerializer,
        responses={200: success_response, 400: bad_response}
    )(view)


def attendance_sheets_swagger(view):
    description = "Get UC and users' attendance schedules"
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": "486d0c6c03d0d26b6173d17a681bb07001e8c2a8",
            "success": [
                "Folhas de presença obtidas com sucesso"
            ],
            "errors": [],
            "data": {
                "course_unit": "0",
                "attendances": [
                    {
                        "id": 1,
                        "register_timestamp": "2020-09-29T10:29:39.394960Z"
                    },
                    {
                        "id": 2,
                        "register_timestamp": "2020-09-29T10:40:09.846346Z"
                    }
                ]
            }
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": "486d0c6c03d0d26b6173d17a681bb07001e8c2a8",
            "success": [],
            "errors": [
                "Erro ao obter as folhas de presença"
            ],
            "data": []
        }
    })
    return swagger_auto_schema(
        method='get',
        operation_summary=description,
        operation_description=description,
        responses={200: success_response, 400: bad_response}
    )(view)


def attendance_info_swagger(view):
    description = ""
    success_response = openapi.Response('Success response', ResponseSerializer, examples={
        'application/json': {
            "token": None,
            "success": [
                "Folha de presenças obtido com sucesso"
            ],
            "errors": [],
            "data": {
                "timestamp": "2020-09-30T15:07:54.303193Z",
                "course_unit_name": "MAS",
                "creator_name": "professor1 DETI",
                "is_active": True
            }
        }
    })

    bad_response = openapi.Response('Error response', ResponseSerializer, examples={
        'application/json': {
            "token": "e85ce7a5d2b242f915fcd6080a1e4b72bd74b9da",
            "success": [],
            "errors": [
                "Folha de presenças não existe"
            ],
            "data": []
        }
    })
    return swagger_auto_schema(
        method='get',
        operation_summary=description,
        operation_description=description,
        responses={200: success_response, 400: bad_response}
    )(view)
