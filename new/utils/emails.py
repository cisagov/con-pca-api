"""Email utils."""
# Standard Python Libraries
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from smtplib import SMTP

# Third-Party Libraries
from bs4 import BeautifulSoup
from faker import Faker
from utils import time


def build_message(
    subject,
    from_email,
    html,
    to_recipients=[],
    bcc_recipients=[],
    attachments=[],
):
    """Build raw email for sending."""
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = from_email

    if to_recipients:
        message["To"] = ",".join(to_recipients)
    if bcc_recipients:
        message["Bcc"] = ",".join(bcc_recipients)

    message.attach(MIMEText(html, "html"))
    text = get_text_from_html(html)
    message.attach(MIMEText(text, "plain"))

    for filename in attachments:
        with open(filename, "rb") as attachment:
            part = MIMEApplication(attachment.read())
            part.add_header("Content-Disposition", "attachment", filename="report.pdf")
        message.attach(part)

    return message.as_string()


def get_text_from_html(html):
    """Convert html to text for email."""
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)
    return text


def convert_html_links(html):
    """Convert all html links to url tag."""
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a"):
        link["href"] = "{{ url }}"
    return soup.prettify()


class Email:
    """Email."""

    def __init__(self, sending_profile):
        """Email."""
        self.sending_profile = sending_profile
        self.server = SMTP(sending_profile["host"])
        self.server.starttls()
        self.server.login(
            self.sending_profile["username"],
            self.sending_profile["password"],
        )

    def send(self, to_email, from_email, subject, body):
        """Send email."""
        message = build_message(
            subject=subject,
            from_email=from_email,
            html=body,
            to_recipients=[to_email],
        )
        self.server.sendmail(from_email, to_email, message)
        logging.info(f"Sent email to {to_email} from {from_email}.")

    def __del__(self):
        """On deconstruct, quit server."""
        self.server.quit()


def get_email_context(customer=None, target=None, url=None):
    """Get context for email template."""
    return {
        "target": target,
        "customer": customer,
        "time": time,
        "fake": Faker(),
        "url": url,
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
