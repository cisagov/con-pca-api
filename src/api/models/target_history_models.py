"""TargetHistory Models."""
# cisagov Libraries
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
    """TemplateStatusModel."""

    template_uuid = UUIDType()
    sent_timestamp = DateTimeType()


class TargetHistoryModel(Model):
    """TargetHistoryModel."""

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
