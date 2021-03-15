"""Webhook Utils."""


def check_opened_event(timeline, email):
    """Check Email Opened Event."""
    opened = list(
        filter(
            lambda x: x["email"] == email and x["message"] == "Email Opened", timeline
        )
    )
    return bool(opened)
