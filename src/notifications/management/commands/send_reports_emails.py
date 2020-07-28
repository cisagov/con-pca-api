"""Send Reports Command."""
# Django Libraries
from django.core.management.base import BaseCommand

# Local Libraries
from api.models.subscription_models import SubscriptionModel, validate_subscription
from api.utils.db_utils import get_list
from notifications.views import ReportsEmailSender


class Command(BaseCommand):
    """Command.

    Args:
        BaseCommand (Django Base): Setting up Command for handling report creation.
    """

    help_text = "Sends reports emails"

    def handle(self, *args, **options):
        """Handle Command."""
        parameters = {"archived": {"$in": [False, None]}}
        subscription_list = get_list(
            parameters, "subscription", SubscriptionModel, validate_subscription
        )
        subscription = subscription_list[0]

        message_type = "cycle_report"
        sender = ReportsEmailSender(subscription, message_type)
        sender.send()
