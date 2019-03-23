class GitLabUser:

    @staticmethod
    def get_emails(fromfile):
        emails = None
        try:
            with open(fromfile) as file:
                emails = file.read().splitlines()
        except FileNotFoundError:
            pass
        return emails

    def __init__(self, private_token):
        self._private_token = private_token

    def get_private_token(self):
        return self._private_token
