"""Template Utils."""
# Standard Python Libraries
import logging
import random

# cisagov Libraries
from api.manager import CampaignManager
from api.services import CustomerService, TagService, TargetHistoryService
from api.utils.generic import format_ztime
from api.utils.subscription.campaigns import get_campaign_from_address
from api.utils.template.personalize import personalize_template

campaign_manager = CampaignManager()
target_history_service = TargetHistoryService()
customer_service = CustomerService()
tag_service = TagService()

deception_level = {"high": 3, "moderate": 2, "low": 1}


def update_target_history(template_uuid, email, time):
    """Update Target History."""
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


def validate_template(template):
    """Validate template."""
    customer = customer_service.random()[0]

    personalized_data = personalize_template(
        customer_info=customer,
        template_data=[template],
        sub_data=None,
        tag_list=tag_service.get_list(),
    )[0]

    try:
        rn = random.randint(0, 5000)
        sending_profile = campaign_manager.create_sending_profile(
            name=f"valid_test_{rn}",
            username="test",
            password="test",
            host="test.com",
            interface_type="SMTP",
            from_address=get_campaign_from_address(
                {"from_address": "test@test.com"}, personalized_data["from_address"]
            ),
            ignore_cert_errors=True,
            headers=None,
        )
    except Exception as e:
        logging.exception(e)
        return str(e)
    campaign_manager.delete_sending_profile(sending_profile.id)
