"""Subscription Campaigns."""

# Standard Python Libraries
from datetime import datetime, timedelta
import logging

# Third-Party Libraries
from bs4 import BeautifulSoup
from api.manager import CampaignManager
from api.serializers import campaign_serializers
from api.utils.generic import format_ztime
from api.utils.subscription.targets import assign_targets
from api.utils.subscription.subscriptions import get_staggered_dates_in_range
from api.utils.subscription.static import CAMPAIGN_MINUTES, DEFAULT_X_GOPHISH_CONTACT

from api.services import LandingPageService

campaign_manager = CampaignManager()
landing_page_service = LandingPageService()


def generate_campaigns(subscription, landing_page, sub_levels, cycle_uuid):
    """Generate_campaigns.

    Args:
        subscription (dict): subscription
        sub_level (dict): sub_level
        landing_page (dict): landing_page

    Returns:
        list(dict): gophish_campaigns
    """
    gophish_campaigns = []
    for k in sub_levels.keys():
        # Assign targets to templates in each group
        assign_targets(sub_levels[k])
        gophish_campaigns.extend(
            create_campaign(subscription, sub_levels[k], landing_page, cycle_uuid)
        )

    return gophish_campaigns


def create_campaign(subscription, sub_level, landing_page, cycle_uuid):
    """Create campaign.

    Args:
        subscription (dict): subscription
        sub_level (dict): sub_level
        landing_page (dict): landing_page

    Returns:
        list(dict): gophish_campaigns
    """
    gophish_campaigns = []
    if subscription["stagger_emails"]:
        date_list = get_staggered_dates_in_range(
            sub_level["start_date"],
            len(sub_level["template_targets"]),
        )
    else:
        date_list = []
        for _ in range(len(sub_level["template_targets"])):
            date_list.append(sub_level["start_date"])

    for index, k in enumerate(sub_level["template_targets"].keys()):

        # Create user groups in Gophish
        target_group = campaign_manager.create_user_group(
            subscription_name=subscription["name"],
            deception_level=sub_level["deception_level"],
            index=index,
            target_list=sub_level["template_targets"][k],
        )

        template = list(
            filter(
                lambda x: x["template_uuid"] == k, sub_level["personalized_templates"]
            )
        )[0]

        landing_page_name = landing_page
        if template.get("landing_page_uuid"):
            template_lp = landing_page_service.get(template["landing_page_uuid"])
            if template_lp:
                landing_page_name = template_lp["name"]

        gophish_campaigns.append(
            __create_campaign(
                subscription=subscription,
                target_group=target_group,
                landing_page=landing_page_name,
                template=template,
                targets=sub_level["template_targets"][k],
                start_date=date_list[index],
                deception_level=sub_level["deception_level"],
                index=index,
                cycle_uuid=cycle_uuid,
            )
        )

    return gophish_campaigns


def stop_campaigns(campaigns):
    for campaign in campaigns:
        if campaign["status"] != "stopped":
            stop_campaign(campaign)


def stop_campaign(campaign):
    """
    Stops a given campaign.

    Delete Campaign

    Delete Template

    Returns updated Campaign
    """
    # Complete Campaign
    try:
        campaign_manager.complete_campaign(campaign_id=campaign["campaign_id"])
    except Exception as e:
        logging.exception(e)
    campaign["status"] = "stopped"
    campaign["completed_date"] = datetime.now()

    # Delete Campaign
    try:
        campaign_manager.delete_campaign(campaign_id=campaign["campaign_id"])
    except Exception as e:
        logging.exception(e)

    # Delete Templates
    try:
        campaign_manager.delete_email_template(
            template_id=campaign["email_template_id"]
        )
    except Exception as e:
        logging.exception(e)

    # Delete Sending Profile
    try:
        campaign_manager.delete_sending_profile(smtp_id=campaign["smtp"]["id"])
    except Exception as e:
        logging.exception(e)

    # Delete User Groups
    for group in campaign["groups"]:
        try:
            campaign_manager.delete_user_group(group_id=group["id"])
        except Exception as e:
            logging.exception(e)

    return campaign


