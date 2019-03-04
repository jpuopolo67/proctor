
from gitlabconfig import GitLabConfiguration
from gitlabserver import GitLabServer
from gitlabuser import GitLabUser
import argparse
import plogger
import sys
import os
from datetime import datetime as dt
from pathlib import Path


class Proctor:
    """Proctor enables WIT instuctors to clone, build, test and grade assignments, labs, and
    projects. It makes the WIT instructor's life a dream. Proctor assumes the projects are test
    are written in Java and use JUnit3 as the testing framework. Future versions of Proctor may
    enable the language-under-test and the unit testing pluggable."""

    _valid_cmds = ('clone', 'grade')
    _required_opts = {'clone': {'project', 'emails'},
                      'grade': {'project', 'emails'}}

    @staticmethod
    def build_dest_path_name(working_dir, email, project_name):
        """Builds a file system path name from component parts.
        :return File system path name."""

        owner_dir_name = GitLabServer.build_server_project_path(project_name, email)
        dest_path_name = os.sep.join([working_dir, project_name, email])
        return dest_path_name

    def __init__(self, cfg):
        """Initializes the Proctor"""
        self._cfg = cfg
        self._init_working_dir()
        self._init_args()
        self._init_server()
        self._init_logger()

        # Log the fact that we're starting
        banner = '=' * 40
        self.logger.info(banner)
        self.logger.info("Proctor")

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
            self.logger.warning("Invalid command or incompatible options selected. Please try again.")
            sys.exit(0)
        cmd = self._argsdict["cmd"]
        if cmd == 'clone':
            self._clone_project()
        elif cmd == 'grade':
            self._grade_project()
        else:
            self.logger.error(f"Unknown command '{cmd}'. Valid commands are: clone, grade")
            sys.exit(0)


    def _grade_project(self):
        """Grades the given project for each email in the specified email file.
        Projects are expected to have been cloned to a local repository previously."""

        owner_emails = self._get_emails_from_file(self._argsdict['emails'])
        project_name = self._argsdict['project']
        project_dir = os.sep.join([self._working_dir_name, project_name])
        project_due_date = self._cfg.get_config_value('Projects', project_name)

        for email in owner_emails:
            dir_to_grade = Path(os.sep.join([project_dir, email]))
            self.logger.info("Attempting to grade: {}".format(dir_to_grade))
            project = self._server.get_user_project(email, project_name)
            if project:
                commits = project.commits.list()
                # Based on examining project commits, it looks like the
                # most recent commit is always the first one in the list.
                if commits:
                    latest_commit_date = commits[0].created_at
                else:
                    self.logger.warning(f'NO COMMIT. Project found but cannot find a commit.')
            else:
                self.logger.warning(f'NOT FOUND: {email}. Project not found. Check email address.')
            self.logger.info("project due: {}, latest_commit: {}".format(project_due_date, latest_commit_date))

            # Calculate time differences and report back in human readable form
            is_ontime, days, hours, mins = self._get_dt_diff_human_readable(project_due_date, latest_commit_date)
            pass

    def _get_dt_diff_human_readable(self, project_due_date, latest_commit_date):

        # Exmaple of project date returned from server: 2019-03-03T23:39:40.000-05:00
        dt_due = dt.strptime(project_due_date, "%Y-%m-%dT%H:%M:%S%z")

        # Remove last : so that strptime can parse correcly
        latest_commit_date = latest_commit_date[::-1].replace(':', '', 1)[::-1]
        dt_latest = dt.strptime(latest_commit_date, "%Y-%m-%dT%H:%M:%S.%f%z")

        # Get the difference and return a tuple in days, hrs, mins
        date_diff = dt_due - dt_latest
        total_sec = date_diff.total_seconds()

        is_ontime = total_sec >= 0
        total_sec = abs(total_sec)
        days, hours, mins = self._convert_secs_to_days_hrs_mins(total_sec)

        return (is_ontime, days, hours, mins)


    def _convert_secs_to_days_hrs_mins(self, total_sec):
        days = total_sec // (24 * 3600)
        total_sec = total_sec % (24 * 3600)
        hours = total_sec // 3600
        total_sec %= 3600
        mins = total_sec // 60
        return (days, hours, mins)


    def _get_emails_from_file(self, email_file):
        """Returns a list of emails from the given file."""
        owner_emails = GitLabUser.get_emails(email_file)
        return owner_emails


    def _clone_project(self):
        """Clones a given project for each email in the specified email file."""
        owner_emails = self._get_emails_from_file(self._argsdict['emails'])
        project_name = self._argsdict['project']

        # Clone 'em
        self.logger.info('Cloning project: {}'.format(project_name))
        force = self._args.force
        for email in owner_emails:
            gitlab_project = self._server.get_user_project(email, project_name)
            if gitlab_project:
                dest_path_name = Proctor.build_dest_path_name(self._working_dir_name, email, project_name)
                self._server.clone_project(gitlab_project, dest_path_name, force)
            else:
                self.logger.warning(f'NOT FOUND: {email}. Check email address.')


if __name__ == "__main__":
    p = Proctor(GitLabConfiguration())
    p.process_command()
    sys.exit(0)
