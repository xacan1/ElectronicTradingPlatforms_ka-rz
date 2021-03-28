import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender:
    def __init__(self, login: str, password: str, addr_to: str, subject: str, sender_name: str):
        self.port = 465
        self.smtp_server = 'smtp.yandex.ru'
        self.login = login
        self.password = password
        self.subject = subject
        self.addr_to = addr_to
        self.sender_name = sender_name

    def send_message(self, message):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.subject
        # msg['From'] = f'{self.sender_name} <{self.login}>'
        msg['From'] = '{} <{}>'.format(self.sender_name, self.login)
        msg['To'] = self.addr_to
        html_msg = f"""
        <html>
        <head>
        <meta charset="utf-8">
        </head>
        <body>
            {message}
        </body>
        </html>
        """
        part1 = MIMEText(message.encode('utf-8'), 'plain', 'utf-8')
        part2 = MIMEText(html_msg, 'html')
        msg.attach(part1)
        msg.attach(part2)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.login, self.password)
            server.sendmail(self.login, self.addr_to, msg.as_string())
