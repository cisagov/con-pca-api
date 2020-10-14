"""
Models.

These are not Django Models, there are created using Schematics Models
"""
# Third-Party Libraries
from api.models.customer_models import CustomerContactModel
from database.repository.models import Model
from api.models.phishing_models import SubscriptionTargetModel, PhishingResultsModel
from database.repository.types import (
    BooleanType,
    DateTimeType,
    EmailType,
    IntType,
    ListType,
    ModelType,
    StringType,
    UUIDType,
)


class SubscriptionEmailHistoryModel(Model):
    """
    This is the Email History Model.

    This is each entry in the email history list.
    """

    report_type = StringType()
    sent = DateTimeType()
    email_to = EmailType(required=True)
    email_from = StringType()
    bcc = EmailType(required=True)
    manual = BooleanType(default=False)


class SubscriptionClicksModel(Model):
    """
    This is the SubscriptionClicks Model.

    This is a format to hold target information in the subscription model.
    """

    source_ip = StringType()
    timestamp = DateTimeType()
    target_uuid = UUIDType()


class CycleModel(Model):
    """
    This is the Cycle Model.

    This tracks the quarterly cycle and the campaigns involved
    in each cycle.
    """

    cycle_uuid = StringType()
    start_date = DateTimeType()
    end_date = DateTimeType()
    active = BooleanType()
    campaigns_in_cycle = ListType(IntType())
    phish_results = ModelType(PhishingResultsModel)
    phish_results_dirty = BooleanType(default=False)
    override_total_reported = IntType()


class ScheduledTaskModel(Model):
    """
    This is the Scheduled Task Model.

    This keeps track of a list of active tasks.
    """

    task_uuid = StringType()
    message_type = StringType()
    scheduled_date = DateTimeType()
    executed = BooleanType()
    executed_date = DateTimeType()
    error = StringType()


class SubscriptionModel(Model):
    """
    This is the Subscription Model.

    This controls all data needed in saving the model.
    """

    # created by mongodb
    subscription_uuid = UUIDType()
    # values being passed in.
    customer_uuid = UUIDType()
    tasks = ListType(ModelType(ScheduledTaskModel))
    name = StringType()
    url = StringType()
    target_domain = StringType()
    keywords = StringType()
    start_date = DateTimeType()
    end_date = DateTimeType()
    primary_contact = ModelType(CustomerContactModel)
    dhs_contact_uuid = UUIDType()
    status = StringType()
    target_email_list = ListType(ModelType(SubscriptionTargetModel))
    target_email_list_cached_copy = ListType(ModelType(SubscriptionTargetModel))
    templates_selected_uuid_list = ListType(StringType)
    sending_profile_name = StringType()
    active = BooleanType()
    archived = BooleanType(default=False)
    manually_stopped = BooleanType(default=False)
    cycles = ListType(ModelType(CycleModel))
    email_report_history = ListType(
        ModelType(SubscriptionEmailHistoryModel), default=[]
    )
    stagger_emails = BooleanType()
    # db data tracking added below
    created_by = StringType()
    cb_timestamp = DateTimeType()
    last_updated_by = StringType()
    lub_timestamp = DateTimeType()


def validate_subscription(data_object):
    """
    This is an the validate_subscription.

    This shows basic validation for the model.
    """
    return SubscriptionModel(data_object).validate()
