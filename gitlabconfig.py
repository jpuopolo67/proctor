import os
import configparser
from pathlib import Path


class GitLabConfiguration:
    """Manages Proctor's configuration file."""

    _DEFAULT_CONFIG_FILE: str = '.proctor.cfg'

    def __init__(self, config_file_path=None):
        """Initializes the configuration based on the .proctor.cfg file."""
        self._config_file = self._get_config_file_path(config_file_path)
        self._cfg = configparser.ConfigParser()
        self._cfg.read(self._config_file)

    def _get_config_file_path(self, config_file_path):
        """Find the path to Proctor's configuration file."""

        # If the caller supplied the config file, return it right away
        if config_file_path is not None:
            return config_file_path

        # Check the current working directory
        cfg_file_path = Path('/'.join([os.getcwd(), GitLabConfiguration._DEFAULT_CONFIG_FILE]))
        if Path.exists(cfg_file_path):
            return cfg_file_path

        # Check the currently logged in user's directory
        cfg_file_path = Path('/'.join([os.path.expanduser('~'),
                                       GitLabConfiguration._DEFAULT_CONFIG_FILE]))
        if Path.exists(cfg_file_path):
            return cfg_file_path

        # No configuration file found. We can't run!
        raise FileNotFoundError("Cannot find the configuration file '{}' in the current "
                                "working directory or your home directory.".format(
                                GitLabConfiguration._DEFAULT_CONFIG_FILE))

    def get_proctor_working_dir(self):
        """Returns where Proctor writes logs, clones git projects, etc."""
        # Make sure the working dir path ends in / to properly indicate a directory
        working_dir = self.get_config_value('Proctor', 'working_dir')
        if not working_dir.endswith(os.sep):
            working_dir = working_dir + os.sep
        return working_dir

    def get_config_value(self, section, key):
        try:
            value = self._cfg.get(section, key)
        except:
            value = None
        return value



