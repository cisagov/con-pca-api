"""Safelist testing utils."""
# Standard Python Libraries
from datetime import datetime
import logging
from uuid import uuid4

# Third-Party Libraries
from flask import redirect
from flask.templating import render_template_string

# cisagov Libraries
from api.manager import (
    CustomerManager,
    LandingPageManager,
    SendingProfileManager,
    SubscriptionManager,
    TemplateManager,
)
from api.phish import add_phish_headers, get_tracking_info
from utils.emails import Email, clean_from_address, get_email_context, get_from_address
from utils.request import get_landing_page, get_timeline_entry

customer_manager = CustomerManager()
landing_page_manager = LandingPageManager()
sending_profile_manager = SendingProfileManager()
subscription_manager = SubscriptionManager()
template_manager = TemplateManager()


def test_subscription(subscription_id, contacts):
    """Test a subscription for safelisting."""
    # Get subscription for sending profile, customer and templates
    subscription = subscription_manager.get(
        document_id=subscription_id,
        fields=[
            "_id",
            "sending_profile_id",
            "customer_id",
            "templates_selected",
            "phish_header",
        ],
    )

    # Get subscription customer for emails
    customer = customer_manager.get(document_id=subscription["customer_id"])

    # Get templates for subscription
    templates = template_manager.all(
        params={"_id": {"$in": subscription["templates_selected"]}},
        fields=[
            "_id",
            "deception_score",
            "from_address",
            "html",
            "landing_page_id",
            "name",
            "sending_profile_id",
            "subject",
        ],
    )

    # Get sending profile to send emails
    sending_profile = sending_profile_manager.get(
        document_id=subscription["sending_profile_id"]
    )

    try:
        # Add headers to sending profile
        add_phish_headers(subscription, sending_profile)

        # Login to subscription SMTP server
        subscription_email = Email(sending_profile)
    except Exception as e:
        return str(e), 400

    # Instantiate variable to store results
    test_results = []

    for template in templates:
        # If template has a different SMTP Server defined, connect to that one
        template_email = None
        template_sp = None
        if template.get("sending_profile_id"):
            template_sp = sending_profile_manager.get(template["sending_profile_id"])
            add_phish_headers(subscription, template_sp)
            template_email = Email(sending_profile=template_sp)

        for contact in contacts:
            print(f"Sending {contact['email']} template {template['name']}")
            test_uuid = str(uuid4())
            contact["test_uuid"] = test_uuid
            result = {
                "test_uuid": test_uuid,
                "email": contact["email"],
                "first_name": contact["first_name"],
                "last_name": contact["last_name"],
                "template": template,
                "sent_date": datetime.utcnow(),
                "sent": True,
                "opened": False,
                "error": "",
            }
            try:
                if template_email:
                    process_contact(
                        template_sp,
                        subscription,
                        contact,
                        customer,
                        template,
                        template_email,
                    )
                else:
                    process_contact(
                        sending_profile,
                        subscription,
                        contact,
                        customer,
                        template,
                        subscription_email,
                    )
                status_code = 200
            except Exception as e:
                logging.exception(e)
                result["sent"] = False
                result["error"] = str(e)
                status_code = 400
            finally:
                test_results.append(result)

    subscription_manager.update(
        document_id=subscription["_id"],
        data={
            "test_results": test_results,
        },
    )
    return test_results, status_code


def process_contact(
    sending_profile, subscription, contact, customer, template, email: Email
):
    """Send test to contact."""
    # Get tracking info for opens/clicks
    tracking_info = get_tracking_info(
        sending_profile,
        f"test_{subscription['_id']}",
        contact["test_uuid"],
        subscription,
    )
    context = get_email_context(
        customer=customer,
        target=contact,
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
        to_recipients=[contact["email"]],
        from_email=from_address,
        subject=subject,
        body=email_body,
    )


def process_click_test(subscription_id, contact_id):
    """Process a click from the landing page."""
    subscription = subscription_manager.get(
        document_id=subscription_id,
        fields=["test_results", "customer_id", "landing_page_url"],
    )
    contact = next(
        filter(lambda x: x["test_uuid"] == contact_id, subscription["test_results"])
    )
    contact["timeline"] = contact.get("timeline", [])
    if len(contact["timeline"]) < 10:
        contact["timeline"].append(get_timeline_entry("clicked"))
    contact["clicked"] = True
    contact["opened"] = True
    subscription_manager.update_in_list(
        document_id=subscription_id,
        field="test_results.$",
        data=contact,
        params={"test_results.test_uuid": contact_id},
    )

    # If a landing page url exists for the subscription, redirect to it after click has been tracked
    if subscription.get("landing_page_url"):
        return redirect(subscription["landing_page_url"], 302)

    # Get landing page
    landing_page = get_landing_page(
        subscription=subscription, template_id=contact["template"]["_id"]
    )

    # Get customer
    customer = customer_manager.get(document_id=subscription["customer_id"])

    # Get Jinja template context
    context = get_email_context(target=contact, customer=customer)

    return render_template_string(landing_page["html"], **context)


def process_open_test(subscription_id, contact_id):
    """Process an open request."""
    subscription = subscription_manager.get(
        document_id=subscription_id, fields=["test_results"]
    )
    contact = next(
        filter(lambda x: x["test_uuid"] == contact_id, subscription["test_results"])
    )
    contact["timeline"] = contact.get("timeline", [])
    if len(contact["timeline"]) < 10:
        contact["timeline"].append(get_timeline_entry("opened"))
    contact["opened"] = True
    subscription_manager.update_in_list(
        document_id=subscription_id,
        field="test_results.$",
        data=contact,
        params={"test_results.test_uuid": contact_id},
    )
