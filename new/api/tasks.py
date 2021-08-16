"""Tasks."""
# cisagov Libraries
from api.manager import SubscriptionManager

subscription_manager = SubscriptionManager()


def task():
    """Run basic task."""
    print("Tasks are active")
    print(len(subscription_manager.all()))
