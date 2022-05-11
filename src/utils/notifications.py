"""Email Notifications."""
# Standard Python Libraries
from datetime import datetime
import logging
import os

# Third-Party Libraries
from flask import render_template

# cisagov Libraries
from api.config.application import AppConfig
from api.manager import SubscriptionManager, TemplateManager
from utils.emails import Email
from utils.reports import get_report_pdf

app_config = AppConfig()
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
            params={"_id": {"$in": self.cycle["template_ids"]}}
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
            "subscription": self.subscription,
        }

    def get_report(self, message_type: str, context: dict):
        """Get report html, text and subject."""
        report = {
            "status_report": {
                "subject": "Con-PCA Phishing Subscription Status Report",
                "to": "primary_contact",
                "bcc": "admin",
            },
            "cycle_report": {
                "subject": "Con-PCA Phishing Subscription Cycle Report",
                "to": "primary_contact",
                "bcc": "admin",
            },
            "yearly_report": {
                "subject": "Con-PCA Phishing Subscription Yearly Report",
                "to": "primary_contact",
                "bcc": "admin",
            },
            "subscription_started": {
                "subject": "Con-PCA Phishing Subscription Started",
                "to": "primary_contact",
                "bcc": "admin",
            },
            "subscription_stopped": {
                "subject": "Con-PCA Phishing Subscription Stopped",
                "to": "primary_contact",
                "bcc": "admin",
            },
            "thirty_day_reminder": {
                "subject": "Con-PCA Phish Subscription 30-Day Reminder",
                "to": "primary_contact",
                "bcc": "admin",
            },
            "fifteen_day_reminder": {
                "subject": "Con-PCA Phish Subscription 15-Day Reminder",
                "to": "primary_contact",
                "bcc": "admin",
            },
            "five_day_reminder": {
                "subject": "Con-PCA Phish Subscription 5-Day Reminder",
                "to": "admin",
            },
            "safelisting_reminder": {
                "subject": "Con-PCA Phish Subscription Safelisting Information",
                "to": "primary_contact",
                "bcc": "admin",
            },
        }.get(message_type, {})
        report["html"] = render_template(f"emails/{message_type}.html", **context)
        return report

    def get_to_addresses(self, report):
        """Get email addresses to send to."""

        def get_email(t):
            """Get email based on report type."""
            if t == "primary_contact":
                return self.subscription["primary_contact"]["email"]
            elif t == "admin":
                return self.subscription["admin_email"]

        addresses = {}
        if report.get("to"):
            addresses["to"] = [get_email(report["to"])]
        if report.get("bcc"):
            addresses["bcc"] = [get_email(report["bcc"])]
        if report.get("cc"):
            addresses["cc"] = [get_email(report["cc"])]

        return addresses

    def add_notification_history(self, addresses, from_address):
        """Add history of notification to subscription."""
        data = {
            "message_type": self.message_type,
            "sent": datetime.now(),
            "email_to": addresses,
            "email_from": from_address,
        }
        subscription_manager.add_to_list(
            document_id=self.subscription["_id"],
            field="notification_history",
            data=data,
        )

    def send(self, nonhuman=False):
        """Send Email."""
        # Set Context
        context = self.set_context()
        report = self.get_report(self.message_type, context)

        attachments = []
        if self.message_type in ["status_report", "cycle_report"]:
            filename = get_report_pdf(
                self.cycle,
                self.message_type.split("_")[0],
                reporting_password=self.subscription.get("reporting_password"),
                nonhuman=nonhuman,
            )
            logging.info(f"Attaching {filename} to notification.")
            attachments.append(filename)

        addresses = self.get_to_addresses(report)

        logging.info(f"Sending template {self.message_type} to {addresses}")
        try:
            config = app_config.load()
            sending_profile = {
                "interface_type": config["REPORTING_INTERFACE_TYPE"],
                "smtp_host": config["REPORTING_SMTP_HOST"],
                "smtp_username": config["REPORTING_SMTP_USERNAME"],
                "smtp_password": config["REPORTING_SMTP_PASSWORD"],
                "mailgun_domain": config["REPORTING_MAILGUN_DOMAIN"],
                "mailgun_api_key": config["REPORTING_MAILGUN_API_KEY"],
                "ses_role_arn": config["REPORTING_SES_ARN"],
                "headers": [],
            }
            from_address = config["REPORTING_FROM_ADDRESS"]
            if from_address:
                email = Email(sending_profile)
                email.send(
                    from_email=from_address,
                    to_recipients=addresses.get("to"),
                    bcc_recipients=addresses.get("bcc"),
                    message_type=self.message_type,
                    subscription_name=self.subscription.get("name"),
                    subject=report["subject"],
                    body=report["html"],
                    attachments=attachments,
                )

                self.add_notification_history(addresses, from_address)
        except Exception as e:
            raise e
        finally:
            if attachments:
                for attachment in attachments:
                    logging.info(f"Deleting attachment {attachment}")
                    os.remove(attachment)
