"""GoPhish API Manager."""

# Standard Python Libraries
import logging
import re
import json
from typing import Dict
import random

# Third-Party Libraries
from bs4 import BeautifulSoup
from config import settings
from faker import Faker
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# cisagov Libraries
# GoPhish Libraries
from gophish import Gophish
from gophish.models import SMTP, Campaign, Group, Page, Template, User

faker = Faker()
vectorizer = TfidfVectorizer()


class TemplateManager:
    """Template calculator."""

    def __init__(self):
        """Init."""
        pass

    def preprocess_keywords(self, url: str, keywords: str):
        """
        Preprocess_keywords.

        Extract text from the given url.
        Concatenate a bag of keywords from user input
        clean text by converting words to lower case,
        removing punctuation and numbers
        """
        web_text = ""
        if url is not None:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url
            headers = {"Content-Type": "text/html"}
            resp = requests.get(url, headers=headers)
            soup = BeautifulSoup(resp.text, "lxml")
            web_text = re.sub(r"[^A-Za-z]+", " ", soup.get_text().lower())

        if keywords is None:
            keywords = ""

        return web_text + keywords

    def randomize_templates(self, template_data):
        return random.sample(
            list(template_data.keys()), len(list(template_data.keys()))
        )

    def get_templates(self, url: str, keywords: str, template_data):
        """
        Get Templates.

        Return highest relative templates using tf-idf and cosine similarity algorithms
        based on customer keywords
        """
        if not url or not keywords:
            return self.randomize_templates(template_data)

        template_uuids = [*template_data.keys()]
        preprocessed_data = [self.preprocess_keywords(url, keywords)] + [
            *template_data.values()
        ]

        docs_tfidf = vectorizer.fit_transform(preprocessed_data)
        cosine_similarities = cosine_similarity(docs_tfidf[:1], docs_tfidf).flatten()
        cosine_similarities = cosine_similarities[1:]

        context = [
            i
            for _, i in sorted(
                dict(zip(cosine_similarities, template_uuids)).items(), reverse=True
            )
        ]

        return context


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
        target_list: Dict = None,
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
            campaign = self.gp_api.campaigns.get(campaign_id=campaign_id)
        else:
            campaign = self.gp_api.campaigns.get()
        return campaign

    def get_campaign_summary(self, campaign_id: int = None):
        if campaign_id:
            summary = self.gp_api.campaigns.summary(campaign_id=campaign_id)
        else:
            summary = self.gp_api.campaigns.summary()
        return summary.as_dict()

    def get_sending_profile(self, smtp_id: int = None):
        """GET Sending Profile."""
        if smtp_id:
            sending_profile = self.gp_api.smtp.get(smtp_id=smtp_id)
        else:
            sending_profile = self.gp_api.smtp.get()
        return sending_profile

    def get_email_template(self, template_id: int = None):
        """GET Email Temp."""
        if template_id:
            template = self.gp_api.templates.get(template_id=template_id)
        else:
            template = self.gp_api.templates.get()
        return template

    def get_landing_page(self, page_id: int = None):
        """GET landingpage."""
        if page_id:
            landing_page = self.gp_api.pages.get(page_id=page_id)
        else:
            landing_page = self.gp_api.pages.get()
        return landing_page

    def get_user_group(self, group_id: int = None):
        """GET User group."""
        if group_id:
            user_group = self.gp_api.groups.get(group_id=group_id)
        else:
            user_group = self.gp_api.groups.get()
        return user_group

    # Delete methods
    def delete_campaign(self, campaign_id: int):
        """DELETE Campaign."""
        if campaign_id:
            status = self.gp_api.campaigns.delete(campaign_id=campaign_id)
        else:
            status: None
        return status

    def delete_sending_profile(self, smtp_id: int):
        """DELETE Sending Profile."""
        if smtp_id:
            status = self.gp_api.smtp.delete(smtp_id=smtp_id)
        else:
            status = None
        return status

    def delete_email_template(self, template_id: int):
        """DELETE Email Temp."""
        if template_id:
            status = self.gp_api.templates.delete(template_id=template_id)
        else:
            status = None
        return status

    def delete_landing_page(self, page_id: int):
        """DELETE landingpage."""
        if page_id:
            status = self.gp_api.pages.delete(page_id=page_id)
        else:
            status = None
        return status

    def delete_user_group(self, group_id: int):
        """DELETE User group."""
        if group_id:
            try:
                status = self.gp_api.groups.delete(group_id=group_id)
            except Exception:
                status = None
        else:
            status = None
        return status

    def send_test_email(self, test_string):
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
        if campaign_id:
            status = self.gp_api.campaigns.complete(campaign_id=campaign_id)
        else:
            status: None
        return status
