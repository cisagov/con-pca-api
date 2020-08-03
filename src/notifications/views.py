"""
Notifications views.

This is the core of gerating emails to send to
contacts about reports and subscription updates.
"""


# Standard Python Libraries
from datetime import datetime
from pathlib import Path
from email.mime.image import MIMEImage
import logging
import pytz

# Third-Party Libraries
from django.conf import settings
from django.utils import timezone
import requests
from api.models.dhs_models import DHSContactModel, validate_dhs_contact
from api.utils.db_utils import get_single
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.storage import FileSystemStorage
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from notifications.utils import get_notification


logger = logging.getLogger()


class ReportsEmailSender:
    """ReportsEmailSender class."""

    def __init__(self, subscription, message_type):
        """Init method."""
        self.subscription = subscription
        self.message_type = message_type

    def get_attachment(self, subscription_uuid, link, cycle):
        """Get_attachment method."""
        url = f"{settings.REPORTS_API}/api/{link}/{subscription_uuid}/{cycle}/pdf/"
        resp = requests.get(url, stream=True, verify=False)
        fs = FileSystemStorage("/tmp")
        filename = Path("/tmp/subscription_report.pdf")
        filename.write_bytes(resp.content)
        return fs.open("subscription_report.pdf")

    def send(self):
        """Send method."""
        subject, path, link = get_notification(self.message_type)

        # pull subscription data
        subscription_uuid = self.subscription.get("subscription_uuid")
        recipient = self.subscription.get("primary_contact").get("email")
        dhs_contact_uuid = self.subscription.get("dhs_contact_uuid")
        dhs_contact = get_single(
            dhs_contact_uuid, "dhs_contact", DHSContactModel, validate_dhs_contact
        )
        recipient_copy = dhs_contact.get("email") if dhs_contact else None
        first_name = self.subscription.get("primary_contact").get("first_name")
        last_name = self.subscription.get("primary_contact").get("last_name")

        # pass context to email templates
        context = {"first_name": first_name, "last_name": last_name}

        text_content = render_to_string(f"emails/{path}.txt", context)
        html_content = render_to_string(f"emails/{path}.html", context)

        to = [f"{first_name} {last_name} <{recipient}>"]

        bcc = [f"DHS <{recipient_copy}>"] if recipient_copy else None

        message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.SERVER_EMAIL,
            to=to,
            bcc=bcc,
        )

        # pass image files
        image_files = ["cisa_logo.png"]
        for image_file in image_files:
            with staticfiles_storage.open(f"img/{image_file}") as f:
                header = MIMEImage(f.read())
                header.add_header("Content-ID", f"<{image_file}>")
                message.attach(header)

        # add html body to email
        message.attach_alternative(html_content, "text/html")

        # add pdf attachment
        current_cycle = self.subscription.get("cycles")[-1]
        cycle_date = datetime.strftime(
            current_cycle.get("start_date"), format="%Y-%m-%d"
        )
        attachment = self.get_attachment(subscription_uuid, link, cycle_date)
        message.attach("subscription_report.pdf", attachment.read(), "application/pdf")
        try:
            message.send(fail_silently=False)
        except ConnectionRefusedError:
            print("failed to send email")
        except ConnectionError:
            print("failed to send email for some other reason")


class SubscriptionNotificationEmailSender:
    """NotificationEmailSender class."""

    def __init__(self, subscription, notification_type):
        """Init method."""
        self.subscription = subscription
        self.notification_type = notification_type

    def create_context_data(self):
        """Create Contect Data Method."""
        first_name = self.subscription.get("primary_contact").get("first_name")
        last_name = self.subscription.get("primary_contact").get("last_name")
        current_cycle = current_cycle = self.subscription.get("cycles")[-1]
        cycle_uuid = current_cycle.get("cycle_uuid")

        logger.info(f'start_date={self.subscription.get("start_date")}')
        # Putting .split on the start and end date because sometimes it comes formatted with a float at the end.
        if not isinstance(self.subscription.get("start_date"), datetime):
            start_date = datetime.strptime(
                self.subscription.get("start_date").split(".")[0], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%d %B, %Y")
        else:
            start_date = self.subscription.get("start_date")

        if self.notification_type == "subscription_stopped":
            end_date = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
        else:
            end_date = self.subscription.get("end_date")

        if end_date is not None:
            if not isinstance(end_date, datetime):
                end_date = datetime.strptime(
                    end_date.split(".")[0], "%Y-%m-%dT%H:%M:%S"
                )

        return {
            "first_name": first_name,
            "last_name": last_name,
            "start_date": start_date,
            "end_date": end_date,
            "cycle_uuid": cycle_uuid,
        }

    def send(self):
        """Send method."""
        subject, path, _ = get_notification(self.notification_type)

        # pull subscription data
        recipient = self.subscription.get("primary_contact").get("email")

        # get to and bcc email addresses
        dhs_contact_uuid = self.subscription.get("dhs_contact_uuid")
        dhs_contact = get_single(
            dhs_contact_uuid, "dhs_contact", DHSContactModel, validate_dhs_contact
        )
        recipient_copy = dhs_contact.get("email") if dhs_contact else None

        print(recipient_copy)
        # pass context to email templates
        context = self.create_context_data()
        text_content = render_to_string(f"emails/{path}.txt", context)
        html_content = render_to_string(f"emails/{path}.html", context)

        to = [f"{context['first_name']} {context['last_name']} <{recipient}>"]
        bcc = [f"DHS <{recipient_copy}>"] if recipient_copy else None
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.SERVER_EMAIL,
            to=to,
            bcc=bcc,
        )

        # pass image files
        image_files = ["cisa_logo.png"]
        for image_file in image_files:
            with staticfiles_storage.open(f"img/{image_file}") as f:
                header = MIMEImage(f.read())
                header.add_header("Content-ID", f"<{image_file}>")
                message.attach(header)

        # add html body to email
        message.attach_alternative(html_content, "text/html")
        try:
            message.send(fail_silently=False)
        except ConnectionRefusedError:
            print("failed to send email")
        except ConnectionError:
            print("failed to send email for some other reason")
