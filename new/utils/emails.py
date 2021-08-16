"""Email utils."""
# Standard Python Libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

# Third-Party Libraries
from faker import Faker
from utils import time


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


def get_email_context(customer=None, target=None):
    """Get context for email template."""
    return {
        "target": target,
        "customer": customer,
        "time": time,
        "fake": Faker(),
    }


def get_from_address(sending_profile, template_from_address):
    """Get campaign from address."""
    # Get template display name
    if "<" in template_from_address:
        template_display = template_from_address.split("<")[0].strip()
    else:
        template_display = None

    # Get template sender
    template_sender = template_from_address.split("@")[0].split("<")[-1]

    # Get sending profile domain
    if type(sending_profile) is dict:
        sp_from = sending_profile["from_address"]
    else:
        sp_from = sending_profile.from_address
    sp_domain = sp_from.split("<")[-1].split("@")[1].replace(">", "")

    # Generate from address
    if template_display:
        from_address = f"{template_display} <{template_sender}@{sp_domain}>"
    else:
        from_address = f"{template_sender}@{sp_domain}"
    return from_address