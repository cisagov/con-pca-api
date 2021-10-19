"""Email Notifications."""
# Standard Python Libraries
from datetime import datetime
import logging
import os

# Third-Party Libraries
from flask import render_template

# cisagov Libraries
from api.config import SMTP_FROM
from api.manager import SubscriptionManager, TemplateManager
from utils.aws import SES
from utils.reports import get_report_pdf

template_manager = TemplateManager()
subscription_manager = SubscriptionManager()


class Notification:
    """Manage sending email notifications."""

    def __init__(self, message_type: str, subscription: dict, cycle: dict):
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
            params={"template_id": {"$in": self.cycle["template_ids"]}}
        )

        return {
            "first_name": self.subscription["primary_contact"]["first_name"].title(),
            "last_name": self.subscription["primary_contact"]["last_name"].title(),
            "start_date": self.subscription["start_date"].strftime("%b %d %Y %H:%M:%S"),
            "end_date": end_date.strftime("%b %d %Y %H:%M:%S"),
            "templates": templates,
            "target_count": self.cycle["target_count"],
            "admin_email": self.subscription["admin_email"],
            "subscription_id": self.subscription["_id"],
        }

    def get_report(self, message_type: str, context: dict):
        """Get report html, text and subject."""
        report = {
            "status_report": {
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
        return report

    def get_to_addresses(self):
        """Get email addresses to send to."""
        return [
            self.subscription["primary_contact"]["email"],
            self.subscription["admin_email"],
        ]

    def add_notification_history(self, addresses):
        """Add history of notification to subscription."""
        data = {
            "message_type": self.message_type,
            "sent": datetime.now(),
            "email_to": addresses,
            "email_from": SMTP_FROM,
        }
        subscription_manager.add_to_list(
            document_id=self.subscription["_id"],
            field="notification_history",
            data=data,
        )

    def send(self, nonhuman=False):
        """Send Email."""
        ses = SES()
        # Set Context
        context = self.set_context()
        report = self.get_report(self.message_type, context)

        attachments = []
        if self.message_type in ["status_report"]:
            filename = get_report_pdf(
                [self.cycle["_id"]],
                self.message_type.split("_")[0],
                nonhuman,
            )
            logging.info(f"Attaching {filename} to notification.")
            attachments.append(filename)

        addresses = self.get_to_addresses()

        logging.info(f"Sending template {self.message_type} to {addresses}")
        try:
            ses.send_email(
                source=SMTP_FROM,
                to=addresses,
                subject=report["subject"],
                html=report["html"],
                attachments=attachments,
            )
            self.add_notification_history(addresses)
        except Exception as e:
            raise e
        finally:
            if attachments:
                for attachment in attachments:
                    logging.info(f"Deleting attachment {attachment}")
                    os.remove(attachment)
