from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from api.models import CourseUnit
from api.serializers import DepartmentSerializer
from swagger.utils import ResponseSerializer


def all_departments_swagger(view):
	description = "Get all departments"
	success_response = openapi.Response('Success response', ResponseSerializer, examples={
		'application/json': {
			"token": "5c0f7483a931b8a599d6ae71e3b1bbb7cb1483f7",
			"success": [
				"Departamentos obtidos com sucesso"
			],
			"errors": [],
			"data": [
				{
					"id": 4,
					"name": "Departamento de Eletrónica, Telecomunicações e Informática",
					"initials": "DETI"
				}
			]
		}
	})

	bad_response = openapi.Response('Error response', ResponseSerializer, examples={
		'application/json': {
			"token": "ae088506cdb1976db1ba6544798c96158be4b191",
			"success": [],
			"errors": [
				"Erro ao obter todos os departamentos"
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


def course_units_by_department_swagger(view):
	description = "Get course units per department"
	success_response = openapi.Response('Success response', ResponseSerializer, examples={
		'application/json': {
			"token": "5c0f7483a931b8a599d6ae71e3b1bbb7cb1483f7",
			"success": [
				"Unidades curriculares obtidas com sucesso"
			],
			"errors": [],
			"data": [
				{
					"id": 0,
					"name": "PI",
					"department": 4
				},
				{
					"id": 1,
					"name": "MAS",
					"department": 4
				},
				{
					"id": 2,
					"name": "ITW",
					"department": 4
				},
				{
					"id": 3,
					"name": "TPW",
					"department": 4
				}
			]
		}
	})

	bad_response = openapi.Response('Error response', ResponseSerializer, examples={
		'application/json': {
			"token": "ae088506cdb1976db1ba6544798c96158be4b191",
			"success": [],
			"errors": [
				"Erro ao obter todas as unidades curriculares por departamento"
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
