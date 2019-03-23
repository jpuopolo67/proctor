from pconfig import ProctorConfig
from gitlabserver import GitLabServer
from gitlabuser import GitLabUser
from grader import Grader
from gradebook import GradeBook
from pathlib import Path
import argparse
import plogger
import sys
import os
import subprocess
import glob
import re


class Proctor:
    """Proctor enables WIT instuctors to clone, build, test and grade assignments, labs, and
    projects. It makes the WIT instructor's life a dream. Proctor assumes the projects are test
    are written in Java and use JUnit3 as the testing framework. Future versions of Proctor may
    enable the language-under-test and the unit testing pluggable."""

    # TODO: Add ability to run JUnit test that outside the project
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

    def __init__(self):
        """Initializes the Proctor"""
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
                                            ProctorConfig.get_config_value('Proctor', 'console_log_level'),
                                            self._working_dir_name,
                                            ProctorConfig.get_config_value('Proctor', 'logfile_name'))

    def _init_working_dir(self):
        self._working_dir_name = ProctorConfig.get_proctor_working_dir()

    def _init_args(self):
        """Helper method that initializes initializes program args"""
        self._argparser = argparse.ArgumentParser()
        self._argparser.add_argument("cmd", help="command for Proctor to execute: clone (initgb, grade, regrade)")
        self._argparser.add_argument("--project", help="name of the assignment, lab or project")
        self._argparser.add_argument("--emails", help="path to text file containing student emails")
        self._argparser.add_argument("--force", help="force overwrite of existing directory or data",
                                     action="store_true")
        self._args = self._argparser.parse_args()
        self._argsdict = vars(self._args)

    def _init_server(self):
        self._server = GitLabServer(ProctorConfig.get_config_value('GitLabServer', 'url'))
        self._user = GitLabUser(ProctorConfig.get_config_value('GitLabUser', 'private_token'))

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

        project_name = self._argsdict['project']
        project_dir = os.sep.join([self._working_dir_name, project_name])
        project_due_dt = ProctorConfig.get_config_value(project_name, 'due_dt')

        gradebook = GradeBook(self._working_dir_name, project_name, project_due_dt)
        grader = Grader(gradebook)

        owner_emails = self._get_emails_from_file(self._argsdict['emails'])
        for email in owner_emails:
            dir_to_grade = Path(project_dir) / email
            self.logger.info('Attempting to grade: {}'.format(dir_to_grade))
            if not dir_to_grade.exists():
                self.logger.warning('NOT FOUND: Target directory {} does not exist. Try clone.'
                                    .format(str(dir_to_grade)))
                gradebook.local_project_not_found(email)
                continue
            project = self._server.get_user_project(email, project_name)
            if project:
                commits = project.commits.list()
                if commits:
                    latest_commit_date = commits[0].created_at  # GitLab returns most recent first (index 0)
                    grader.grade(email, project_name, dir_to_grade, project_due_dt, latest_commit_date)
                else:
                    gradebook.no_commit_found(email)
                    self.logger.warning('NO COMMIT. Project found but cannot find a commit.')
            else:
                gradebook.server_project_not_found(email)
                self.logger.warning('NOT FOUND: Project not found on server. Check email address.')

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
    ProctorConfig.init()
    p = Proctor()

    # <editor-fold desc="Drive code. Delete when completed.">
    # testval = ProctorConfig.get_config_value("Projects", "junit_path")
    #
    # path_name = "/Users/johnpuopolo/Adventure/proctor_wd/pa1-review-student-master/martinezd2@wit.edu"
    # # path_name = "/Users/johnpuopolo/Adventure/proctor_wd/pa1-review-student-master/lockwalds@wit.edu"
    # src_code_path_name = "src/edu/wit/cs/comp1050/"
    # test_code_path_name = src_code_path_name + "tests/"
    #
    # full_path = os.sep.join([path_name, src_code_path_name]) + "*.java"
    # java_files = glob.glob(full_path)
    # p.logger.info("Grading projects")
    #
    # gr = Grader(GradeBook('/Users/johnpuopolo/Adventure/proctor_wd', 'pa1-review-student-master'))
    # gr.grade('martinezd2@wit.edu', 'pa1-review-student-master',
    #          '/Users/johnpuopolo/Adventure/proctor_wd/pa1-review-student-master/martinezd2@wit.edu', None, None)
    #          #'/Users/johnpuopolo/Adventure/proctor_wd/pa1-review-student-master/lockwalds@wit.edu', None, None)
    # gr._gradebook.save()
    # </editor-fold>

    p.process_command()
    sys.exit(0)
