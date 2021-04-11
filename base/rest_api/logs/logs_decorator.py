import functools
import time

from humanfriendly import format_timespan

from api.views.utils import create_response
from constants.enums import LogType
from logs import exceptions_log, operation_time_log
from rest.queries.utils import get_token


def _log_and_catch(log_type, *args):
	def _view_chain_handler(func, handler_data, *func_args, **func_kwargs):
		exception, error, status_code = handler_data[0]
		try:
			if len(handler_data) == 1:
				return None, func(*func_args, **func_kwargs)
			else:
				return _view_chain_handler(func, handler_data[1:], *func_args, **func_kwargs)
		except exception as exp:
			return exp, create_response(status=status_code, errors=[error], token=get_token(func_args[0].user))

	def _query_chain_handler(func, handler_data, *func_args, **func_kwargs):
		exception, error = handler_data[0]
		try:
			if len(handler_data) == 1:
				return None, func(*func_args, **func_kwargs)
			else:
				return _query_chain_handler(func, handler_data[1:], *func_args, **func_kwargs)
		except exception as exp:
			return exp, ({}, [], [error])

	def decorator(function):
		@functools.wraps(function)
		def wrapper(*function_args, **function_kwargs):
			function_name = function.__name__
			function_module = function.__module__

			if log_type == LogType.VIEW:
				error, return_value = _view_chain_handler(function, list(map(tuple, args))[::-1], *function_args,
														  **function_kwargs)
			else:
				error, return_value = _query_chain_handler(function, list(map(tuple, args))[::-1], *function_args,
														   **function_kwargs)

			if error:
				exceptions_log.exception(f"{function_module}__{function_name} returnou erro -> {error}")
			else:
				exceptions_log.debug(f"{function_module}__{function_name} executou com sucesso")

			return return_value

		return wrapper

	return decorator


def log_and_catch_view(*args):
	"""
	Decorator that silently catches all exceptions and log  the respectively outcome of the function used for views
	:param args: List of objects needed to specify which exceptions is need to catch and their behavior
	(<Exception>,<Error_message>,<status_code>)

	Usage:
	@log_and_catch_view(
	(KeyValueError, "Erro a encontrar a chave", HTTP_400_BAD_REQUEST),
	(Exception, "Erro geral!", HTTP_401_FORBIDDEN),)
	def view(): pass

	Prepara a função para dar catch nas Exception definidas em cima por ordem e
	retorna um  Response com as mensagem de erro e status_code definidos respetivamente.
	E guarda os log_files do estado da função

	Codigo equivalente com try catchs:
	def view():
		try:
			# Some code
		except KeyValueError as error:
			return create_response(status=HTTP_400_BAD_REQUEST, errors=["Erro a encontrar a chave"]

		except Exception as error:
			return create_response(status=HTTP_401_FORBIDDEN, errors=["Erro geral!"]

	"""
	return _log_and_catch(LogType.VIEW, *args)


def log_and_catch_query(*args):
	"""
	Decorator that silently catches all exceptions and log  the respectively outcome of the function used for queries
	:param args: List of objects needed to specify which exceptions is need to catch and their behavior
	(<Exception>,<Error_message>)

	Usage:
	@log_and_catch_view(
	(KeyValueError, "Erro a encontrar a chave"),
	(Exception, "Erro geral!"),)
	def query(): pass

	Prepara a função para dar catch nas Exception definidas em cima por ordem e
	retorna um  Response com as mensagem de erro e status_code definidos respetivamente.
	E guarda os log_files do estado da função

	Codigo equivalente com try catchs:
	def  query():
		try:
			# Some code
		except KeyValueError as error:
			return [],[],["Erro a encontrar a chave"]
		except Exception as error:
			return [],[],["Erro geral!"]
	"""
	return _log_and_catch(LogType.QUERY, *args)


def log_operations_time(function):
	@functools.wraps(function)
	def operations_time(*args, **kwargs):
		function_name = function.__name__
		function_module = function.__module__

		begin_time = time.time()
		return_value = function(*args, **kwargs)
		end_time = time.time() - begin_time

		operation_time_log.debug(
			f'Tempo de execução para {function_module}->{function_name} '
			f'{format_timespan(end_time)} ({end_time} seconds)')

		return return_value

	return operations_time
