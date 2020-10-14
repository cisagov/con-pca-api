"""
Models.

These are not Django Models, there are created using Schematics Models
"""
# Third-Party Libraries
from database.repository.models import Model
from database.repository.types import (
    BooleanType,
    DateTimeType,
    IntType,
    StringType,
    UUIDType,
)


class LandingPageModel(Model):
    """
    This is the Landing Page Model
    """

    # Created via service
    landing_page_uuid = UUIDType()
    # Created by Gophish
    gophish_template_id = IntType()
    # User Creataed
    name = StringType()
    is_default_template = BooleanType(default=False)
    html = StringType()

    # db tracking data added below
    created_by = StringType()
    cb_timestamp = DateTimeType()
    last_updated_by = StringType()
    lub_timestamp = DateTimeType()


def validate_landing_page(data_object):
    """
    This validates templates data.

    This shows basic validation for the model.
    """
    return LandingPageModel(data_object).validate()
