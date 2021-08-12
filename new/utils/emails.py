"""Email utils."""
# Standard Python Libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP


def send_email(to_email, from_email, subject, body, sending_profile):
    """Send email."""
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = to_email
    message.attach(MIMEText(body, "html"))
    message_body = message.as_string()
    server = SMTP(sending_profile["host"])
    server.starttls()
    server.login(sending_profile["username"], sending_profile["password"])
    server.sendmail(from_email, to_email, message_body)
    server.quit()
