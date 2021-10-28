"""Mailgun utils."""
# Third-Party Libraries
import requests  # type: ignore


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
