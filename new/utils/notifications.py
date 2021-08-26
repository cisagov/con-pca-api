"""Email Notifications."""
# Standard Python Libraries
from datetime import datetime
import logging

# Third-Party Libraries
from bs4 import BeautifulSoup
from flask import render_template
from utils.aws import SES

# cisagov Libraries
from api.config import SMTP_FROM
from api.manager import TemplateManager

template_manager = TemplateManager()


class Notification:
    """Manage sending email notifications."""

    def __init__(self, message_type: str, subscription: str, cycle: str):
        """Initialize."""
        self.message_type = message_type
        self.subscription = subscription
        self.cycle = cycle

    def set_context(self):
        """Set notification context."""
        if self.message_type == "subscription_stopped":
            end_date = datetime.utcnow()
        else:
            end_date = self.cycle["end_date"]

        templates = template_manager.all(
            params={"template_uuid": {"$in": self.cycle["template_uuids"]}}
        )

        return {
            "first_name": self.subscription["primary_contact"]["first_name"].title(),
            "last_name": self.subscription["primary_contact"]["last_name"].title(),
            "start_date": self.subscription["start_date"].strftime("%b %d %Y %H:%M:%S"),
            "end_date": end_date.strftime("%b %d %Y %H:%M:%S"),
            "templates": templates,
            "target_count": self.cycle["target_count"],
            "admin_email": self.subscription["admin_email"],
            "subscription_uuid": self.subscription["subscription_uuid"],
        }

    def get_report(self, message_type: str, context: dict):
        """Get report html, text and subject."""
        report = {
            "monthly_report": {
                "subject": "Con-PCA Phishing Subscription Status Report",
            },
            "cycle_report": {
                "subject": "Con-PCA Phishing Subscription Cycle Report",
            },
            "yearly_report": {
                "subject": "Con-PCA Phishing Subscription Yearly Report",
            },
            "subscription_started": {
                "subject": "Con-PCA Phishing Subscription Started",
            },
            "subscription_stopped": {
                "subject": "Con-PCA Phishing Subscription Stopped",
            },
        }.get(message_type, {})
        report["html"] = render_template(f"emails/{message_type}.html", **context)
        report["text"] = self.get_text_from_html(html=report["html"])
        return report

    def get_text_from_html(self, html):
        """Convert html to text for email."""
        soup = BeautifulSoup(html, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        return text

    def get_to_addresses(self):
        """Get email addresses to send to."""
        return [
            self.subscription["primary_contact"]["email"],
            self.subscription["admin_email"],
        ]

    def send(self):
        """Send Email."""
        ses = SES()
        # Set Context
        context = self.set_context()
        report = self.get_report(self.message_type, context)
        addresses = self.get_to_addresses()

        logging.info(f"Sending template {self.message_type} to {addresses}")
        return ses.send_email(
            source=SMTP_FROM,
            to=addresses,
            subject=report["subject"],
            text=report["text"],
            html=report["html"],
        )
