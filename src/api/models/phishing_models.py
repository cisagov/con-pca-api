"""Phish Models."""
# cisagov Libraries
from database.repository import types
from database.repository.models import Model


class PhishingResultsModel(Model):
    """PhishingResultsModel."""

    sent = types.IntType()
    opened = types.IntType()
    clicked = types.IntType()
    submitted = types.IntType()
    reported = types.IntType()


class SubscriptionTargetModel(Model):
    """SubscriptionTargetModel."""

    first_name = types.StringType()
    last_name = types.StringType()
    position = types.StringType()
    email = types.EmailType(required=True)
