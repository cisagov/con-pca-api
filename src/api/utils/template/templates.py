"""Tempalte Utils."""
# Third-Party Libraries
from api.models.template_models import (
    TargetHistoryModel,
    TemplateModel,
    validate_history,
    validate_template,
)
from api.utils import db_utils as db
from api.utils.generic import format_ztime

deception_level = {"high": 3, "moderate": 2, "low": 1}


def get_email_templates():
    """
    Returns a list of unretired email templates from database.

    Returns:
        list: returns a list of unretired email templates
    """
    return db.get_list(
        {"template_type": "Email", "retired": False},
        "template",
        TemplateModel,
        validate_template,
    )


def update_target_history(campaign_info, seralized_data):
    """Update target History.

    Args:
        campaign_info (dict): campaign_info
        seralized_data (dict): seralized_data
    """
    # check if email target exists, if not, create
    document_list = db.get_list(
        {"email": seralized_data["email"]},
        "target",
        TargetHistoryModel,
        validate_history,
    )
    if document_list:
        # If object exists, update with latest template info
        target = document_list[0]
        filter_target_history = list(
            filter(
                lambda x: x["template_uuid"] == campaign_info["template_uuid"],
                target["history_list"],
            )
        )
        if not filter_target_history:
            target["history_list"].append(
                {
                    "template_uuid": campaign_info["template_uuid"],
                    "sent_timestamp": format_ztime(seralized_data["time"]),
                }
            )
            db.update_single(
                target["target_uuid"],
                target,
                "target",
                TargetHistoryModel,
                validate_history,
            )
    else:
        # create new target history if not exisiting
        targert_hist = {
            "email": seralized_data["email"],
            "history_list": [
                {
                    "template_uuid": campaign_info["template_uuid"],
                    "sent_timestamp": format_ztime(seralized_data["time"]),
                }
            ],
        }
        db.save_single(targert_hist, "target", TargetHistoryModel, validate_history)

    return


def get_subscription_templates(subscription):
    return db.get_list(
        parameters={
            "template_uuid": {"$in": subscription.get("templates_selected_uuid_list")}
        },
        collection="template",
        model=TemplateModel,
        validation_model=validate_template,
    )


def generate_template_email(subscription):
    """
    returns email with list of templates used by subscription
    """
    templates = get_subscription_templates(subscription)

    templates_separator = "--------------------------------------------------------------------------------\n<br>"
    body = ""
    seperator = "\n<br>"
    for t in templates:
        deception_level = list(
            filter(
                lambda x: x["template_uuid"] == t["template_uuid"],
                subscription["gophish_campaign_list"],
            )
        )[0].get("deception_level")

        body += "\n\nTemplate Name: " + t["name"] + seperator
        body += "Template Subject: " + t["subject"] + seperator
        body += "Deception Level:" + str(deception_level) + seperator + seperator
        body += t["html"]
        body += templates_separator
        body += templates_separator

    return body
