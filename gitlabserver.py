
import gitlab.v3
import gitlab.v3.objects
import os
from pathlib import Path
import shutil


class GitLabServer:
    """Abstracts the GitLab server that contains our users, groups, and projects."""
    _GITLAB_API_VERSION = 3

    @staticmethod
    def build_project_path(owner_email, project_name):
        """Builds a repo name by stripping domain from email, adding / and appending the
        project name, e.g., myname/myrepo"""

        repo_name = owner_email
        if '@' in owner_email:
            repo_name = owner_email.split('@')[0]
        repo_name = str.format('{}/{}', repo_name, project_name)
        return repo_name

    def __init__(self, server_url, api_version=_GITLAB_API_VERSION):
        self._url = server_url
        self._api_version = api_version

    def login(self, user):
        self._server = gitlab.Gitlab(url=self._url,
                                     private_token=user.get_private_token(),
                                     api_version=str(self._api_version))

    def whoami(self):
        self._server.auth() #required to make next line work!
        current_user = self._server.user
        return current_user

    def get_user_project(self, owner_email, project_name):
        project_path = GitLabServer.build_project_path(owner_email, project_name)
        try:
            project = self._server.projects.get(project_path)
            return project
        except:
            return None

    def get_user_from_email(self, email):
        users = self._server.users.list(search=email)
        num_users = len(users)
        if num_users == 1:
            return users[0]     # found exactly who we're looking for
        elif num_users == 0:
            return None         # didn't find the user

        # If we get here, we found > 1 user
        errmsg = str.format("Ambiguous email '{}'. Try again with a more specific email.", email)
        raise ValueError(errmsg)

    def get_user_by_id(self, userid):
        return self._server.users.get(userid)

    def get_projects_named(self, project_name):
        projects = self._server.projects.list(search=project_name, all=True)
        return projects

    def clone_project(self, gitlab_project, dest_path_name, force=False):
        dest_path = Path(dest_path_name)
        try:
            http_url = gitlab_project.http_url_to_repo
            print(str.format("Cloning repo {}...{}", http_url, "(FORCED)" if force else ''))
            self._init_dest_path(dest_path, force)
            shell_cmd = str.format("git clone {repo} {dest_dir}",
                                   repo=http_url, dest_dir=str(dest_path))
            os.system(shell_cmd)
        except FileExistsError as fex:
            print(fex)

    def _init_dest_path(self, dest_path, force):
        if not dest_path.exists():
            dest_path.mkdir(parents=True)
        if dest_path.exists() and force:
            shutil.rmtree(dest_path)
            dest_path.mkdir(parents=True, exist_ok=True)
            return

        errmsg = str.format("FAILED: Destination directory '{}' already exists. Use --force to overwrite.", str(dest_path))
        raise FileExistsError(errmsg)



