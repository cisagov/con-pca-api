"""Phishing tasks."""
# Standard Python Libraries
import base64
from datetime import datetime
from itertools import groupby
import logging

# Third-Party Libraries
from flask import render_template_string

# cisagov Libraries
from api.app import app
from api.config import LANDING_SUBDOMAIN
from api.manager import (
    CustomerManager,
    CycleManager,
    SendingProfileManager,
    SubscriptionManager,
    TargetManager,
    TemplateManager,
)
from utils.emails import Email, get_email_context, get_from_address

customer_manager = CustomerManager()
cycle_manager = CycleManager()
sending_profile_manager = SendingProfileManager()
subscription_manager = SubscriptionManager()
target_manager = TargetManager()
template_manager = TemplateManager()


def emails_job():
    """Email job to run every minute."""
    with app.app_context():
        targets = []
        cycle_uuids = get_active_cycles()
        if not cycle_uuids:
            logging.info("No cycles to process")
            return
        while True:
            target = get_target(cycle_uuids)
            if not target:
                logging.info("No more targets found.")
                break
            targets.append(target)
        if targets:
            process_targets(targets)
            logging.info("Processed all targets.")
        else:
            logging.info("No targets to send to.")


def get_active_cycles():
    """Get active cycle uuids."""
    active_cycles = cycle_manager.all(params={"active": True}, fields=["cycle_uuid"])
    if not active_cycles:
        return None
    uuids = [c["cycle_uuid"] for c in active_cycles]
    return uuids


def get_target(cycle_uuids):
    """Get and update target for processing."""
    return target_manager.find_one_and_update(
        params={
            "send_date": {"$lt": datetime.utcnow()},
            "sent": {"$in": [False, None]},
            "cycle_uuid": {"$in": cycle_uuids},
        },
        data={"sent": True},
        fields=[
            "target_uuid",
            "cycle_uuid",
            "subscription_uuid",
            "template_uuid",
            "email",
            "first_name",
            "last_name",
            "position",
        ],
    )


def process_targets(targets):
    """Process cycle targets for sending."""
    for subscription_uuid, subscription_targets in groupby(
        targets, key=lambda x: x["subscription_uuid"]
    ):
        try:
            process_subscription_targets(subscription_uuid, subscription_targets)
        except Exception as e:
            logging.exception(e)
            for t in subscription_targets:
                target_manager.update(
                    uuid=t["target_uuid"],
                    data={
                        "error": str(e),
                        "sent_date": datetime.utcnow(),
                    },
                )


def process_subscription_targets(subscription_uuid, targets):
    """Process subscription targets."""
    # Get subscription for sending profile and customer
    subscription = subscription_manager.get(
        uuid=subscription_uuid,
        fields=["sending_profile_uuid", "customer_uuid"],
    )

    # Get sending profile to send emails
    sending_profile = sending_profile_manager.get(
        uuid=subscription["sending_profile_uuid"]
    )
    # Get customer for email context
    customer = customer_manager.get(uuid=subscription["customer_uuid"])

    # Login to subscription SMTP server
    subscription_email = Email(sending_profile)

    # Group targets by template
    for template_uuid, targets in groupby(targets, key=lambda x: x["template_uuid"]):
        template = template_manager.get(uuid=template_uuid)
        # If template has a different SMTP Server defined, connect to that one
        template_email = None
        template_sp = None
        if template.get("sending_profile_uuid"):
            template_sp = sending_profile_manager.get(template["sending_profile_uuid"])
            template_email = Email(sending_profile=template_sp)

        for target in targets:
            try:
                if template_email:
                    process_target(
                        template_sp, target, customer, template, template_email
                    )
                else:
                    process_target(
                        sending_profile, target, customer, template, subscription_email
                    )
            except Exception as e:
                logging.exception(e)
                target["error"] = str(e)
            finally:
                target_manager.update(
                    uuid=target["target_uuid"],
                    data={"sent": True, "sent_date": datetime.utcnow()},
                )

    cycle_manager.update(
        uuid=target["cycle_uuid"],
        data={
            "processing": False,
            "dirty_stats": True,
        },
    )


def process_target(sending_profile, target, customer, template, email):
    """Send email to target."""
    tracking_info = get_tracking_info(
        sending_profile,
        target["cycle_uuid"],
        target["target_uuid"],
    )
    context = get_email_context(
        customer=customer,
        target=target,
        url=tracking_info["click"],
    )

    html = template["html"] + tracking_info["open"]

    email_body = render_template_string(html, **context)
    from_address = get_from_address(sending_profile, template["from_address"])
    email.send(
        to_email=target["email"],
        from_email=from_address,
        subject=template["subject"],
        body=email_body,
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
