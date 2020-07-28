"""Utils for notification service."""

# Standard Libraries


def get_notification(message_type):
    """
    Get notification.

    Parses out the type of notificartion.
    """
    if message_type == "monthly_report":
        subject = "DHS CISA Phishing Subscription Status Report"
        path = "monthly_report"
        link = "monthly"
    elif message_type == "cycle_report":
        subject = "DHS CISA Phishing Subscription Cycle Report"
        path = "cycle_report"
        link = "cycle"
    elif message_type == "yearly_report":
        subject = "DHS CISA Phishing Subscription Yearly Report"
        path = "yearly_report"
        link = "yearly"
    elif message_type == "subscription_started":
        subject = "DHS CISA Phishing Subscription Started"
        path = "subscription_started"
        link = None
    elif message_type == "subscription_stopped":
        subject = "DHS CISA Phishing Subscription Stopped"
        path = "subscription_stopped"
        link = None
    else:
        subject = ""
        path = ""
        link = ""
    return subject, path, link
