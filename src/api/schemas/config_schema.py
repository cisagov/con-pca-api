"""Application config schemas."""
# Third-Party Libraries
from marshmallow import fields, validate
from marshmallow.schema import Schema
from marshmallow.utils import EXCLUDE

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class ConfigSchema(BaseSchema):
    """
    ConfigSchema.

    This is the schema for the way that the config is stored in the database.
    """

    key = fields.Str()
    value = fields.Str(allow_none=True)


class ConfigPostSchema(Schema):
    """
    ConfigPostSchema.

    This is the way new configs are posted and validators to go along with it.
    """

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    REPORTING_FROM_ADDRESS = fields.Email(allow_none=True)
    REPORTING_INTERFACE_TYPE = fields.Str(
        allow_none=True, validate=validate.OneOf(["SMTP", "Mailgun", "SES"])
    )

    # SMTP Config
    REPORTING_SMTP_HOST = fields.Str(allow_none=True)
    REPORTING_SMTP_USERNAME = fields.Str(allow_none=True)
    REPORTING_SMTP_PASSWORD = fields.Str(allow_none=True)

    # Mailgun Config
    REPORTING_MAILGUN_DOMAIN = fields.Str(allow_none=True)
    REPORTING_MAILGUN_API_KEY = fields.Str(allow_none=True)

    # SES Config
    REPORTING_SES_ARN = fields.Str(allow_none=True)
