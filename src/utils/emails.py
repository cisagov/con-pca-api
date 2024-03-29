"""Email utils."""
# Standard Python Libraries
from datetime import datetime
import email
from email.charset import QP, Charset
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import re
from smtplib import SMTP

# Third-Party Libraries
from bs4 import BeautifulSoup
import requests  # type: ignore
from requests.exceptions import HTTPError  # type: ignore
from werkzeug.utils import secure_filename

# cisagov Libraries
from utils import time
from utils.aws import SES
from utils.fake import Fake
from utils.logging import setLogger

logger = setLogger(__name__)


class Email:
    """Email."""

    def __init__(self, sending_profile):
        """Email."""
        self.sending_profile = sending_profile

        if sending_profile["interface_type"] == "SMTP":
            self.server = SMTP(sending_profile["smtp_host"])
            self.server.starttls()
            self.server.login(
                self.sending_profile["smtp_username"],
                self.sending_profile["smtp_password"],
            )

    def send(
        self,
        from_email: str,
        subject: str,
        body: str,
        message_type="",
        subscription_name="",
        to_recipients=[],
        bcc_recipients=[],
        attachments=[],
        **kwargs,
    ):
        """Send email."""
        if message_type == "safelisting_reminder":
            attachment_filename = secure_filename(
                f"CISA_PCA_Safelisting_Information_{subscription_name}_{datetime.today().strftime('%m%d%Y')}.xlsx"
            )
        elif message_type == "status_report" or message_type == "cycle_report":
            cycle_id = kwargs["cycle_id"]
            attachment_filename = secure_filename(
                f"CISA_PCA_{message_type}_{subscription_name}_{datetime.today().strftime('%m%d%Y')}_{cycle_id}.pdf"
            )
        else:
            attachment_filename = secure_filename(
                f"CISA_PCA_{message_type}_{subscription_name}_{datetime.today().strftime('%m%d%Y')}.pdf"
            )

        if self.sending_profile["interface_type"] == "SMTP":
            logger.info("Sending email via SMTP")
            self.send_smtp(
                from_email,
                subject,
                body,
                attachment_filename,
                to_recipients,
                bcc_recipients,
                attachments,
            )
        elif self.sending_profile["interface_type"] == "Mailgun":
            logger.info("Sending email via Mailgun")
            self.send_mailgun(
                from_email,
                subject,
                body,
                attachment_filename,
                to_recipients,
                bcc_recipients,
                attachments,
            )
        elif self.sending_profile["interface_type"] == "SES":
            logger.info("Sending email via SES")
            self.send_ses(
                from_email,
                subject,
                body,
                attachment_filename,
                to_recipients,
                bcc_recipients,
                attachments,
            )
        logger.info(
            f"Sent email to {to_recipients}, {bcc_recipients} from {from_email}."
        )

    def send_smtp(
        self,
        from_email,
        subject,
        body,
        filename,
        to_recipients=[],
        bcc_recipients=[],
        attachments=[],
    ):
        """Send email via SMTP."""
        message = build_message(
            subject=subject,
            from_email=from_email,
            html=body,
            pdf_filename=filename,
            to_recipients=to_recipients,
            bcc_recipients=bcc_recipients,
            headers=self.sending_profile.get("headers", []),
            attachments=attachments,
        )
        self.server.sendmail(from_email, to_recipients, message)

    def send_mailgun(
        self,
        from_email,
        subject,
        html,
        filename: str,
        to_recipients=[],
        bcc_recipients=[],
        attachments=[],
    ):
        """Send email via mailgun."""
        data = {
            "from": from_email,
            "to": to_recipients,
            "bcc": bcc_recipients,
            "subject": subject,
            "html": html,
            "text": get_text_from_html(html),
        }
        for header in self.sending_profile.get("headers", []):
            data[f"h:{header['key']}"] = header["value"]

        # Attach files to email
        attachment_files = []
        for a in attachments:
            with open(a, "rb") as file:
                attachment_files.append(("attachment", (filename, file.read())))

        resp = requests.post(
            f"https://api.mailgun.net/v3/{self.sending_profile['mailgun_domain']}/messages",
            auth=("api", self.sending_profile["mailgun_api_key"]),
            data=data,
            files=attachment_files,
        )
        try:
            resp.raise_for_status()
        except HTTPError as e:
            logger.exception(e)
            logger.error(resp.text)
            raise e
        # message = resp.json()
        # The message id that comes back looks like <20211027170419.1.8E418A15D17BB7E3@example.com>
        # This removes < and > that surround the message id for filtering
        # message_id = message["id"][1:-1]

    def send_ses(
        self,
        from_email,
        subject,
        body,
        filename: str,
        to_recipients=[],
        bcc_recipients=[],
        attachments=[],
    ):
        """Send email via SES."""
        ses = SES(self.sending_profile["ses_role_arn"])
        message = build_message(
            subject=subject,
            from_email=from_email,
            html=body,
            pdf_filename=filename,
            to_recipients=to_recipients,
            bcc_recipients=bcc_recipients,
            headers=self.sending_profile.get("headers", []),
            attachments=attachments,
        )
        ses.send_email(message)

    def __del__(self):
        """On deconstruct, quit server."""
        if self.sending_profile["interface_type"] == "SMTP":
            self.server.quit()


