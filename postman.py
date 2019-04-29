import smtplib
from pconfig import ProctorConfig

class Postman:
    """Postman enables the application to send emails programmatically."""
    @staticmethod
    def send_email(recipient, subject, body, logger):
        """Sends an email to the given recipient.
        :param recipient: Recipient email
        :param subject: Subject line
        :param body: Message body
        :param logger: Logger to which to capture send"""
        Postman._init_server()
        logger.debug(f"Sending email '{subject}' to {recipient}")
        header = f'Subject: {subject}\n'
        message_body = header + '\n' + body
        Postman._server.sendmail(Postman._smtp_user, recipient, message_body)
        Postman._server.quit()

    @staticmethod
    def send_missing_project_email(email_list, project_name, logger):
        """Sends an email to each person in the given email list.
        :param email_list: List of receipient email addresses
        :param project_name: Name of the project for which email is being sent.
        :param logger: Proctor's logger"""
        subject = "Missing Project: {}".format(project_name.upper())
        for recipient in email_list:
            logger.info(f'Chiding {recipient}')
            message_body = Postman._generate_missing_project_message_body(recipient, project_name)
            Postman.send_email(recipient, subject, message_body, logger)

    @staticmethod
    def _generate_missing_project_message_body(recipient_email, project_name):
        """Generates the body of the email message.
        :param recipient_email: Email address of recipient
        :param project_name: Project for which email is being sent
        :returns Email message body that will be sent to the recipient"""
        message_body = 'Hi {},\n\nI am currently in the process of grading {}, and cannot find your submission.' \
            .format(recipient_email, project_name)
        message_body += " Please make sure that you've submitted the project to the GitLab server and that you've" \
                        " given me Developer access to it.\n\nThanks."
        return message_body

    @staticmethod
    def _init_server():
        """Initializes SMTP variables and establishes secure communications with the SMTP server."""
        Postman._init_smpt()
        Postman._server = smtplib.SMTP(Postman._smtp_host, Postman._smtp_port)
        Postman._server.ehlo()
        Postman._server.starttls()
        Postman._server.login(Postman._smtp_user, Postman._smtp_pwd)

    @staticmethod
    def _init_smpt():
        """Initializes the variables used to communication with the SMTP server. See Proctor's configuration file."""
        Postman._smtp_host = ProctorConfig.get_config_value('SMTP', 'smtp_host')
        Postman._smtp_port = ProctorConfig.get_config_value('SMTP', 'smtp_port')
        Postman._smtp_user = ProctorConfig.get_config_value('SMTP', 'smtp_user')
        Postman._smtp_pwd = ProctorConfig.get_config_value('SMTP', 'smtp_pwd')
