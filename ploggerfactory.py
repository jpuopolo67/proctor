import plogger

class ProctorLoggerFactory:
    """Supplies the application with a configured logger."""

    # I separated out the logger factory from the logger itself because it broke a thorny
    # import dependency cycle.

    _the_logger = None
    _logger_name = None
    _console_log_level = None
    _proctor_working_dir = None
    _logfile_name = None

    @staticmethod
    def init(logger_name, console_log_level, proctor_working_dir, logfile_name):
        """Initializes the factory with various logging information.
        :param logger_name: Name of the logger
        :param console_log_level: Log threshold for the console. Higher thresholds mean less verbosity in console.
        Note all output is logged to the log file, separate from the console.
        :param proctor_working_dir: Name of Proctor's working directory, where all the action happens
        :param logfile_name: Name of the log file where all log messages are captured. May be None, which means
        that there is no log file specified."""
        ProctorLoggerFactory._logger_name = logger_name
        ProctorLoggerFactory._console_log_level = console_log_level
        ProctorLoggerFactory._proctor_working_dir = proctor_working_dir
        ProctorLoggerFactory._logfile_name = logfile_name

    @staticmethod
    def getLogger():
        """Returns the configured logger.
        :returns The configure logger."""

        # The logger is a singleton
        if ProctorLoggerFactory._the_logger:
            return ProctorLoggerFactory._the_logger

        # Create and initialize the logger
        ProctorLoggerFactory._the_logger = plogger.ProctorLogger(ProctorLoggerFactory._logger_name,
                                           ProctorLoggerFactory._console_log_level,
                                           ProctorLoggerFactory._proctor_working_dir,
                                           ProctorLoggerFactory._logfile_name)
        return ProctorLoggerFactory._the_logger



