
from gitlabconfig import GitLabConfiguration
from gitlabserver import GitLabServer
from gitlabuser import GitLabUser
import argparse
import sys
from pprint import pprint as pp


class Proctor:

    _valid_cmds = ('clone', )
    _required_opts = {'clone': {'project', 'emails'}}

    @staticmethod
    def build_dest_path_name(working_dir, email, project_name):
        owner_dir_name = GitLabServer.build_project_path(email, project_name)
        dest_path_name = str.format("{}/{}", working_dir, owner_dir_name)
        return dest_path_name

    def __init__(self, server, user, working_dir):
        self._server = server
        self._user = user
        self._working_dir_name = working_dir
        self._argparser = argparse.ArgumentParser()
        self._init_args()
        self._server.login(self._user)

    def _init_args(self):
        self._argparser.add_argument("cmd", help="command for Proctor to execute: clone (initgb, grade, regrade)")
        self._argparser.add_argument("--project", help="name of the assigment, lab or project")
        self._argparser.add_argument("--emails", help="path to text file containing student emails")
        self._argparser.add_argument("--force", help="force overwrite of existing directory or data", action="store_true")
        self._args = self._argparser.parse_args()
        self._argsdict = vars(self._args)

    def _are_args_valid(self):
        # Make sure the command is one that we accept and can process
        cmd = self._args.cmd
        if cmd not in Proctor._valid_cmds:
            return False

        # Make sure the required options are present for the given command
        cmd = self._argsdict["cmd"]
        for opt in Proctor._required_opts[cmd]:
            if opt not in self._argsdict.keys() or self._argsdict[opt] is None:
                return False
        return True

    def process_command(self):
        if not self._are_args_valid():
            print("Invalid command or incompatible options selected. Please try again.")
            sys.exit(0)

        cmd = self._argsdict["cmd"]
        if cmd == 'clone':
            self._clone()

    def _clone(self):
        """Clones one or more projects from the GitLab server."""

        # Get the list of project owners to clone
        email_file = self._argsdict["emails"]
        owner_emails = GitLabUser.get_emails(email_file)

        # Convenience variable
        project_name = self._argsdict["project"]

        # Clone 'em
        force = self._args.force == True
        for email in owner_emails:
            gitlab_project = self._server.get_user_project(email, project_name)
            dest_path_name = Proctor.build_dest_path_name(self._working_dir_name, email, project_name)
            self._server.clone_project(gitlab_project, dest_path_name, force)



if __name__ == "__main__":

    cfg = GitLabConfiguration()
    server = GitLabServer(cfg.get_server_url())
    user = GitLabUser(cfg.get_user_private_token())
    working_dir = cfg.get_proctor_working_dir()

    # Proctor
    p = Proctor(server, user, working_dir)
    p.process_command()


