"""GoPhish API Manager."""

# Standard Python Libraries
import json
import logging

# Third-Party Libraries

from faker import Faker

# GoPhish Libraries
from gophish import Gophish
from gophish.models import SMTP, Campaign, Group, Page, Template, User
import requests

# cisagov Libraries
from config import settings

faker = Faker()


class CampaignManager:
    """GoPhish API Manager. TODO: create put methods."""

    def __init__(self):
        """Init."""
        self.gp_api = Gophish(settings.GP_API_KEY, host=settings.GP_URL)

    # Create methods
    def create_campaign(
        self,
        campaign_name: str,
        smtp_name: str,
        page_name: str,
        user_group=None,
        email_template=None,
        launch_date=None,
        send_by_date=None,
    ):
        """Generate campaign Method."""
        smtp = SMTP(name=smtp_name)
        landing_page = Page(name=page_name)
        campaign = Campaign(
            name=campaign_name,
            groups=[user_group],
            page=landing_page,
            template=email_template,
            smtp=smtp,
            url=settings.PHISH_URL,
            launch_date=launch_date,
            send_by_date=send_by_date,
        )

        campaign = self.gp_api.campaigns.post(campaign)

        return campaign

    def create_sending_profile(
        self,
        name,
        username,
        password,
        host,
        interface_type,
        from_address,
        ignore_cert_errors,
        headers,
    ):
        """Create Sending Profile."""
        smtp = SMTP(
            name=name,
            username=username,
            password=password,
            host=host,
            interface_type=interface_type,
            from_address=from_address,
            ignore_cert_errors=ignore_cert_errors,
            headers=headers,
        )

        return self.gp_api.smtp.post(smtp=smtp)

    def put_sending_profile(self, sp):
        """Update Sending Profile."""
        return self.gp_api.smtp.put(smtp=sp)

    def create_email_template(self, name: str, template: str, subject: str, text=None):
        """Generate Email Templates."""
        template = "<html><head></head><body>" + template + "</body></html>"
        email_template = Template(name=name, subject=subject, html=template)
        if text is not None:
            email_template.text = text

        return self.gp_api.templates.post(email_template)

    def create_landing_page(self, name: str, template: str):
        """Generate Landing Page."""
        landing_page = Page(
            name=name, html=template, capture_credentials=False, capture_passwords=False
        )
        return self.gp_api.pages.post(landing_page)

    def put_landing_page(self, gp_id, name, html):
        """Modify Landing Page."""
        landing_page = Page(id=gp_id, name=name, html=html)
        return self.gp_api.pages.put(landing_page)

    def create_user_group(
        self,
        subscription_name: str,
        deception_level: int,
        index: int,
        target_list: list = [],
    ):
        """Generate User Group."""
        users = [
            User(
                first_name=target.get("first_name"),
                last_name=target.get("last_name"),
                email=target.get("email"),
                position=target.get("position"),
            )
            for target in target_list
        ]

        group_name = f"{subscription_name}.Targets.{deception_level}.{index}"

        target_group = Group(name=group_name, targets=users)

        return self.gp_api.groups.post(target_group)

    # Get methods
    def get_campaign(self, campaign_id: int = None):
        """GET Campaign."""
        if campaign_id:
            return self.gp_api.campaigns.get(campaign_id=campaign_id)
        return self.gp_api.campaigns.get()

    def get_sending_profile(self, smtp_id: int = None):
        """GET Sending Profile."""
        if smtp_id:
            return self.gp_api.smtp.get(smtp_id=smtp_id)
        return self.gp_api.smtp.get()

    def get_email_template(self, template_id: int = None):
        """GET Email Temp."""
        if template_id:
            return self.gp_api.templates.get(template_id=template_id)
        return self.gp_api.templates.get()

    def get_landing_page(self, page_id: int = None):
        """GET landingpage."""
        if page_id:
            return self.gp_api.pages.get(page_id=page_id)
        return self.gp_api.pages.get()

    def get_user_group(self, group_id: int = None):
        """GET User group."""
        if group_id:
            return self.gp_api.groups.get(group_id=group_id)
        return self.gp_api.groups.get()

    # Delete methods
    def delete_campaign(self, campaign_id: int):
        """DELETE Campaign."""
        if campaign_id:
            return self.gp_api.campaigns.delete(campaign_id=campaign_id)

    def delete_sending_profile(self, smtp_id: int):
        """DELETE Sending Profile."""
        if smtp_id:
            return self.gp_api.smtp.delete(smtp_id=smtp_id)

    def delete_email_template(self, template_id: int):
        """DELETE Email Temp."""
        if template_id:
            return self.gp_api.templates.delete(template_id=template_id)

    def delete_landing_page(self, page_id: int):
        """DELETE landingpage."""
        if page_id:
            return self.gp_api.pages.delete(page_id=page_id)

    def delete_user_group(self, group_id: int):
        """DELETE User group."""
        if group_id:
            try:
                return self.gp_api.groups.delete(group_id=group_id)
            except Exception:
                return None

    def send_test_email(self, test_string):
        """Send Test Email."""
        try:
            # sending post request and saving response as response object
            url = settings.GP_URL + "api/util/send_test_email"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(settings.GP_API_KEY),
            }
            r = requests.post(url=url, json=test_string, headers=headers)
            # extracting response text
            return json.loads(r.text)
        except Exception as e:
            logging.exception(e)
            if hasattr(e, "message"):
                return e.message
            else:
                return e

    # Other Methods
    def complete_campaign(self, campaign_id: int):
        """Complete Campaign."""
        if campaign_id:
            return self.gp_api.campaigns.complete(campaign_id=campaign_id)
