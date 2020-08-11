"""Landing Page Utils"""
# Third-Party Libraries
from api.models.landing_page_models import LandingPageModel, validate_landing_page
from api.utils import db_utils as db
from api.utils.generic import format_ztime


def get_landing_pages():
    """
    Returns a list of unretired email templates from database.

    Returns:
        list: returns a list of unretired email templates
    """
    return db.get_list(
        {"template_type": "Email", "retired": False},
        "landing_page",
        LandingPageModel,
        validate_landing_page,
    )


# def get_subscription_templates(subscription):
#     return db.get_list(
#         parameters={
#             "template_uuid": {"$in": subscription.get("templates_selected_uuid_list")}
#         },
#         collection="landing_pages",
#         model=TemplateModel,
#         validation_model=validate_template,
#     )
