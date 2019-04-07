
import smtplib
from pconfig import ProctorConfig

class Postman:
    @staticmethod
    def sendmail(email_list, project_name):
        Postman._init_server()
        subject = "Missing Project: {}".format(project_name.upper())
        header = f'Subject: {subject}\n'
        for receiver in email_list:
            message_body = header + '\n' + Postman._generate_message_body(receiver, project_name)
            Postman._server.sendmail(Postman._smtp_user, receiver,  message_body)
        Postman._server.quit()

    @staticmethod
    def _generate_message_body(person, project_name):
        message_body = 'Hi {},\n\nI am currently in the process of grading {}, and cannot find your submission.' \
            .format(person, project_name)
        message_body += " Please make sure that you've submitted the project to the GitLab server and that you've" \
                        " given me Developer access to it.\n\nThanks."
        return message_body

    @staticmethod
    def _init_server():
        Postman._init_smpt()
        Postman._server = smtplib.SMTP(Postman._smtp_host, Postman._smtp_port)
        Postman._server.ehlo()
        Postman._server.starttls()
        Postman._server.login(Postman._smtp_user, Postman._smtp_pwd)

    @staticmethod
    def _init_smpt():
        Postman._smtp_host = ProctorConfig.get_config_value('SMTP', 'smtp_host')
        Postman._smtp_port = ProctorConfig.get_config_value('SMTP', 'smtp_port')
        Postman._smtp_user = ProctorConfig.get_config_value('SMTP', 'smtp_user')
        Postman._smtp_pwd = ProctorConfig.get_config_value('SMTP', 'smtp_pwd')
