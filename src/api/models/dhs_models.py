"""DHS Contact Models."""
# cisagov Libraries
from database.repository.models import Model
from database.repository.types import (
    BooleanType,
    DateTimeType,
    EmailType,
    StringType,
    UUIDType,
)


class DHSContactModel(Model):
    """DHSContactModel."""

    dhs_contact_uuid = UUIDType()
    first_name = StringType()
    last_name = StringType()
    title = StringType()
    office_phone = StringType()
    mobile_phone = StringType()
    email = EmailType()
    notes = StringType()
    active = BooleanType()

    # db data
    created_by = StringType()
    cb_timestamp = DateTimeType()
    last_updated_by = StringType()
    lub_timestamp = DateTimeType()
