import argparse
import sys
import os
import termcolor
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
        parser_project.add_argument("--email", help="person for which to find the projects", required=True)

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
            self._clone_project()
        elif cmd == 'grade':
            self._grade_project()
        elif cmd == 'projects':
            self._find_projects_for_owner()
        elif cmd == 'group':
            self._manage_groups()
        else:
            self._logger.error(f"Unknown command '{cmd}'. Valid commands are: clone, grade")
            sys.exit(0)

    def _display_config_info(self):
        p._logger.info(f'Configuration file: {ProctorConfig.config_file}')
        p._logger.info(f'Working directory : {p._working_dir_name}')
        p._logger.info(f'Log file          : {p._logger._logfile_name}')
        if self._args.verbose:
            self._display_config_file()

    def _display_config_file(self):
        print(f'\n{ProctorConfig.config_file}:')
        with open(ProctorConfig.config_file) as f:
            print(f.read())

    def _find_projects_for_owner(self):
        owner_email = self._argsdict['email']
        num_projects, projects = self._server.get_projects_for_owner(owner_email)
        self._logger.info(f'{owner_email} has {num_projects} projects')
        count = 1
        for p in projects:
            self._logger.info(f'{count:2} {p}')
            count += 1
        return projects

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
            self._logger.error(f'Cannot access GitLab server')
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

    def _grade_project(self):
        """Grades the given project for each email in the specified email file, pulled from program args.
        Projects are expected to have been cloned to a local directory previously.
        Results in the gradebook file saved to the project's working directory."""

        project_name = self._argsdict['project']
        project_dir = os.sep.join([self._working_dir_name, project_name])
        project_due_dt = ProctorConfig.get_config_value(project_name, 'due_dt')

        gradebook = GradeBook(self._working_dir_name, project_name, project_due_dt)
        builder = Builder()
        testrunner = UnitTestRunner()
        grader = Grader(builder, testrunner, gradebook)

        owner_emails = self._get_emails_from_file(self._argsdict['emails'])
        users_missing_project = []

        self._logger.info(f'Grading {project_name}')
        for email in owner_emails:

            self._logger.info('---')
            self._logger.info(f'Owner {email}')

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
                    Postman.sendmail(users_missing_project, project_name, self._logger)

    def _get_emails_from_file(self, email_file):
        """Returns a list of emails from the given file.
        :param email_file: Path to the file that contains project-owner email addresses.
        :returns: List of emails from the given email file."""
        owner_emails = GitLabUser.get_emails(email_file)
        if owner_emails is None:
            self._logger.error(f'EMAIL FILE {email_file} NOT FOUND. Check the path.')
        return owner_emails

    def _clone_project(self):
        """Clones the given project for each email in the specified email file."""
        owner_emails = self._get_emails_from_file(self._argsdict['emails'])
        if owner_emails is None:
            self._logger.error("Cannot clone projects without valid emails. Exiting.")
            sys.exit(-1)

        project_name = self._argsdict['project']

        # Clone 'em
        self._logger.info('Cloning project: {}'.format(project_name))
        force = self._args.force
        for email in owner_emails:
            gitlab_project = self._server.get_user_project(email, project_name)
            if gitlab_project:
                dest_path_name = PathManager.build_dest_path_name(self._working_dir_name, email, project_name)
                self._server.clone_project(gitlab_project, dest_path_name, force)
            else:
                self._logger.warning(f'Not found: {email}. Check email address.')

    def done(self):
        # Possibly print something here
        pass

if __name__ == "__main__":

    if len(sys.argv) <= 1:
        termcolor.cprint("usage: proctor.py [-h] {config, glping, clone, grade, group}", color='red')
        sys.exit(-1)

    ProctorConfig.init()
    p = Proctor()
    p.process_command()
    p.done()
    sys.exit(0)
