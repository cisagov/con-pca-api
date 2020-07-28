# Third-Party Libraries
from api.utils.subscription import actions
from notifications.views import ReportsEmailSender


def start_subscription_cycle(subscription):
    """
    Create the next subscription cycle
    """
    actions.new_subscription_cycle(subscription.get("subscription_uuid"))
    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }
    return context


def email_subscription_monthly(subscription):
    """
    schedule the next monthly subscription report email
    """
    # Send email
    sender = ReportsEmailSender(subscription, "monthly_report")
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
    sender = ReportsEmailSender(subscription, "cycle_report")
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
    sender = ReportsEmailSender(subscription, "yearly_report")
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context
