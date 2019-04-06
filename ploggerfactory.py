
import plogger

class ProctorLoggerFactory:

    _the_logger = None
    _logger_name = None
    _console_log_level = None
    _proctor_working_dir = None
    _logfile_name = None

    @staticmethod
    def init(logger_name, console_log_level, proctor_working_dir, logfile_name):
        ProctorLoggerFactory._logger_name = logger_name
        ProctorLoggerFactory._console_log_level = console_log_level
        ProctorLoggerFactory._proctor_working_dir = proctor_working_dir
        ProctorLoggerFactory._logfile_name = logfile_name

    @staticmethod
    def getLogger():
        if ProctorLoggerFactory._the_logger:
            return ProctorLoggerFactory._the_logger
        ProctorLoggerFactory._the_logger = plogger.ProctorLogger(ProctorLoggerFactory._logger_name,
                                           ProctorLoggerFactory._console_log_level,
                                           ProctorLoggerFactory._proctor_working_dir,
                                           ProctorLoggerFactory._logfile_name)
        return ProctorLoggerFactory._the_logger



