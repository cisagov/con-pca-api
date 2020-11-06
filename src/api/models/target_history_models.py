from database.repository.models import Model
from database.repository.types import (
    DateTimeType,
    EmailType,
    ListType,
    ModelType,
    StringType,
    UUIDType,
)


class TemplateStatusModel(Model):
    """
    Template Status Model.

    This tracks the template uuid and timestamp of being sent.
    """

    template_uuid = UUIDType()
    sent_timestamp = DateTimeType()


class TargetHistoryModel(Model):
    """
    Template History Model.

    This tracks the history of tempaltes sent to a user.
    """

    # created by mongodb
    target_uuid = UUIDType()
    # User Defined
    email = EmailType(required=True)
    history_list = ListType(ModelType(TemplateStatusModel))
    # db tracking data added below
    created_by = StringType()
    cb_timestamp = DateTimeType()
    last_updated_by = StringType()
    lub_timestamp = DateTimeType()