def get_email_context(customer=None, target=None, url=None):
    """Get context for email template."""
    return {
        "target": target,
        "customer": customer,
        "time": time,
        "fake": Fake(),
        "url": url,
        "datetime": datetime,
    }


def clean_from_address(template_from_address: str):
    """Clean processed from address."""
    # Get template display name
    template_display = ""
    template_sender = ""
    sp_domain = ""
    try:
        r = re.match("^(.*?) <(.*?)@(.*?)>", template_from_address)
        if r is not None:
            template_display = r.group(1)  # type: ignore
            template_sender = r.group(2)  # type: ignore
            sp_domain = r.group(3)  # type: ignore
    except AttributeError:
        split_from_address = template_from_address.split("@")
        template_sender = split_from_address[0]
        sp_domain = split_from_address[1]

    # Remove spaces and other special characters
    template_sender = template_sender.translate(template_sender.maketrans(" ,.", "---"))
    template_sender = template_sender.strip("-").lower()

    # Generate from address
    if "<" in template_from_address:
        from_address = f"{template_display} <{template_sender}@{sp_domain}>"
    else:
        from_address = f"{template_sender}@{sp_domain}"
    return from_address


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


def build_message(
    subject,
    from_email,
    html,
    pdf_filename,
    to_recipients=[],
    bcc_recipients=[],
    attachments=[],
    headers=[],
):
    """Build raw email for sending."""
    message = MIMEMultipart("alternative")
    cs = Charset("utf-8")
    cs.body_encoding = QP

    message["Subject"] = subject
    message["From"] = from_email

    if to_recipients:
        message["To"] = ",".join(to_recipients)
    if bcc_recipients:
        message["Bcc"] = ",".join(bcc_recipients)

    text = get_text_from_html(html)
    plain_text = MIMEText(text, "plain", cs)
    message.attach(plain_text)

    html_text = MIMEText(html, "html", cs)
    message.attach(html_text)

    for header in headers:
        message[header["key"]] = header["value"]

    for filepath in attachments:
        if filepath and not os.path.exists(filepath):
            logger.info("Attachment file does not exist: " + filepath)
            continue

        with open(filepath, "rb") as attachment:
            part = MIMEApplication(attachment.read())
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=pdf_filename,
            )
        message.attach(part)

    return message.as_string()


def parse_email(payload, convert_links=False):
    """Convert html to text for email."""
    message = email.message_from_string(payload.strip())

    html = None
    text = None

    for part in message.walk():
        if part.get_content_type() == "text/plain" and text is None:
            text = part.get_payload(decode=True).decode()
        if part.get_content_type() == "text/html" and html is None:
            html = part.get_payload(decode=True).decode()

    subject = message.get("Subject")

    # Convert html links
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    for link in links:
        link["href"] = "{{ url }}"

    return subject, soup.prettify(), text


def get_text_from_html(html):
    """Convert html to text for email."""
    soup = BeautifulSoup(html, "html.parser")

    for line_break in soup.find_all("br"):
        line_break.replace_with("\n")

    text = soup.find_all(text=True)
    output = ""
    blacklist = [
        "[document]",
        "noscript",
        "header",
        "html",
        "meta",
        "head",
        "input",
        "script",
    ]
    for t in text:
        if t.parent.name == "a":
            href = t.parent.get("href")
            output += f"{t} ({href}) "
        elif t == "\n":
            output += f"{t}"
        elif t.parent.name not in blacklist:
            output += f"{t} "

    return output.strip()
