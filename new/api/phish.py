"""Phishing tasks."""
# Standard Python Libraries
import base64
from datetime import datetime
from itertools import groupby
import logging

# Third-Party Libraries
from flask import render_template_string
from utils.emails import Email, get_email_context, get_from_address

# cisagov Libraries
from api.app import app
from api.config import LANDING_SUBDOMAIN
from api.manager import (
    CustomerManager,
    CycleManager,
    SendingProfileManager,
    SubscriptionManager,
    TemplateManager,
)

customer_manager = CustomerManager()
cycle_manager = CycleManager()
sending_profile_manager = SendingProfileManager()
subscription_manager = SubscriptionManager()
template_manager = TemplateManager()


def emails_job():
    """Email job to run every minute."""
    with app.app_context():
        while True:
            cycle = get_cycle()
            if not cycle:
                logging.info("No more cycles to process.")
                break
            process_cycle(cycle)


def process_cycle(cycle):
    """Process cycle targets for sending."""
    # Get subscription for sending profile and customer
    subscription = subscription_manager.get(
        uuid=cycle["subscription_uuid"],
        fields=["sending_profile_uuid", "customer_uuid"],
    )
    # Get sending profile to send emails
    sending_profile = sending_profile_manager.get(
        uuid=subscription["sending_profile_uuid"]
    )
    # Get customer for email context
    customer = customer_manager.get(uuid=subscription["customer_uuid"])

    # Filter out targets that need sent to
    targets = list(
        filter(
            lambda x: x["send_date"].timestamp() < datetime.utcnow().timestamp()
            and not x.get("sent"),
            cycle["targets"],
        )
    )

    # Group targets by template
    for template_uuid, targets in groupby(targets, key=lambda x: x["template_uuid"]):
        template = template_manager.get(uuid=template_uuid)
        sp = (
            sending_profile_manager.get(template["sending_profile_uuid"])
            if template.get("sending_profile_uuid")
            else sending_profile
        )
        email = Email(sending_profile=sp)
        for target in targets:
            tracking_info = get_tracking_info(
                sp,
                cycle["cycle_uuid"],
                target["target_uuid"],
            )
            context = get_email_context(
                customer=customer,
                target=target,
                url=tracking_info["click"],
            )

            html = template["html"] + tracking_info["open"]

            email_body = render_template_string(html, **context)
            from_address = get_from_address(sp, template["from_address"])
            email.send(
                to_email=target["email"],
                from_email=from_address,
                subject=template["subject"],
                body=email_body,
            )
            target["sent"] = True
            target["sent_date"] = datetime.utcnow()
            cycle_manager.update_in_list(
                uuid=cycle["cycle_uuid"],
                field="targets.$",
                data=target,
                params={"targets.target_uuid": target["target_uuid"]},
            )

    cycle_manager.update(uuid=cycle["cycle_uuid"], data={"processing": False})


def get_cycle():
    """Get and update cycle for processing."""
    return cycle_manager.find_one_and_update(
        params={
            "targets": {
                "$elemMatch": {
                    "send_date": {"$lt": datetime.utcnow()},
                    "sent": {"$in": [False, None]},
                }
            },
            "processing": {"$in": [False, None]},
            "active": True,
        },
        data={"processing": True},
    )


def get_landing_url(sending_profile):
    """Get url for landing page."""
    sp_domain = (
        sending_profile["from_address"].split("<")[-1].split("@")[1].replace(">", "")
    )
    return f"http://{LANDING_SUBDOMAIN}.{sp_domain}"


def get_tracking_info(sending_profile, cycle_uuid, target_uuid):
    """Get tracking html for opens and link for clicks."""
    tracking_id = get_tracking_id(cycle_uuid, target_uuid)
    url = get_landing_url(sending_profile)
    return {
        "open": f'<img width="1px" heigh="1px" alt="" src="{url}/o/{tracking_id}/"/>',
        "click": f"{url}/c/{tracking_id}/",
    }


def get_tracking_id(cycle_uuid, target_uuid):
    """
    Get url to embed into template.

    Base64 encodes cycle uuid with the target uuid.
    """
    data = f"{cycle_uuid}_{target_uuid}"
    urlsafe_bytes = base64.urlsafe_b64encode(data.encode("utf-8"))
    return str(urlsafe_bytes, "utf-8")


def decode_tracking_id(s):
    """Decode base64 url into cycle uuid and target uuid."""
    return str(base64.urlsafe_b64decode(s), "utf-8").split("_")
