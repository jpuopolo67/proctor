#!/usr/bin/env python3

import argparse
import sys
import os
import termcolor
from datetime import datetime as dt
from pathlib import Path
from pconfig import ProctorConfig
from gitlabserver import GitLabServer
from gitlabuser import GitLabUser
from pathmgr import PathManager
from grader import Grader
from gradebook import GradeBook
from builder import Builder
from utrunner import UnitTestRunner
from ploggerfactory import ProctorLoggerFactory
from postman import Postman


class Proctor:
    """Proctor enables WIT instructors to clone, build, test and grade Java-based projects."""

    def __init__(self):
        """Initializes the Proctor"""
        self._init_logger()     # Put as first line in init so that all other
                                # components can access the common logger
        self._init_working_dir()
        self._init_args()
        self._init_server()
        self._server.login(self._user)

    def _init_logger(self):
        """Initializes the Proctor logger."""
        ProctorLoggerFactory.init('proctor',
                                  ProctorConfig.get_config_value('Proctor', 'console_log_level'),
                                  ProctorConfig.get_proctor_working_dir(),
                                  ProctorConfig.get_config_value('Proctor', 'logfile_name'))
        self._logger = ProctorLoggerFactory.getLogger()

    def _init_working_dir(self):
        """Initializes the app's working directory. This is the root of all application operations."""
        self._working_dir_name = ProctorConfig.get_proctor_working_dir()

    def _init_args(self):
        """Helper method that initializes program args."""
        self._argparser = argparse.ArgumentParser()

        # organize the hierarchy of command parsers
        subparsers = self._argparser.add_subparsers()

        # srefresh
        parser_srefresh = subparsers.add_parser('srefresh', help='re-clone and optionally regrade all student projects')
        parser_srefresh.add_argument('--owner', help='email of the person to refresh')
        parser_srefresh.add_argument('--emails', help='path to text file containing all people to refresh')
        parser_srefresh.add_argument('--grade', help='if present, re-grades projects after cloning', action='store_true')

        # config
        parser_config = subparsers.add_parser('config', help='display basic configuration information')
        parser_config.add_argument("--verbose", help="display entire configruation file", action="store_true")

        # glping (GitLab ping)
        parser_glping = subparsers.add_parser('glping', help='hail the GitLab server to verify everything is working')

        # clone command
        parser_clone = subparsers.add_parser('clone', help='clone projects')
        parser_clone.add_argument("--project", help="name of the assignment, lab or project", required=True)
        parser_clone.add_argument("--emails", help="path to text file containing student emails", required=True)
        parser_clone.add_argument("--force", help="force overwrite of existing directory", action="store_true")

        # grade command
        parser_grade = subparsers.add_parser('grade', help='grade projects')
        parser_grade.add_argument("--project", help="name of the assignment, lab or project", required=True)
        parser_grade.add_argument("--emails", help="path to text file containing student emails", required=True)
        parser_grade.add_argument("--chide", help="automatically email students when project not found", action="store_true")

        # project
        parser_project = subparsers.add_parser('projects', help='list projects for a given owner/email')
        parser_project.add_argument("--owner", help="person for which to find the projects")
        parser_project.add_argument("--emails", help="path to text file containing students emails")
        parser_project.add_argument("--share", help="shares each student's list with the student", action="store_true")

        # group command
        parser_group = subparsers.add_parser('group', help='command used to manage groups on server')
        subparsers_group = parser_group.add_subparsers()
        # ...create subcommand
        parser_group_create = subparsers_group.add_parser('create', help='create new group on server')
        parser_group_create.add_argument('--groupname', type=str, help='name of the group to create', required=True)

        # ...append subcommand
        parser_group_append = subparsers_group.add_parser('append', help='append emails to existing group on server')
        parser_group_append.add_argument('--groupname', type=str, help='name of the group to which to append names',
                                         required=True)
        parser_group_append.add_argument('--emails', type=str, help='path to text file containing student emails',
                                         required=True)

        self._args = self._argparser.parse_args()
        self._argsdict = vars(self._args)

    def _init_server(self):
        """Sets the server endpoint and user token that we'll use to log in."""
        self._server = GitLabServer(ProctorConfig.get_config_value('GitLabServer', 'url'))
        self._user = GitLabUser(ProctorConfig.get_config_value('GitLabUser', 'private_token'))

    def process_command(self):
        """Process the user-specified command. This method acts as a junction, dispatching
        calls to appropriate handler functions to complete the work."""
        cmd = sys.argv[1]
        if cmd == 'config':
            self._display_config_info()
        elif cmd == 'glping':
            self._glping()
        elif cmd == 'clone':
            project_name = self._argsdict['project']
            self._clone_project_cmd(project_name)
        elif cmd == 'grade':
            self._grade_project()
        elif cmd == 'projects':
            self._list_projects()
        elif cmd == 'group':
            self._manage_groups()
        elif cmd == 'srefresh':
            self._refresh_student_projects()
        else:
            self._logger.error(f"Unknown command '{cmd}'. Try -h for help.")
            sys.exit(0)

    def _clone_project_cmd(self, project_name):
        """Called when clone called from the command line. Prepares arguments and then
        delegates actual clone operation to common cloning function.
        :arg project_name: Name of project to clone, e.g., pa1-review-student-master"""
        email_file = self._argsdict['emails']
        emails = self._get_emails_from_file(email_file)
        force = self._argsdict['force']
        self._clone_project(project_name, emails, force)

    def _refresh_student_projects(self):

        parameters = self._parse_parameters_from_argv('owner', 'emails', 'grade')
        owner = parameters['owner']
        email_file = parameters['emails']
        grade = parameters['grade']

        if owner is None and email_file is None:
            self._logger.warning("Please add the --owner or --emails parameter. If both given, --owner wins.")
            return

        projects = ProctorConfig.get_section_items('Projects').keys()
        emails = list()
        if owner:
            emails.append(owner)
        else:
            emails = (self._get_emails_from_file(email_file))

        for p in projects:
            self._clone_project(p, emails, force=True)

        if grade:
            for p in projects:
                self._grade_project(p, emails)

    def _grade_project(self, project_name=None, emails=None):
        """Grades the given project for each email in the specified email file, pulled from program args.
        Projects are expected to have been cloned to a local directory previously.
        Results in the gradebook file saved to the project's working directory."""

        if project_name is None:
            project_name = self._argsdict['project']
        project_dir = os.sep.join([self._working_dir_name, project_name])
        project_due_dt = ProctorConfig.get_config_value(project_name, 'due_dt')

        gradebook = GradeBook(self._working_dir_name, project_name, project_due_dt)
        builder = Builder()
        testrunner = UnitTestRunner()
        grader = Grader(builder, testrunner, gradebook)

        owner_emails = emails if not emails is None else \
            self._get_emails_from_file(self._argsdict['emails'])
        users_missing_project = []

        self._logger.info(f'Grading {project_name}')

        num_to_grade = len(owner_emails)
        current = 0

        for email in owner_emails:

            email = email.strip(' ')
            current += 1

            self._logger.info('---')
            self._logger.info(f'Owner {email} ({current} of {num_to_grade})')

            if len(email) == 0:
                self._logger.info(f"Invalid owner email '{email}'. Check email file for blank lines.")
                continue

            dir_to_grade = Path(project_dir) / email
            if not dir_to_grade.exists():
                users_missing_project.append(email)
                self._logger.warning('Local project not found: {}. Try clone.'.format(str(dir_to_grade)))
                gradebook.local_project_not_found(email)
                continue

            project = self._server.get_user_project(email, project_name)
            if project:
                commits = project.commits.list()
                if commits:
                    latest_commit_date = commits[0].created_at  # GitLab returns most recent first (index 0)
                    grader.grade(email, project_name, dir_to_grade, project_due_dt, latest_commit_date)
                else:
                    gradebook.commit_not_found(email)
                    self._logger.warning('No commit. Server project found, no commit.')
            else:
                gradebook.server_project_not_found(email)
                self._logger.warning('Not found. Project not found on server. Check email address.')

        self._logger.info('---')
        self._logger.info(f'Saving grades to: {gradebook.get_file_name()}')
        gradebook.save()

        if users_missing_project:
            self._logger.info("Local project missing for: {}".format(users_missing_project))
            if 'chide' in self._argsdict:
                if self._argsdict['chide']:
                    self._logger.info("Chiding people with missing projects...")
                    Postman.send_missing_project_email(users_missing_project, project_name, self._logger)

    def _clone_project(self, project_name, emails, force):
        """Clones the given project for each email in the specified email file.
        :arg project_name: Name of the project to clone, e.g., pa1-review-student-master
        :arg emails: List of emails for which to clone projects
        :arg force: If true, causes clone to overwrite existing target directories"""
        if emails is None:
            self._logger.error("Cannot clone projects without valid emails. Exiting.")
            sys.exit(-1)

        # Make sure emails that come from file are not blank
        owner_emails = [email for email in emails if len(email.strip(' ')) > 0]

        # Clone 'em
        self._logger.info('Cloning project: {}'.format(project_name))
        for email in owner_emails:
            gitlab_project = self._server.get_user_project(email, project_name)
            if gitlab_project:
                dest_path_name = PathManager.build_dest_path_name(self._working_dir_name, email, project_name)
                self._server.clone_project(gitlab_project, dest_path_name, force)
            else:
                self._logger.warning(f"Project not found. Check project name '{project_name}' and email '{email}'.")

    def _display_config_info(self):
        """Displays basic logging information."""
        p._logger.info(f'Configuration file: {ProctorConfig.config_file}')
        p._logger.info(f'Working directory : {p._working_dir_name}')
        p._logger.info(f'Log file          : {p._logger._logfile_name}')
        if self._args.verbose:
            self._display_config_file()

    def _display_config_file(self):
        """Displays the contents of the configuration file. Note that the contents of the configuration
        file are not logger and simply displayed on the console."""
        print(f'\n{ProctorConfig.config_file}:')
        with open(ProctorConfig.config_file) as f:
            print(f.read())

    def _list_projects(self):
        """Finds and displays the repo URLs for all projects on the GitLab server owned by the
        a single owner (--owner) or a list of people (--emails)."""

        parameters = self._parse_parameters_from_argv('owner', 'emails', 'share')
        owner = parameters['owner']
        email_file = parameters['emails']
        share = parameters['share']

        if owner is None and email_file is None:
            self._logger.warning("Please add the --owner or --emails parameter. If both given, --owner wins.")
            return

        the_projects = None
        if owner:
            the_projects = {owner: self._list_projects_for(owner)}
        elif email_file:
            the_projects = self._list_projects_for_owners(email_file)
        if share:
            self._email_owners_project_summary_list(the_projects)

    def _parse_parameters_from_argv(self, *args):
        parameters = dict()
        for arg in args:
            parameters[arg] = self._argsdict[arg] if arg in self._argsdict else None
        return parameters

    def _list_projects_for(self, owner):
        num_projects, projects = self._server.get_projects_for_owner(owner)
        self._logger.info(f'{owner} has {num_projects} projects')

        count = 1
        for p in projects:
            self._logger.info(f'{count:2} {p}')
            count += 1
        return projects

    def _list_projects_for_owners(self, email_file):
        """Iterates over the emails in the given email file and lists all projects owned by that person.
        If --share has been specified on the command line, email each person his or her project list.
        :arg email_file: Full path to the file that contains the list of project owner emails to process. """
        owner_emails = self._get_emails_from_file(email_file)
        num_emails = len(owner_emails)

        self._logger.info(f'Fetching projects for {num_emails} people')
        projects = dict()
        count = 1

        for email in owner_emails:
            self._logger.info('---')
            self._logger.info(f'Owner: {email} ({count} of {num_emails})')
            email = email.strip()
            if email:
                projects[email] = self._list_projects_for(email)
            else:
                self._logger.info(f"Invalid email '{email}' in file. Skipped.")
            count += 1

        return projects

    def _email_owners_project_summary_list(self, projects):
        """Emails each person a summary list of what his or she has uploaded to the server and
        available to the instructor.
        :arg projects: A dictionary that maps email->list of projects"""
        num_owners = len(projects)
        self._logger.info(f'Sharing project information with {num_owners} owners')

        for recipient, the_projects in projects.items():
            msg = []
            now = dt.today().strftime("%Y-%m-%d %H:%M")
            msg.append('This is an automatically generated email.\n')
            msg.append(f'Projects available to your instructor as of {now}:\n')
            msg.append('\n'.join(the_projects))
            msg.append('\nIf you think this list is inaccurate, please contact your instructor.\n---\n')
            self._logger.info(f'Emailing project snapshot: {recipient}')
            msg_body = '\n'.join(msg)
            Postman.send_email(recipient, 'Projects Availability Snapshot', msg_body, self._logger)

    def _glping(self):
        """Hails the GitLab server and returns information about the logged in user."""
        #self._logger.info("glping")
        try:
            user = self._server.whoami()
            self._logger\
                .info(f'Hello {user.name} (id={user.id}, username={user.username}, email={user.email})')
            user_projects = self._server.get_all_projects_owned_by_current_user()
            if user_projects:
                self._logger.info('Owned projects: {}'.format(len(user_projects)))
                #for p in user_projects:
                #    self._logger.info(repr(p))
            else:
                self._logger.info('No owned projects (yet!)')
        except Exception as e:
            self._logger.error(f'Cannot access GitLab server. Check URL and private token in configuration file.')
            self._logger.error(f'Error message: {e}')

    def _manage_groups(self):
        """Ensures proper use of group command"""
        if len(self._argsdict) == 0:
            self._logger.error('usage: proctor.py group {create, append} [-h]')
            self._logger.error(
                "proctor.py group: error: command must include subcommand 'create' or 'append'. Try proctor.py -h.")
            sys.exit(-1)

        subcommand = sys.argv[2]
        if subcommand == 'create':
            self._create_server_group(self._args.groupname)
            return
        if subcommand == 'append':
            self._add_users_to_server_group(self._args.groupname, self._args.emails)
        else:
            raise ValueError(f'Unknown group subcommand: {subcommand}')

    def _create_server_group(self, group_name):
        """Creates a new group on the GitLab server.
        :param Name of group to create"""
        self._server.create_group(group_name)

    def _add_users_to_server_group(self, group_name, emails_file_name):
        """Adds given set of people (emails) to the specified group.
        :param group_name: Name of group to which to add people
        :param emails_file_name: Name of file that contains the list of emails to add to the group"""
        email_list = self._get_emails_from_file(emails_file_name)
        self._server.add_users_to_group(group_name, email_list)

    def _get_emails_from_file(self, email_file):
        """Returns a list of emails from the given file.
        :param email_file: Path to the file that contains project-owner email addresses.
        :returns: List of emails from the given email file."""
        owner_emails = GitLabUser.get_emails(email_file)
        if owner_emails is None:
            self._logger.error(f'EMAIL FILE {email_file} NOT FOUND. Check the path.')
        return owner_emails

    def done(self):
        # Possibly print something here
        pass

if __name__ == "__main__":

    if len(sys.argv) <= 1:
        termcolor.cprint("usage: proctor.py [-h] {config, glping, clone, grade, group, srefresh}", color='red')
        sys.exit(-1)

    ProctorConfig.init(None)
    p = Proctor()
    p.process_command()
    p.done()
    sys.exit(0)
