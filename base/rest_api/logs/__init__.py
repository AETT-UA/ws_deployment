import logging
from pathlib import Path

from constants import BASE_LOGS_PATH


def generate_log(logger_name=__name__, file_path=f"{BASE_LOGS_PATH}/example.log"):
	Path(BASE_LOGS_PATH).mkdir(parents=True, exist_ok=True)
	log = logging.getLogger(logger_name)
	if not log.hasHandlers():
		log.setLevel(logging.DEBUG)

		handler = logging.FileHandler(file_path)
		handler.setLevel(logging.DEBUG)

		formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		handler.setFormatter(formatter)

		log.addHandler(handler)
	return log


general_log = generate_log(logger_name="general", file_path=f"{BASE_LOGS_PATH}/general.log")
exceptions_log = generate_log(logger_name="exceptions", file_path=f"{BASE_LOGS_PATH}/exceptions.log")
operation_time_log = generate_log(logger_name="operation_time", file_path=f"{BASE_LOGS_PATH}/operation_time.log")
