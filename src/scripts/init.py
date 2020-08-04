# Standard Python Libraries
import os
import requests
import json
import time

# Third Party Libraries
from gophish import Gophish
from gophish.models import SMTP, Page, Webhook

API_KEY = os.environ.get("GP_API_KEY")
URL = os.environ.get("GP_URL")
API = Gophish(API_KEY, host=URL, verify=False)
LOCAL_URL = "http://localhost:8000"


SENDING_PROFILES = [
    {
        "name": "SMTP",
        "host": os.environ.get("GP_SMTP_HOST"),
        "from_address": os.environ.get("GP_SMTP_FROM"),
        "username": os.environ.get("GP_SMTP_USER"),
        "password": os.environ.get("GP_SMTP_PASS"),
    },
    {
        "name": "REPORTING",
        "host": "TEST",
        "from_address": "TEST@TEST.TEST",
        "username": "TESTUSER",
        "password": "TESTPASSWORD",
    },
]

LANDING_PAGES = [
    {
        "name": "Phished",
        "html": "",
    },
]

WEBHOOKS = [
    {
        "name": "con-pca-webhook",
        "url": os.environ.get("WEBHOOK_URL"),
        "is_active": True,
        "secret": os.environ.get("LOCAL_API_KEY"),
    }
]


def create_sending_profile(profiles):
    """
    Create Gophish sending profiles
    """
    existing_names = {smtp.name for smtp in API.smtp.get()}

    for profile in profiles:
        profile_name = profile.get("name")
        if profile_name in existing_names:
            print(f"Sending profile, {profile_name}, already exists.. Skipping")
            continue
        smtp = SMTP(name=profile_name)
        smtp.host = profile.get("host")
        smtp.from_address = profile.get("from_address")
        smtp.username = profile.get("username")
        smtp.password = profile.get("password")
        smtp.interface_type = "SMTP"
        smtp.ignore_cert_errors = True
        smtp = API.smtp.post(smtp)
        print(f"Sending profile with id: {smtp.id} has been created")


def create_landing_page(pages):
    """
    Create a Gophish landing page
    """
    existing_names = {smtp.name for smtp in API.pages.get()}
    for page in pages:
        page_name = page.get("name")
        if page_name in existing_names:
            print(f"Landing page, {page_name}, already exists.. Skipping")
            continue
        landing_page = Page(name=page_name, html=page.get("html"))
        landing_page = API.pages.post(landing_page)
        print(f"Landing page with id: {landing_page.id} has been created")

def readinLandingHtml(path):
    """
    read in default landing page template
    """
    

def create_webhook(webhooks):
    existing_names = {webhook.name for webhook in API.webhooks.get()}

    for webhook in webhooks:
        if webhook["name"] in existing_names:
            print(f"Webhook, {webhook['name']}, already exists.. Skipping")
            continue
        response = API.webhooks.post(
            Webhook(
                name=webhook["name"],
                url=webhook["url"],
                is_active=webhook["is_active"],
                secret=webhook["secret"],
            )
        )
        print(f"Webhook with id: {response.id} has been created")


def create_templates():
    existing_names = [
        t["name"]
        for t in requests.get(
            f"{LOCAL_URL}/api/v1/templates", headers=get_headers(), verify=False
        ).json()
    ]

    templates = load_file("data/templates.json") + load_file("data/landing_pages.json")

    for template in templates:
        if not template["name"] in existing_names:
            template["deception_score"] = template["complexity"]
            resp = requests.post(
                f"{LOCAL_URL}/api/v1/templates/",
                json=template,
                headers=get_headers(),
                verify=False,
            )

            if resp.status_code == 409:
                print(f"Template, {template['name']}, already exists.. Skipping")
                continue

            resp.raise_for_status()
            resp_json = resp.json()
            if resp_json.get("error"):
                print(f"Template Creation error: {resp_json}")
            else:
                print(
                    f"Template with uuid: {resp_json['template_uuid']} has been created"
                )

        else:
            print(f"Template, {template['name']}, already exists.. Skipping")


def create_tags():
    tags = load_file("data/tags.json")
    existing_tags = [
        t["tag"]
        for t in requests.get(
            f"{LOCAL_URL}/api/v1/tags/", headers=get_headers(), verify=False
        ).json()
    ]

    for tag in tags:
        if tag["tag"] not in existing_tags:
            resp = requests.post(
                f"{LOCAL_URL}/api/v1/tags/",
                json=tag,
                headers=get_headers(),
                verify=False,
            )
            resp.raise_for_status()
            resp_json = resp.json()
            if resp_json.get("error"):
                print(f"Tag Creation error: {resp_json}")
            else:
                print(
                    f"Tag with uuid {resp_json['tag_definition_uuid']} has been created"
                )
        else:
            print(f"Tag, {tag['tag']}, already exists.. Skipping")


def get_headers():
    return {"Authorization": os.environ.get("LOCAL_API_KEY")}


def wait_connection():
    for i in range(1, 15):
        try:
            requests.get(f"{LOCAL_URL}/", headers=get_headers(), verify=False)
            break
        except BaseException:
            print("Django API not yet running. Waiting...")
            time.sleep(5)

def load_default_landing_page():
    LANDING_PAGES[0]["html"]  = load_file_html("data/landing.html")

def load_file_html(data_file):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, data_file)
    with open(data_file, "r") as f:
        data = f.read()
    return data


def load_file(data_file):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, data_file)
    with open(data_file, "r") as f:
        data = json.load(f)
    return data


def main():
    print("Waiting for api to initialize")
    wait_connection()

    print("Step 1/5: Creating Sending Profiles")
    create_sending_profile(SENDING_PROFILES)
    print("Step 2/5: Creating Landing Pages")
    
    load_default_landing_page()
    create_landing_page(LANDING_PAGES)
    print("Step 3/5: Create Webhooks")
    create_webhook(WEBHOOKS)
    print("Step 4/5: Create Templates")
    create_templates()
    print("Step 5/5: Create Tags")
    create_tags()
    print("...Con-PCA Initialized...")
    return 0


if __name__ == "__main__":
   main()