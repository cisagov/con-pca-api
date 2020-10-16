"""Tempalte Utils."""
from api.utils.generic import format_ztime
from api.services import TargetHistoryService

target_history_service = TargetHistoryService()

deception_level = {"high": 3, "moderate": 2, "low": 1}


def update_target_history(campaign_info, seralized_data):
    """Update target History.

    Args:
        campaign_info (dict): campaign_info
        seralized_data (dict): seralized_data
    """
    # check if email target exists, if not, create
    document_list = target_history_service.get_list({"email": seralized_data["email"]})
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
            target_history_service.update(target["target_uuid"], target)
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
        target_history_service.save(targert_hist)
