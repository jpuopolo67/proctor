
import gitlab.v3
import gitlab.v3.objects
import subprocess
import logging
import os
from pathmgr import PathManager


class GitLabServer:
    """Abstracts the GitLab server that contains  users, groups, and projects."""

    _GITLAB_API_VERSION = 3 # The version of the GitLab API supported by the WIT server

    @staticmethod
    def build_server_project_path(project_name, owner_email):
        """Builds a repo name using the project name and email."""
        repo_name = owner_email
        if '@' in owner_email:
            repo_name = owner_email.split('@')[0]
        repo_name = os.sep.join([repo_name, project_name])
        return repo_name


    def __init__(self, server_url, api_version=_GITLAB_API_VERSION):
        """Initializes the GitLabServer with a URL and API version, enabling login and
        programmatic communication."""
        self._url = server_url
        self._api_version = api_version
        self._logger = logging.getLogger("proctor")


    def login(self, user):
        """Establishes an authenticated connection to the GitLab server."""
        self._server = gitlab.Gitlab(url=self._url,
                                     private_token=user.get_private_token(),
                                     api_version=str(self._api_version))


    def whoami(self):
        """Returns the user currently logged into the GitLab server from the program's perspective.
        :returns The name of the currently logged in user."""
        self._server.auth() #required to make next line work!
        current_user = self._server.user
        return current_user


    def get_user_project(self, owner_email, project_name):
        """Fetches information about a user's project from the GitLabServer.
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
        :returns GitLab user information."""
        return self._server.users.get(userid)


    def get_projects_named(self, project_name):
        """Fetches information about GitLab projects with a given project name.
        :returns A list of the all projects available to the currently logged in user that match
        the given project name."""
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
            #shell_cmd = 'git clone {repo} {dest_dir}'.format(repo=http_url, dest_dir=dest_path_name)
            result = subprocess.run(['git', 'clone', http_url, dest_path_name],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                self._logger.info('Cloned OK')
            else:
                sresult = result.stderr.decode('utf-8')
                self._logger.warning(f'CLONE WAR: {sresult}')
        except FileExistsError as fex:
            self._logger.warning(fex)




