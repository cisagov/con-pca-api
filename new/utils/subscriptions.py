"""Subscription utils."""
# cisagov Libraries
from api.manager import SubscriptionManager

subscription_manager = SubscriptionManager()


def create_subscription_name(customer):
    """Create name for subscription from customer."""
    subscriptions = subscription_manager.all(
        {"customer_uuid": customer["customer_uuid"]},
        fields=["name", "identifier"],
    )
    if not subscriptions:
        return f"{customer['identifier']}_1"
    else:
        ids = [int(float(x["name"].split("_")[-1])) for x in subscriptions]
        return f"{customer['identifier']}_{max(ids) + 1}"