def __create_campaign(
    subscription,
    target_group,
    landing_page,
    template,
    targets,
    start_date,
    deception_level,
    index,
    cycle_uuid,
):
    """
    Create and Save Campaigns.

    This method handles the creation of each campain with given template, target group, and data.
    """
    base_name = f"{subscription['name']}.{deception_level}.{index}"

    created_template = campaign_manager.create_email_template(
        name=f"{base_name}.{template['name']}",
        template=template["data"],
        text=BeautifulSoup(template["data"], "html.parser").get_text(),
        subject=template["subject"],
    )

    campaign_start = start_date
    campaign_end = start_date + timedelta(minutes=CAMPAIGN_MINUTES)

    campaign_name = f"{base_name}.{template['name']}.{campaign_start.strftime('%Y-%m-%d')}.{campaign_end.strftime('%Y-%m-%d')}"

    sending_profile = __create_campaign_smtp(
        campaign_name,
        template["from_address"],
        cycle_uuid,
        subscription["sending_profile_name"],
    )

    campaign = campaign_manager.create_campaign(
        campaign_name=campaign_name,
        smtp_name=sending_profile.name,
        page_name=landing_page,
        user_group=target_group,
        email_template=created_template,
        launch_date=start_date.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        send_by_date=(campaign_end).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
    )

    default_phish_results = {
        "sent": 0,
        "opened": 0,
        "clicked": 0,
        "submitted": 0,
        "reported": 0,
    }

    return {
        "campaign_id": campaign.id,
        "name": campaign_name,
        "created_date": format_ztime(campaign.created_date),
        "launch_date": campaign_start,
        "send_by_date": campaign_end,
        "email_template": created_template.name,
        "email_template_id": created_template.id,
        "template_uuid": template["template_uuid"],
        "landing_page_template": campaign.page.name,
        "deception_level": deception_level,
        "status": campaign.status,
        "results": [],
        "phish_results": default_phish_results,
        "groups": [campaign_serializers.CampaignGroupSerializer(target_group).data],
        "timeline": [
            {
                "email": None,
                "time": format_ztime(campaign.created_date),
                "message": "Campaign Created",
                "details": "",
            }
        ],
        "target_email_list": targets,
        "smtp": campaign_serializers.CampaignSmtpSerializer(campaign.smtp).data,
    }


def __create_campaign_smtp(
    campaign_name, template_from_address, cycle_uuid, subscription_sending_profile_name
):
    """[summary]

    Args:
        campaign_name (String): Generated name for campaign in gophish
        template_from_address (String): Tempate From address

    Returns:
        SMTP[object]: returning newly created sending profile from gophish
    """
    sending_profiles = campaign_manager.get_sending_profile()
    sending_profile = next(
        iter(
            [p for p in sending_profiles if p.name == subscription_sending_profile_name]
        ),
        None,
    )

    __set_smtp_headers(sending_profile, cycle_uuid)

    from_address = get_campaign_from_address(sending_profile, template_from_address)

    try:
        resp = campaign_manager.create_sending_profile(
            name=campaign_name,
            username=sending_profile.username,
            password=sending_profile.password,
            host=sending_profile.host,
            interface_type=sending_profile.interface_type,
            from_address=from_address,
            ignore_cert_errors=sending_profile.ignore_cert_errors,
            headers=sending_profile.headers,
        )
    except Exception as e:
        logging.error(
            f"Error creating sending profile. Name={campaign_name}; From={from_address}; template_from={template_from_address}"
        )
        raise e

    return resp


def get_campaign_from_address(sending_profile, template_from_address):
    # Get template display name
    if "<" in template_from_address:
        template_display = template_from_address.split("<")[0].strip()
    else:
        template_display = None

    # Get template sender
    template_sender = template_from_address.split("@")[0].split("<")[-1]

    # Get sending profile domain
    sp_domain = (
        sending_profile.from_address.split("<")[-1].split("@")[1].replace(">", "")
    )

    # Generate from address
    if template_display:
        from_address = f"{template_display} <{template_sender}@{sp_domain}>"
    else:
        from_address = f"{template_sender}@{sp_domain}"
    return from_address


def __set_smtp_headers(sending_profile, cycle_uuid):
    """Set SMTP headers.

    This will set up headers: X-Gophish-Contact Header and  DHS-PHISH Header.

    Args:
        sending_profile (object): SMTP object
        cycle_uuid (string): Cycle uuid
    """
    if not sending_profile.headers:
        sending_profile.headers = []

    set_x_gophish_contact_header(sending_profile)

    set_dhs_phish_header(sending_profile, cycle_uuid)


def set_dhs_phish_header(sending_profile, cycle_uuid):
    for header in sending_profile.headers:
        if header["key"] == "DHS-PHISH":
            header["value"] = cycle_uuid
            return

    new_header = {"key": "DHS-PHISH", "value": cycle_uuid}
    sending_profile.headers.append(new_header)
    return


def set_x_gophish_contact_header(sending_profile):
    for header in sending_profile.headers:
        if header["key"] == "X-Gophish-Contact":
            header["value"] = DEFAULT_X_GOPHISH_CONTACT
            return

    if DEFAULT_X_GOPHISH_CONTACT:
        new_header = {"key": "X-Gophish-Contact", "value": DEFAULT_X_GOPHISH_CONTACT}
        sending_profile.headers.append(new_header)

    return
