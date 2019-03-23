
class GitLabUser:
    """Represents a user on the GitLab server."""
    @staticmethod
    def get_emails(fromfile):
        """Fetches a list of emails from the given file.
        :param fromfile: Path name to file containing list of emails
        :returns List of email addresses parsed from the given file. None on error."""
        emails = None
        try:
            with open(fromfile) as file:
                emails = file.read().splitlines()
        except FileNotFoundError:
            pass
        return emails

    def __init__(self, private_token):
        """Initializes the GitLabUser.
        :param private_token: User's private token used to access the GitLab server."""
        self._private_token = private_token

    def get_private_token(self):
        """Returns the GitLabUser's private token, used for logging into the GitLab server.
        :returns User's private token."""
        return self._private_token
