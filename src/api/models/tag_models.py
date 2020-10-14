from database.repository.models import Model
from database.repository.types import (
    DateTimeType,
    StringType,
    UUIDType,
)


class TagModel(Model):
    """
    Tag Model.

    A Tag is a replaceable string in a
    Template that is replaced by a real value.
    """

    # created by mongodb
    tag_definition_uuid = UUIDType()
    # User Defined
    tag = StringType()
    description = StringType()
    data_source = StringType()
    tag_type = StringType()
    # db tracking data added below
    created_by = StringType()
    cb_timestamp = DateTimeType()
    last_updated_by = StringType()
    lub_timestamp = DateTimeType()


def validate_tag(data_object):
    """
    This is an the validate_tag.

    This shows basic validation for the model.
    """
    return TagModel(data_object).validate()
