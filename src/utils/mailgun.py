"""Mailgun utils."""
# Third-Party Libraries
import requests  # type: ignore
from requests.exceptions import HTTPError  # type: ignore

# cisagov Libraries
from api.config.environment import MAILGUN_API_KEY
from api.manager import SendingProfileManager
from utils.logging import setLogger

logger = setLogger(__name__)

sending_profile_manager = SendingProfileManager()


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
    for sending_profile in sending_profiles:
        match sending_profile["interface_type"]:
            case "SES":
                break
            case "Mailgun":
                resp = requests.get(
                    f"https://api.mailgun.net/v3/{sending_profile['mailgun_domain']}/events",
                    auth=("api", MAILGUN_API_KEY),
                    params={"event": "failed"},
                )
            case "SMTP":
                resp = requests.get(
                    f"https://api.mailgun.net/v3/{sending_profile['smtp_host']}/events",
                    auth=("api", MAILGUN_API_KEY),
                    params={"event": "failed"},
                )
        try:
            resp.raise_for_status()
        except HTTPError as e:
            logger.exception(e)
            logger.error(resp.text)
            raise e
        if resp.json()["items"]:
            events.extend(resp.json()["items"])

    return events
