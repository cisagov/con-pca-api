from database.repository import types
from database.repository.models import Model


class PhishingResultsModel(Model):
    """
    This is the Cycle Model.

    This hold the results for each campaign. Filled by webhook response data
    """

    sent = types.IntType()
    opened = types.IntType()
    clicked = types.IntType()
    submitted = types.IntType()
    reported = types.IntType()


class SubscriptionTargetModel(Model):
    """
    This is the Target Model.

    This controls all data needed in saving the model. Current fields are:
    first_name = StringType()
    last_name = StringType()
    position = StringType()
    email = EmailType(required=True)
    """

    first_name = types.StringType()
    last_name = types.StringType()
    position = types.StringType()
    email = types.EmailType(required=True)
