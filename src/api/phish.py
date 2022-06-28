"""Phishing tasks."""
# Standard Python Libraries
import base64
from datetime import datetime
from itertools import groupby

# Third-Party Libraries
from flask import render_template_string

# cisagov Libraries
from api.app import app
from api.manager import (
    CustomerManager,
    CycleManager,
    SendingProfileManager,
    SubscriptionManager,
    TargetManager,
    TemplateManager,
)
from utils.emails import Email, clean_from_address, get_email_context, get_from_address
from utils.logging import setLogger

logger = setLogger(__name__)


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
        cycle_ids = get_active_cycles()
        if not cycle_ids:
            logger.info("No cycles to process")
            return
        while True:
            target = get_target(cycle_ids)
            if not target:
                logger.info("No more targets found.")
                break
            targets.append(target)
        if targets:
            process_targets(targets)
            logger.info("Processed all targets.")
        else:
            logger.info("No targets to send to.")


def get_active_cycles():
    """Get active cycle ids."""
    active_cycles = cycle_manager.all(params={"active": True}, fields=["_id"])
    if not active_cycles:
        return None
    return [c["_id"] for c in active_cycles]


def get_target(cycle_ids):
    """Get and update target for processing."""
    return target_manager.find_one_and_update(
        params={
            "send_date": {"$lt": datetime.utcnow()},
            "sent": {"$in": [False, None]},
            "cycle_id": {"$in": cycle_ids},
        },
        data={"sent": True},
        fields=[
            "_id",
            "cycle_id",
            "subscription_id",
            "template_id",
            "email",
            "first_name",
            "last_name",
            "position",
        ],
    )


def process_targets(targets):
    """Process cycle targets for sending."""
    for subscription_id, subscription_targets in groupby(
        targets, key=lambda x: x["subscription_id"]
    ):
        try:
            process_subscription_targets(subscription_id, subscription_targets)
        except Exception as e:
            logger.exception(e)
            for t in subscription_targets:
                target_manager.update(
                    document_id=t["_id"],
                    data={
                        "error": str(e),
                        "sent_date": datetime.utcnow(),
                    },
                )


def process_subscription_targets(subscription_id, targets):
    """Process subscription targets."""
    # Get subscription for sending profile and customer
    subscription = subscription_manager.get(
        document_id=subscription_id,
        fields=["_id", "sending_profile_id", "customer_id"],
    )

    # Get cycle for phish header
    cycle = cycle_manager.get(
        filter_data={
            "subscription_id": subscription_id,
            "active": True,
        },
        fields=["phish_header"],
    )

    # Get sending profile to send emails
    sending_profile = sending_profile_manager.get(
        document_id=subscription["sending_profile_id"]
    )

    # Add headers to sending profile
    add_phish_headers(cycle, sending_profile)

    # Get customer for email context
    customer = customer_manager.get(document_id=subscription["customer_id"])

    # Login to subscription SMTP server
    subscription_email = Email(sending_profile)

    # Group targets by template
    for template_id, targets in groupby(targets, key=lambda x: x["template_id"]):
        template = template_manager.get(document_id=template_id)
        # If template has a different SMTP Server defined, connect to that one
        template_email = None
        template_sp = None
        if template.get("sending_profile_id"):
            template_sp = sending_profile_manager.get(template["sending_profile_id"])
            add_phish_headers(cycle, template_sp)
            template_email = Email(sending_profile=template_sp)

        for target in targets:
            try:
                if template_email:
                    process_target(
                        template_sp,
                        target,
                        customer,
                        template,
                        subscription,
                        template_email,
                    )
                else:
                    process_target(
                        sending_profile,
                        target,
                        customer,
                        template,
                        subscription,
                        subscription_email,
                    )
            except Exception as e:
                logger.exception(e)
                target["error"] = str(e)
            finally:
                target_manager.update(
                    document_id=target["_id"],
                    data={"sent": True, "sent_date": datetime.utcnow()},
                )

    cycle_manager.update(
        document_id=target["cycle_id"],
        data={
            "processing": False,
            "dirty_stats": True,
        },
    )


def process_target(
    sending_profile, target, customer, template, subscription, email: Email
):
    """Send email to target."""
    tracking_info = get_tracking_info(
        sending_profile,
        target["cycle_id"],
        target["_id"],
        subscription,
    )
    context = get_email_context(
        customer=customer,
        target=target,
        url=tracking_info["click"],
    )

    html = template["html"] + tracking_info["open"]

    email_body = render_template_string(html, **context)
    from_address = render_template_string(
        get_from_address(sending_profile, template["from_address"]), **context
    )
    from_address = clean_from_address(from_address)
    subject = render_template_string(template["subject"], **context)
    email.send(
        to_recipients=[target["email"]],
        from_email=from_address,
        subject=subject,
        body=email_body,
    )


def get_landing_url(sending_profile, subscription):
    """Get url for landing page."""
    if subscription.get("landing_domain"):
        return f"http://{subscription['landing_domain']}"

    return f"http://{sending_profile['landing_page_domain']}"


def get_tracking_info(sending_profile, cycle_id, target_id, subscription):
    """Get tracking html for opens and link for clicks."""
    tracking_id = get_tracking_id(cycle_id, target_id)
    url = get_landing_url(sending_profile, subscription)
    return {
        "open": f'<img width="1px" heigh="1px" alt="" src="{url}/o/{tracking_id}/"/>',
        "click": f"{url}/c/{tracking_id}/",
    }


def get_tracking_id(cycle_id, target_id):
    """
    Get url to embed into template.

    Base64 encodes cycle id with the target id.
    """
    data = f"{cycle_id}_{target_id}"
    urlsafe_bytes = base64.urlsafe_b64encode(data.encode("utf-8"))
    return str(urlsafe_bytes, "utf-8")


def decode_tracking_id(s):
    """Decode base64 url into cycle id and target id."""
    return str(base64.urlsafe_b64decode(s), "utf-8").split("_")


def add_phish_headers(cycle, sending_profile):
    """Add Cisa-Phish header to phishing emails."""
    if not sending_profile.get("headers"):
        sending_profile["headers"] = []
    sending_profile["headers"].append(
        {
            "key": "Cisa-Phish",
            "value": cycle["phish_header"],
        }
    )
