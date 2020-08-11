from notifications.views import EmailSender
from api.utils.subscription.subscriptions import send_start_notification
from api.utils.subscription import actions
from datetime import datetime


def start_subscription_email(subscription):
    send_start_notification(subscription)


def start_subscription_cycle(subscription):
    """
    Create the next subscription cycle
    """
    actions.start_subscription(
        subscription_uuid=subscription.get("subscription_uuid"), new_cycle=True
    )
    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }
    return context


def email_subscription_monthly(subscription):
    """
    schedule the next monthly subscription report email
    """
    # Send email
    sender = EmailSender(subscription, "monthly_report", datetime.now().isoformat())
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context


def email_subscription_cycle(subscription):
    """
    schedule the next subscription cycle report email
    """
    # Send email
    sender = EmailSender(subscription, "cycle_report", datetime.now().isoformat())
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context


def email_subscription_yearly(subscription):
    """
    schedule the next yearly subscription report email
    """
    # Send email
    sender = EmailSender(subscription, "yearly_report", datetime.now().isoformat())
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context
