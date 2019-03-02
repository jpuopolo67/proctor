
import logging
import os
import pathlib

class ProctorLogger:

    def __init__(self, logger_name, log_level, log_to_console, proctor_working_dir, logfile_name):
        self._logger_name = logger_name
        self._log_level = getattr(logging, log_level)
            # converts the string from the config file to the associated
            # numeric value required
        self._log_to_console = log_to_console.lower() == 'true'
        self._logfile_name = proctor_working_dir + logfile_name

        # Access proctor logger and remove all the handlers.
        self._thelogger = logging.getLogger('proctor')
        self._thelogger.setLevel(self._log_level)
        self._thelogger.handlers = []

        # Format of log records
        formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

        # Now, depending on the specified configuration, add handlers back
        if self._log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self._thelogger.addHandler(console_handler)
        if self._logfile_name is not None:
            file_handler = logging.FileHandler(self._logfile_name)
            file_handler.setFormatter(formatter)
            self._thelogger.addHandler(file_handler)

    # Logging wrappers for ease-of-use
    def debug(self, msg, *args, **kwargs):
        return self._log(msg, logging.DEBUG, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return self._log(msg, logging.INFO, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        return self._log(msg, logging.WARNING, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self._log(msg, logging.ERROR, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        return self._log(msg, logging.CRITICAL, *args, **kwargs)

    def _log(self, msg, log_level, *args, **kwargs):
        self._thelogger.log(log_level, msg, *args, **kwargs)
