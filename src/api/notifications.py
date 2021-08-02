"""Notifications."""
# Standard Python Libraries
from datetime import datetime
import logging
import os

# Third-Party Libraries
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string

# cisagov Libraries
from api.manager import CampaignManager
from api.services import DHSContactService, SubscriptionService, TemplateService
from api.utils.aws_utils import SES
from api.utils.reports import download_pdf
from config import settings

dhs_contact_service = DHSContactService()
subscription_service = SubscriptionService()
template_service = TemplateService()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.abspath(f"{BASE_DIR}/static")


class EmailSender:
    """Class for sending email notifications."""

    def __init__(self, subscription, message_type, cycle_uuid, nonhuman=False):
        """Init Email Sender."""
        self.subscription = subscription
        self.cycle_uuid = cycle_uuid
        self.notification = self._set_notification(message_type)
        self.attachment = self._get_attachment(nonhuman)
        self.dhs_contact = dhs_contact_service.get(
            self.subscription.get("dhs_contact_uuid")
        )
        self.context = self._set_context()

        self.text_content = render_to_string(
            f"emails/{self.notification['path']}.txt", self.context
        )
        self.html_content = render_to_string(
            f"emails/{self.notification['path']}.html", self.context
        )

        self.to = self._set_to()
        self.bcc = self._set_bcc()

    def send(self):
        """Send email."""
        try:
            if settings.USE_SES:
                self._send_ses()
            else:
                self._send_django()

            self._add_email_report_history()
        except Exception as e:
            logging.exception(e)
            raise e

    def _get_attachment(self, nonhuman=False):
        if "report" in self.notification["path"]:
            return download_pdf(
                report_type=self.notification["link"],
                uuid=self.subscription["subscription_uuid"],
                cycle_uuid=self.cycle_uuid,
                nonhuman=nonhuman,
            )
        return None

    def _send_django(self):
        message = EmailMultiAlternatives(
            subject=self.notification["subject"],
            body=self.text_content,
            from_email=settings.SERVER_EMAIL,
            to=self.to,
            bcc=self.bcc,
        )

        # image_files = []
        # for image_file in image_files:
        #     fp = open(os.path.abspath(f"{STATIC_DIR}/img/{image_file}"), "rb")
        #     msgImage = MIMEImage(fp.read(), _subtype="png")
        #     fp.close()
        #     msgImage.add_header("Content-ID", f"<{image_file}>")
        #     message.attach(msgImage)

        message.attach_alternative(self.html_content, "text/html")

        if self.attachment:
            message.attach(
                "subscription_report.pdf", self.attachment.read(), "application/pdf"
            )

        message.send(fail_silently=False)

    def _send_ses(self):
        ses = SES()

        if self.attachment:
            binary_attachments = [
                {"filename": "subscription_report.pdf", "data": self.attachment.read()}
            ]
        else:
            binary_attachments = None

        ses.send_message(
            sender=settings.SERVER_EMAIL,
            to=self.to,
            subject=self.notification["subject"],
            bcc=self.bcc,
            text=self.text_content,
            html=self.html_content,
            binary_attachments=binary_attachments,
        )

    def _add_email_report_history(self):
        data = {
            "report_type": self.notification["type"],
            "sent": datetime.now(),
            "email_to": self.subscription.get("primary_contact").get("email"),
            "email_from": settings.SERVER_EMAIL,
            "bcc": self.dhs_contact.get("email"),
        }

        logging.info(data)

        resp = subscription_service.push_nested(
            uuid=self.subscription["subscription_uuid"],
            field="email_report_history",
            data=data,
        )

        return resp

    def _set_context(self):
        campaign_manager = CampaignManager()

        first_name = self.subscription.get("primary_contact").get("first_name").title()
        last_name = self.subscription.get("primary_contact").get("last_name").title()
        current_cycle = self.subscription.get("cycles")[-1]
        cycle_uuid = current_cycle.get("cycle_uuid")
        subscription_uuid = self.subscription.get("subscription_uuid")

        dhs_contact = self.dhs_contact

        # Putting .split on the start and end date because sometimes it comes formatted with a float at the end.
        if not isinstance(self.subscription.get("start_date"), datetime):
            start_date = datetime.strptime(
                self.subscription.get("start_date").split(".")[0], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%d %B, %Y")
        else:
            start_date = self.subscription.get("start_date")

        if self.notification["path"] == "subscription_stopped":
            end_date = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
        else:
            end_date = self.subscription.get("end_date")

        if end_date is not None:
            if not isinstance(end_date, datetime):
                end_date = datetime.strptime(
                    end_date.split(".")[0], "%Y-%m-%dT%H:%M:%S"
                )

        # Required to convert list of UUID's to strings for DB query
        uuid_string_list = list(
            map(str, self.subscription.get("templates_selected_uuid_list", []))
        )
        templates = template_service.get_list(
            parameters={"template_uuid": {"$in": uuid_string_list}}
        )
        phishing_email = list(
            filter(
                lambda x: x.name == self.subscription.get("sending_profile_name"),
                campaign_manager.get_sending_profile(),
            )
        )[0].from_address

        email_count = len(self.subscription.get("target_email_list"))

        return {
            "first_name": first_name,
            "last_name": last_name,
            "start_date": start_date,
            "end_date": end_date,
            "cycle_uuid": cycle_uuid,
            "subscription_uuid": subscription_uuid,
            "templates": templates,
            "phishing_email": phishing_email,
            "email_count": email_count,
            "dhs_contact": dhs_contact,
            "phishing_domain": phishing_email.split("@")[-1].replace(">", ""),
            "x_gophish_contact": settings.DEFAULT_X_GOPHISH_CONTACT,
        }

    def _set_to(self):
        recipient = self.subscription.get("primary_contact").get("email")
        return [
            f"{self.context['first_name']} {self.context['last_name']} <{recipient}>"
        ]

    def _set_bcc(self):
        dhs_contact = self.dhs_contact.get("email")

        bcc = [f"DHS <{dhs_contact}>"] if dhs_contact else []

        if settings.DEBUG == 0:
            bcc.extend(settings.EXTRA_BCC_EMAILS)

        return bcc

    def _set_notification(self, message_type):
        return {
            "monthly_report": {
                "subject": "CISA Phishing Subscription Status Report",
                "path": "monthly_report",
                "link": "monthly",
                "type": "Monthly",
            },
            "cycle_report": {
                "subject": "CISA Phishing Subscription Cycle Report",
                "path": "cycle_report",
                "link": "cycle",
                "type": "Cycle",
            },
            "yearly_report": {
                "subject": "CISA Phishing Subscription Yearly Report",
                "path": "yearly_report",
                "link": "yearly",
                "type": "Yearly",
            },
            "subscription_started": {
                "subject": "CISA Phishing Subscription Started",
                "path": "subscription_started",
                "link": None,
                "type": "Cycle Start Notification",
            },
            "subscription_stopped": {
                "subject": "CISA Phishing Subscription Stopped",
                "path": "subscription_stopped",
                "link": None,
                "type": "Cycle Complete",
            },
        }.get(message_type)
