"""Sending Profile Schemas."""

# Third-Party Libraries
from marshmallow import fields, validate

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class SendingProfileSchema(BaseSchema):
    """SendingProfileSchema."""

    name = fields.Str(required=True)
    interface_type = fields.Str(
        default="SMTP",
        validate=validate.OneOf(
            [
                "SMTP",
                "Mailgun",
                "SES",
            ]
        ),
    )
    from_address = fields.Str()
    landing_page_domain = fields.Str(required=False)
    sending_ips = fields.Str()

    # SMTP
    smtp_username = fields.Str()
    smtp_password = fields.Str()
    smtp_host = fields.Str()

    # Mailgun
    mailgun_domain = fields.Str()
    mailgun_api_key = fields.Str()

    # SES
    ses_role_arn = fields.Str()

    # TODO: Write up validations based on Type
