from api.utils.generic import format_ztime
from api.services import TargetHistoryService

target_history_service = TargetHistoryService()

deception_level = {"high": 3, "moderate": 2, "low": 1}


def update_target_history(template_uuid, email, time):
    # check if email target exists, if not, create
    data = {
        "template_uuid": template_uuid,
        "sent_timestamp": format_ztime(time),
    }
    target = target_history_service.get_single(
        {"email": email},
        fields=["target_uuid"],
    )

    if target:
        target_history_service.push_nested(
            uuid=target["target_uuid"],
            field="history_list",
            data=data,
        )
    else:
        # create new target history if not exisiting
        target_history_service.save(
            {
                "email": email,
                "history_list": [data],
            }
        )
