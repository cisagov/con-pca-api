"""Mailgun utils."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
import requests  # type: ignore
from requests.exceptions import HTTPError  # type: ignore

# cisagov Libraries
from api.config.environment import MAILGUN_API_KEY
from api.manager import FailedEmailManager, SendingProfileManager
from utils.logging import setLogger

logger = setLogger(__name__)

sending_profile_manager = SendingProfileManager()
failed_email_manager = FailedEmailManager()


def get_message_events(domain, api_key, message_id):
    """Get events for domain from mailgun api."""
    resp = requests.get(
        f"https://api.mailgun.net/v3/{domain}/events",
        auth=("api", api_key),
        params={"message-id": message_id},
    )
    resp.raise_for_status()
    events = resp.json()
    return [e["event"] for e in events]


def get_failed_email_events():
    """Get failed email events from all domains from mailgun api."""
    sending_profiles = sending_profile_manager.all()
    events = []
    success = {"success": True}
    for sending_profile in sending_profiles:
        if sending_profile["interface_type"] == "SES":
            break
        if sending_profile["interface_type"] == "Mailgun":
            if sending_profile["mailgun_domain"]:
                try:
                    resp = requests.get(
                        f"https://api.mailgun.net/v3/{sending_profile['mailgun_domain']}/events",
                        auth=("api", MAILGUN_API_KEY),
                        params={"event": "failed"},
                    )
                    resp.raise_for_status()
                except HTTPError as e:
                    logger.exception(e)
                    logger.error(resp.text)
                    success["success"] = False
        if sending_profile["interface_type"] == "SMTP":
            if sending_profile["smtp_host"]:
                try:
                    resp = requests.get(
                        f"https://api.mailgun.net/v3/{sending_profile['smtp_host']}/events",
                        auth=("api", MAILGUN_API_KEY),
                        params={"event": "failed"},
                    )
                except HTTPError as e:
                    logger.exception(e)
                    logger.error(resp.text)
                    success["success"] = False
        if resp.json().get("items"):
            events.extend(resp.json()["items"])

    for event in events:
        if event["recipient"] not in [
            failed_email["recipient"] for failed_email in failed_email_manager.all()
        ]:
            failed_email_manager.save(
                {
                    "recipient": event["recipient"],
                    "sent_time": datetime.fromtimestamp(event["timestamp"]),
                    "error_type": event["reason"],
                    "message_id": event["message"]["headers"]["message-id"],
                    "reason": event["delivery-status"]["message"],
                }
            )
    return success
