"""Landing Page Models."""
# cisagov Libraries
from database.repository.models import Model
from database.repository.types import (
    BooleanType,
    DateTimeType,
    IntType,
    StringType,
    UUIDType,
)


class LandingPageModel(Model):
    """LandingPageModel."""

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
