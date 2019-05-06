import os
import subprocess
import gitlab.v3
import gitlab.v3.objects
from gitlab.v3.objects import GitlabCreateError
from pathmgr import PathManager
from pconfig import ProctorConfig
from ploggerfactory import ProctorLoggerFactory


class GitLabServer:
    """Abstracts the GitLab server that contains  users, groups, and projects."""

    _GITLAB_API_VERSION = 3 # The version of the GitLab API supported by the WIT server

    @staticmethod
    def build_server_project_path(project_name, owner_email):
        """Builds a repo name by combining the project name and email.
        :param project_name: Project being worked on, e.g., cloned or graded.
        :param owner_email: Project owner's email
        :returns Path name to project repository"""
        repo_name = owner_email
        if '@' in owner_email:
            repo_name = owner_email.split('@')[0]
        repo_name = os.sep.join([repo_name, project_name])
        return repo_name

    def __init__(self, server_url, api_version=_GITLAB_API_VERSION):
        """Initializes the GitLabServer with a URL and API version, enabling login and programmatic communication.
        :param server_url: URL to GitLab server API endpoint
        :param api_version GitLab API version used for communication"""
        self._url = server_url
        self._api_version = api_version
        self._logger = ProctorLoggerFactory.getLogger()

    def login(self, user):
        """Establishes an authenticated connection to the GitLab server.
        :param: GitLabUser logging into the GitLab server"""
        self._server = gitlab.Gitlab(url=self._url,
                                     private_token=user.get_private_token(),
                                     api_version=str(self._api_version))

    def whoami(self):
        """Returns the user currently logged into the GitLab server from the program's perspective.
        :returns The name of the currently logged in user."""
        self._server.auth() # <<< required to make next line work!
        current_user = self._server.user
        return current_user

    def get_all_projects_owned_by_current_user(self):
        """Gets all projects owned by the user currently logged into the GitLab server.
        :returns List of all projects owned by the user currently logged into the GitLab server."""
        return list(self._server.projects.owned(all=True))

    def get_projects_for_owner(self, email):
        """Fetches the list of projects owned by the given user/email.
        :param email: Email for which to find projects on the GitLab server.
        :returns: Tuple of project count and list of projects owned by given user."""

        user_projects = []
        project_count = 0

        username = email.replace('@wit.edu', '')
        all_projects = self._server.projects.list(search=username, all=True)

        for p in all_projects:
            if p.owner.username == username:
                project_count += 1
                user_projects.append(p.web_url)

        return (project_count, user_projects)

    def get_user_project(self, owner_email, project_name):
        """Fetches information about a user's project from the GitLabServer.
        :param owner_email: Project owner's email
        :param project_name: Project being worked on
        :returns: Information about the given user's GitLab project."""
        try:
            project_path = GitLabServer.build_server_project_path(project_name, owner_email)
            self._logger.info(f'Getting project info from server <= {project_path}')
            project = self._server.projects.get(project_path)
            return project
        except:
            return None

    def get_user_from_email(self, email):
        """Given an email address, fetches information about a GitLab user.
        :param email: GitLab user's email
        :returns GitLab user information."""
        users = self._server.users.list(search=email)
        num_users = len(users)
        if num_users == 1:
            return users[0]     # found exactly who we're looking for
        elif num_users == 0:
            return None         # didn't find the user

        # If we get here, we found > 1 user
        errmsg = f"Ambiguous: '{email}'. Try again with a more specific email."
        raise ValueError(errmsg)

    def get_user_by_id(self, userid):
        """Given a user ID, fetches information about a GitLab user.
        :param userid: User ID of the GitLab user on the GitLab server
        :returns GitLab user information."""
        return self._server.users.get(userid)

    def get_projects_named(self, project_name):
        """Fetches information about the specified project from the GitLab server.
        :param project_name: Name of the project to fetch from the server.
        :returns A list of the all projects available to the currently logged in user that match
        the given project name. Likely to be multiple, e.g., in the case of many students all having projects
        of the same name as one another."""
        projects = self._server.projects.list(search=project_name, all=True)
        return projects

    def clone_project(self, gitlab_project, dest_path_name, force=False):
        """git clone the given project from the GitLab server to the local computer.
        :returns None
        :param gitlab_project: GitLab project to clone.
        :param dest_path_name: Destination directory on the local computer to which the cloned files will be copied.
        :param force: True to force overwriting the destination directory if it already exists."""
        try:
            PathManager.init_dest_path(dest_path_name, force)
            http_url = gitlab_project.http_url_to_repo
            self._logger.info('Cloning repo: {}...{}'.format(http_url, "(FORCED)" if force else ''))
            result = subprocess.run(['git', 'clone', http_url, dest_path_name],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                self._logger.info('Cloned OK')
            else:
                sresult = result.stderr.decode('utf-8')
                self._logger.warning(f'Clone war: {sresult}')
        except FileExistsError as fex:
            self._logger.warning(str(fex))

    def create_group(self, group_name):
        """Creates a new group on the GitLab server.
        :param group_name: Name of the group to create on the GitLab server."""
        try:
            group_path_prefix = ProctorConfig.get_config_value('GitLabServer', 'group_path_prefix')
            group_path = '-'.join([group_path_prefix, group_name])
            self._server.groups.create({'name': group_name,
                                        'path': group_path,
                                        'visibility_level': gitlab.VISIBILITY_PRIVATE})
            self._logger.info(f"Group '{group_path}' created OK")
        except GitlabCreateError as err:
            self._logger.error(f'Cannot create server group {group_name}: {err.error_message}')

    def add_users_to_group(self, group_name, email_list):
        """Adds the given list of users (emails) to the specified group on the GitLab server.
        :param group_name: Group to which emails are added
        :param email_list: List of emails to add to the group"""
        self._logger.info(f"Adding users to group '{group_name}'")
        try:
            groups = self._server.groups.list(search=group_name, all=True)
            for email in email_list:
                for group in groups:
                    try:
                        self._logger.info(f'Adding {group.name}/{email}')
                        user = self.get_user_from_email(email)
                        if not user is None:
                            member = group.members.create({'user_id': user.id,
                                                           'access_level': gitlab.DEVELOPER_ACCESS})
                        else:
                            self._logger.warning('Unknown. User not found.')
                    except GitlabCreateError:
                        self._logger.warning('Duplicate. Already exists.')
                        continue
        except Exception as e:
            print(e, type(e))
            raise e

