import os
import configparser
from pathlib import Path

class GitLabConfiguration:
    """Manages Proctor's configuration file."""

    _DEFAULT_CONFIG_FILE: str = '.proctor.cfg'

    def __init__(self, config_file_path=None):
        """Initializes the configuration based on the .proctor.cfg file."""
        self._config_file = self._get_config_file_path(config_file_path)
        self._load_config_settings_from_file()

    def _get_config_file_path(self, config_file_path):
        """Find the path to Proctor's configuration file."""

        # If the caller supplied the config file, return it right away
        if config_file_path is not None:
            return config_file_path

        # Check the current working directory
        cfg_file_path = Path((os.getcwd() + "/" + GitLabConfiguration._DEFAULT_CONFIG_FILE))
        if Path.exists(cfg_file_path):
            return cfg_file_path

        # Check the currently logged in user's directory
        cfg_file_path = Path((os.path.expanduser('~') + "/" + GitLabConfiguration._DEFAULT_CONFIG_FILE))
        if Path.exists(cfg_file_path):
            return cfg_file_path

        # No configuration file found. We can't run!
        raise FileNotFoundError(str.format(
            "Cannot find the configuration file '{}' in the current working directory or your home directory.",
            GitLabConfiguration._DEFAULT_CONFIG_FILE))

    def _load_config_settings_from_file(self):
        """Reads the configuration file."""
        cfg = configparser.ConfigParser()
        cfg.read(self._config_file)

        self._proctor_working_dir = cfg['Proctor']['working_dir']
        self._gitlab_server_url = cfg['GitLabServer']['url']
        self._gitlab_user_private_token = cfg['GitLabUser']['private_token']


    def get_server_url(self):
        return self._gitlab_server_url

    def get_user_private_token(self):
        return self._gitlab_user_private_token

    def get_proctor_working_dir(self):
        return self._proctor_working_dir


