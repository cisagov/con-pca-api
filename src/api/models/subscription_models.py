"""
Models.

These are not Django Models, there are created using Schematics Models
"""
# Third-Party Libraries
from api.models.customer_models import CustomerContactModel
from database.repository.models import Model
from database.repository.types import (
    BooleanType,
    DateTimeType,
    EmailType,
    FloatType,
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


class SubscriptionTargetModel(Model):
    """
    This is the Target Model.

    This controls all data needed in saving the model. Current fields are:
    first_name = StringType()
    last_name = StringType()
    position = StringType()
    email = EmailType(required=True)
    """

    first_name = StringType()
    last_name = StringType()
    position = StringType()
    email = EmailType(required=True)


class SubscriptionClicksModel(Model):
    """
    This is the SubscriptionClicks Model.

    This is a format to hold target information in the subscription model.
    """

    source_ip = StringType()
    timestamp = DateTimeType()
    target_uuid = UUIDType()


class GoPhishResultModel(Model):
    """
    This is the GoPhish Result Model.

    This is a format to hold target information in the subscription model.
    id                   : int64
    first_name           : string
    last_name            : string
    position             : string
    status               : string
    ip                   : string
    latitude             : float
    longitude            : float
    send_date            : string(datetime)
    reported             : boolean
    """

    id = StringType()
    first_name = StringType()
    last_name = StringType()
    position = StringType()
    status = StringType()
    ip = StringType()
    latitude = FloatType()
    longitude = FloatType()
    send_date = DateTimeType()
    reported = BooleanType()


class GoPhishGroupModel(Model):
    """
    This is the SubscriptionClicks Model.

    This is a format to hold target information in the subscription model.
    id              : int64
    name            : string
    targets         : array(Target)
    modified_date   : string(datetime)
    """

    id = IntType()
    name = StringType()
    targets = ListType(ModelType(SubscriptionTargetModel))
    modified_date = DateTimeType()


class GoPhishTimelineModel(Model):
    """
    This is the GoPhish Timeline Model.

    This is a format to hold target information in the subscription model.
    email                : string
    time                 : string(datetime)
    message              : string
    details              : string(JSON)
    """

    email = StringType()
    time = DateTimeType()
    message = StringType()
    details = StringType()
    duplicate = BooleanType()


class PhishingResultsModel(Model):
    """
    This is the Cycle Model.

    This hold the results for each campaign. Filled by webhook response data
    """

    sent = IntType()
    opened = IntType()
    clicked = IntType()
    submitted = IntType()
    reported = IntType()


class GoPhishCampaignsModel(Model):
    """
    This is the GoPhish Campaigns Model.

    This is a format to hold GophishCampaign information in the subscription model.
    id                  : int64
    name                : string
    created_date        : string(datetime)
    launch_date         : string(datetime)
    send_by_date        : string(datetime)
    completed_date      : string(datetime)
    template            : Template
    page                : Page
    status              : string
    results             : []Result
    groups              : []Group
    timeline            : []Event
    """

    campaign_id = IntType()
    name = StringType()
    created_date = DateTimeType()
    launch_date = DateTimeType()
    send_by_date = DateTimeType()
    completed_date = DateTimeType()
    email_template = StringType()
    email_template_id = IntType()
    template_uuid = UUIDType()
    deception_level = IntType()
    landing_page_template = StringType()
    status = StringType()
    results = ListType(ModelType(GoPhishResultModel))
    phish_results = ModelType(PhishingResultsModel)
    phish_results_dirty = BooleanType(default=False)
    groups = ListType(ModelType(GoPhishGroupModel))
    timeline = ListType(ModelType(GoPhishTimelineModel))
    target_email_list = ListType(ModelType(SubscriptionTargetModel))


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
    keywords = StringType()
    start_date = DateTimeType()
    # commented out fields for now are unused for the time
    end_date = DateTimeType()
    # report_count = IntType()
    gophish_campaign_list = ListType(ModelType(GoPhishCampaignsModel))
    # first_report_timestamp = DateTimeType()
    primary_contact = ModelType(CustomerContactModel)
    dhs_contact_uuid = UUIDType()
    status = StringType()
    target_email_list = ListType(ModelType(SubscriptionTargetModel))
    templates_selected_uuid_list = ListType(StringType)
    sending_profile_name = StringType()
    active = BooleanType()
    archived = BooleanType(default=False)
    manually_stopped = BooleanType(default=False)
    cycles = ListType(ModelType(CycleModel))
    email_report_history = ListType(
        ModelType(SubscriptionEmailHistoryModel), default=[]
    )
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
