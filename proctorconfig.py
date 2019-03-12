import os
import configparser
from pathlib import Path


class ProctorConfig:
    """Manages Proctor's configuration file."""

    DEFAULT_CONFIG_FILE: str = '.proctor.cfg'
    CONFIG = configparser.ConfigParser()


    @staticmethod
    def init(config_file_path=None):
        """Initializes the configuration based on the .proctor.cfg file."""
        config_file = ProctorConfig._get_config_file_path(config_file_path)
        ProctorConfig.CONFIG.read(config_file)


    @staticmethod
    def _get_config_file_path(config_file_path):
        """Find the path to Proctor's configuration file."""

        # If the caller supplied the config file, return it right away
        if config_file_path is not None:
            return config_file_path

        # Check the current working directory
        cfg_file_path = Path(os.sep.join([os.getcwd(), ProctorConfig.DEFAULT_CONFIG_FILE]))
        if Path.exists(cfg_file_path):
            return cfg_file_path

        # Check the currently logged in user's directory
        cfg_file_path = Path(os.sep.join([os.path.expanduser('~'),
                                       ProctorConfig.DEFAULT_CONFIG_FILE]))
        if Path.exists(cfg_file_path):
            return cfg_file_path

        # No configuration file found. We can't run!
        raise FileNotFoundError("Cannot find the configuration file '{}' in the current "
                                "working directory or your home directory.".format(
                                ProctorConfig.DEFAULT_CONFIG_FILE))


    @staticmethod
    def get_proctor_working_dir():
        """Returns where Proctor writes logs, clones git projects, etc."""
        working_dir = ProctorConfig.get_config_value('Proctor', 'working_dir')
        if working_dir.endswith(os.sep):
            working_dir = working_dir[:-1]
        return working_dir


    @staticmethod
    def get_config_value(section, key):
        try:
            value = ProctorConfig.CONFIG.get(section, key)
        except:
            value = None
        return value


