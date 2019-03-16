
import logging
import termcolor
import sys
import os


class ProctorLogger:
    """Wraps the standard Python logging module and provides a simplifed interface to use
    in the Proctor application."""

    @staticmethod
    def _format_msg(msg, threshold=200, width=40):
        final_msg = msg
        if len(msg) > threshold:
            left_side = msg[:width]
            right_side = msg[-width:]
            final_msg = '...'.join([left_side, right_side])
        return final_msg

    def __init__(self, logger_name, console_log_level, proctor_working_dir, logfile_name):
        self._logger_name = logger_name

        # Converts the logging level string read from the config file into
        # the associated integer log level value
        self._log_level = None
        try:
            self._log_level = getattr(logging, console_log_level)
            self._logfile_name = None
            if logfile_name is not None and len(logfile_name) > 0:
                self._logfile_name = os.sep.join([proctor_working_dir, logfile_name])

            # Access proctor logger, set the log level as "DEBUG" to make sure
            # all log messages are forwarded to handlers
            self._thelogger = logging.getLogger('proctor')
            self._thelogger.setLevel(logging.DEBUG)

            # Patterns for the format of log records
            formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)10s | %(message)s')

            # Remove all handlers to that we cleanly install our own based on configuration file
            self._thelogger.handlers = []

            # Now, depending on the specified configuration, add handlers back
            if self._log_level:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(self._log_level)
                console_handler.setFormatter(formatter)
                self._thelogger.addHandler(console_handler)
            if self._logfile_name is not None:
                file_handler = logging.FileHandler(self._logfile_name)
                file_handler.setLevel(logging.DEBUG)    # all messages logged
                file_handler.setFormatter(formatter)
                self._thelogger.addHandler(file_handler)
        except:
            termcolor.cprint("Proctor ERROR: Invalid configuration file format or malformed key.", 'red')
            sys.exit(0)

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
        the_msg = ProctorLogger._format_msg(msg)
        self._thelogger.log(log_level, the_msg, *args, **kwargs)



