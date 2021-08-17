"""Phishing tasks."""
# Standard Python Libraries
from datetime import datetime
from itertools import groupby
import logging

# Third-Party Libraries
from flask import render_template_string
from utils.emails import Email, get_email_context, get_from_address

# cisagov Libraries
from api.app import app
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
            context = get_email_context(customer=customer, target=target)
            email_body = render_template_string(template["html"], **context)
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
        },
        data={"processing": True},
    )
