from database.repository.models import Model
from database.repository.types import (
    BooleanType,
    DateTimeType,
    FloatType,
    IntType,
    ListType,
    ModelType,
    StringType,
    UUIDType,
)
from api.models.phishing_models import SubscriptionTargetModel, PhishingResultsModel


class SendingHeaderModel(Model):
    key = StringType()
    value = StringType()


class GoPhishSmtpModel(Model):
    id = IntType()
    name = StringType()
    host = StringType()
    interface_type = StringType()
    from_address = StringType()
    ignore_cert_errors = BooleanType()
    modified_date = DateTimeType()
    headers = ListType(ModelType(SendingHeaderModel), default=[])


class GoPhishTimelineModel(Model):
    email = StringType()
    time = DateTimeType()
    message = StringType()
    details = StringType()
    duplicate = BooleanType()


class GoPhishGroupModel(Model):
    id = IntType()
    name = StringType()
    targets = ListType(ModelType(SubscriptionTargetModel))
    modified_date = DateTimeType()


class GoPhishResultModel(Model):
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


class GoPhishCampaignsModel(Model):
    campaign_uuid = UUIDType()
    campaign_id = IntType()
    subscription_uuid = UUIDType()
    cycle_uuid = UUIDType()
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
    smtp = ModelType(GoPhishSmtpModel)

    # db data tracking added below
    created_by = StringType()
    cb_timestamp = DateTimeType()
    last_updated_by = StringType()
    lub_timestamp = DateTimeType()
