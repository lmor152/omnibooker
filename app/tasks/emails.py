import smtplib
from email.mime.text import MIMEText

from app.core.settings import settings


def send_email(subject: str, content: str, to_email: str | None) -> None:
    if to_email is None:
        return

    smtp_server = settings.app.smtp_host
    smtp_port = settings.app.smtp_port
    username = settings.app.smtp_username
    password = settings.app.smtp_password

    msg = MIMEText(content)
    msg["Subject"] = subject
    msg["From"] = settings.app.email_from
    msg["To"] = to_email

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(msg["From"], [msg["To"]], msg.as_string())
    server.quit()
