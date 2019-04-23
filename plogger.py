import logging
import termcolor
import sys
import os
import re
from datetime import datetime as dt


class ProctorLogger:
    """Wraps the standard Python logging module and provides a simplified interface to use
    in the application."""

    @staticmethod
    def _format_msg(msg, threshold=2000, width=40):
        """Used to chop out the middle of a long msg for display purposes.
        :param msg: Message to format
        :param threshold: Message must be this long before chopping will commence
        :param width: The number of characters remaining on the left...right after middle chopped out
        :returns Formatted message, with first and last 'width' characters separated by ellipses."""
        final_msg = msg
        if msg and (len(msg) > threshold):
            left_side = msg[:width]
            right_side = msg[-width:]
            final_msg = '...'.join([left_side, right_side])
        return final_msg

    def __init__(self, logger_name, console_log_level, proctor_working_dir, logfile_name):
        """Initializes ProctorLogger.
        :param logger_name: Unique name of the logger that the entire application uses.
        :param console_log_level: Logging threshold used by the console. The lower the level, e.g., DEBUG, the more output shown on the console.
        :param proctor_working_dir: Directory that serves as the root for cloned projects, gradebook files, etc.
        :param logfile_name: Name of the file to which log output is written."""
        self._logger_name = logger_name

        # Converts the log level string read from the config file into
        # the associated log level integer required by the standard logging module
        self._log_level = None
        try:
            self._log_level = getattr(logging, console_log_level)
            self._logfile_name = None
            if logfile_name is not None and len(logfile_name) > 0:
                self._logfile_name = self._determine_logfile_name(proctor_working_dir, logfile_name)

            # Access proctor logger, set the log level as "DEBUG" to make sure
            # all log messages are forwarded to handlers
            self._thelogger = logging.getLogger('proctor')
            self._thelogger.setLevel(logging.DEBUG)

            # Define formatters and output patterns of the log records
            logfile_formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)8s | %(message)s')
            console_formatter = logging.Formatter('%(message)s')

            # Remove all handlers to that we cleanly install our own based on values from
            # our configuration file
            self._thelogger.handlers = []

            # Now, depending on the specified configuration, add handlers back.
            if self._log_level:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(self._log_level)   # define console's log level in config file
                console_handler.setFormatter(console_formatter)
                self._thelogger.addHandler(console_handler)

            if self._logfile_name is not None:
                file_handler = logging.FileHandler(self._logfile_name)
                file_handler.setLevel(logging.DEBUG)        # all messages logged to the log file
                file_handler.setFormatter(logfile_formatter)
                self._thelogger.addHandler(file_handler)
        except Exception as e:
            termcolor.cprint("Proctor ERROR: Invalid configuration file format or malformed key.", 'red')
            termcolor.cprint(str(e), 'red')
            sys.exit(0)

    # Helpers
    def _determine_logfile_name(self, proctor_working_dir, logfile_name):
        """Determines the logfile name to use, based on the [Proctor] logfile_name key in the configuration
        file. If the logfile name passed contains the pattern YYYYMMDD, this pattern will be replaced by
        today's date, allowing for per diem log files.
        :param proctor_working_dir: Full working directory path name
        :param logfile_name: Name of the logfile name as specified in the configuration file.
        :return Name of the logfile to use"""
        logfile_name = logfile_name.replace("YYYYMMDD", dt.today().strftime('%Y%m%d'))
        logfile_name = os.sep.join([proctor_working_dir, logfile_name])
        return logfile_name

    # Logging wrappers
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
        """Format and log the given message, honoring the specified log level.
        :param msg: Message to log
        :param log_level: Log level threshold, e.g. INFO.
        :param *args: Additional positional parameters, required by standard logger
        :param **kwargs: Additional named parameters, required by standard logger"""
        the_msg = ProctorLogger._format_msg(msg)
        home_dir = os.path.expanduser('~')
        if home_dir in the_msg:
            the_msg = the_msg.replace(home_dir, '~')
        self._thelogger.log(log_level, the_msg, *args, **kwargs)
