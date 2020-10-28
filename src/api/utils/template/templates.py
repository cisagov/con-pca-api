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
    data = {
        "template_uuid": campaign_info["template_uuid"],
        "sent_timestamp": format_ztime(seralized_data["time"]),
    }

    if target_history_service.exists({"email": seralized_data["email"]}):
        target = target_history_service.get_list({"email": seralized_data["email"]})[0]
        target_history_service.push_nested(
            uuid=target["target_uuid"],
            field="history_list",
            data=data,
        )
    else:
        # create new target history if not exisiting
        target_hist = {
            "email": seralized_data["email"],
            "history_list": [data],
        }
        target_history_service.save(target_hist)
