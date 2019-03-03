
from gitlabconfig import GitLabConfiguration
from gitlabserver import GitLabServer
from gitlabuser import GitLabUser
import argparse
import plogger
import sys


class Proctor:
    """Proctor enables WIT instuctors to clone, build, test and grade assignments, labs, and
    projects. It makes the WIT instructor's life a dream. Proctor assumes the projects are test
    are written in Java and use JUnit3 as the testing framework. Future versions of Proctor may
    enable the language-under-test and the unit testing pluggable."""

    _valid_cmds = ('clone', )
    _required_opts = {'clone': {'project', 'emails'}}

    @staticmethod
    def build_dest_path_name(working_dir, email, project_name):
        """Builds a file system path name from component parts.
        :return File system path name."""

        owner_dir_name = GitLabServer.build_project_path(email, project_name)
        dest_path_name ="{}/{}".format(working_dir, owner_dir_name)
        return dest_path_name

    def __init__(self, cfg):
        """Initializes the Proctor"""
        self._cfg = cfg
        self._init_working_dir()
        self._init_args()
        self._init_server()
        self._init_logger()

        # As a final step, log into the server
        self._server.login(self._user)


    def _init_logger(self):
        self.logger = plogger.ProctorLogger('proctor',
                                            self._cfg.get_config_value('Proctor', 'console_log_level'),
                                            self._working_dir_name,
                                            self._cfg.get_config_value('Proctor', 'logfile_name'))


    def _init_working_dir(self):
        self._working_dir_name = self._cfg.get_proctor_working_dir()

    def _init_args(self):
        """Helper method that initializes initializes program args"""
        self._argparser = argparse.ArgumentParser()
        self._argparser.add_argument("cmd", help="command for Proctor to execute: clone (initgb, grade, regrade)")
        self._argparser.add_argument("--project", help="name of the assignment, lab or project")
        self._argparser.add_argument("--emails", help="path to text file containing student emails")
        self._argparser.add_argument("--force", help="force overwrite of existing directory or data", action="store_true")
        self._args = self._argparser.parse_args()
        self._argsdict = vars(self._args)


    def _init_server(self):
        self._server = GitLabServer(self._cfg.get_config_value('GitLabServer', 'url'))
        self._user = GitLabUser(self._cfg.get_config_value('GitLabUser', 'private_token'))


    def _are_args_valid(self):
        """Ensures the program was run with a valid command and valid args supporting that command.
        :return True is all args and switches are valid and compatible."""

        # Valid command?
        cmd = self._args.cmd
        if cmd not in Proctor._valid_cmds:
            return False

        # Required options present for the given command?
        cmd = self._argsdict["cmd"]
        for opt in Proctor._required_opts[cmd]:
            if opt not in self._argsdict.keys() or self._argsdict[opt] is None:
                return False
        return True


    def process_command(self):
        """Process the command entered. This method acts as a junction, dispatching
        calls to appropriate handler functions to complete the work."""
        if not self._are_args_valid():
            print("Invalid command or incompatible options selected. Please try again.")
            sys.exit(0)
        cmd = self._argsdict["cmd"]
        if cmd == 'clone':
            self._clone_projects()


    def _clone_projects(self):
        """Clones one or more projects from the GitLab server."""

        # Get the list of project owners to clone
        email_file = self._argsdict["emails"]
        owner_emails = GitLabUser.get_emails(email_file)

        # Convenience variable
        project_name = self._argsdict["project"]

        # Clone 'em
        force = self._args.force
        for email in owner_emails:
            gitlab_project = self._server.get_user_project(email, project_name)
            dest_path_name = Proctor.build_dest_path_name(self._working_dir_name, email, project_name)
            self._server.clone_project(gitlab_project, dest_path_name, force)


if __name__ == "__main__":
    p = Proctor(GitLabConfiguration())
    p.logger.debug("This is a DEBUG message")
    p.logger.info("This is an INFO message")
    p.logger.warning("This is a WARNING message")
    p.logger.error("This is an ERROR message")
    p.process_command()
    sys.exit(0)
