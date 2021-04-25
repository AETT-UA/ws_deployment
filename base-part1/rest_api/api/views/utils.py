from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from logs import general_log


class BadArguments(BaseException):
	pass


def create_response(token=None, success=None, errors=None, data=None, status=HTTP_200_OK) -> Response:
	if success and type(success) is not list:
		raise BadArguments("Success argument  should be a list")
	if errors and type(errors) is not list:
		raise BadArguments("Errors argument  should be a list")

	success = [] if not success else success
	data = [] if not data else data
	errors = [] if not errors else errors

	return Response({
		'token': token,
		'success': success,
		'errors': errors,
		'data': data
	}, status=status)


def serializer_not_valid_response(serializer, function_name: str, token=None) -> Response:
	error_msg = f"O serializer do <{function_name}> teve os seguintes erros - > {serializer.errors}"
	general_log.error(f"{__name__} -> {function_name}  {error_msg}")
	errors = [f"{field_name} -> {error[0]}" for field_name, error in serializer.errors.items()]
	return create_response(errors=errors, status=HTTP_400_BAD_REQUEST, token=token)
