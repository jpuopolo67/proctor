
from gitlabconfig import GitLabConfiguration
from gitlabserver import GitLabServer
from gitlabuser import GitLabUser
import argparse
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


    def __init__(self, server, user, working_dir, app_logger):
        """Initizlies the Proctor"""
        self._server = server
        self._user = user
        self._working_dir_name = working_dir
        self._argparser = argparse.ArgumentParser()
        self._init_args()
        self._server.login(self._user)


    def _init_args(self):
        """Helper method that initializes initializes program args"""
        self._argparser.add_argument("cmd", help="command for Proctor to execute: clone (initgb, grade, regrade)")
        self._argparser.add_argument("--project", help="name of the assignment, lab or project")
        self._argparser.add_argument("--emails", help="path to text file containing student emails")
        self._argparser.add_argument("--force", help="force overwrite of existing directory or data", action="store_true")
        self._args = self._argparser.parse_args()
        self._argsdict = vars(self._args)


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

    cfg = GitLabConfiguration()
    server = GitLabServer(cfg.get_server_url())
    user = GitLabUser(cfg.get_user_private_token())
    working_dir = cfg.get_proctor_working_dir()
    app_logger = applogger.AppLogger("proctor-logger", "INFO")

    # Proctor
    p = Proctor(server, user, working_dir, app_logger)
    p.process_command()


