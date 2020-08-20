"""Subscription Campaigns."""

# Standard Python Libraries
from datetime import datetime, timedelta
import logging

# Third-Party Libraries
from api.manager import CampaignManager
from api.serializers import campaign_serializers
from api.utils.generic import format_ztime
from api.utils.subscription.targets import assign_targets
from api.utils import db_utils as db
from api.models.dhs_models import DHSContactModel, validate_dhs_contact
from api.models.landing_page_models import LandingPageModel, validate_landing_page
from api.serializers.dhs_serializers import DHSContactGetSerializer

logger = logging.getLogger()

campaign_manager = CampaignManager()


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
        sub_levels[k] = assign_targets(sub_levels[k])
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

    for index, k in enumerate(sub_level["template_targets"].keys()):
        group_name = (
            f"{subscription['name']}.Targets.{sub_level['deception_level']}.{index}"
        )

        target_group = campaign_manager.create(
            "user_group",
            group_name=group_name,
            target_list=sub_level["template_targets"][k],
        )

        if not target_group:
            # target_group exists, so delete and remake
            # first get all group
            gp_user_groups = campaign_manager.get_user_group()
            # filter out group
            pg_user_group = list(
                filter(lambda x: x.name == group_name, gp_user_groups)
            )[0]
            # delete pre-exisiting group
            campaign_manager.delete_email_template(template_id=pg_user_group.id)
            # create new group
            target_group = campaign_manager.create(
                "user_group",
                group_name=group_name,
                target_list=sub_level["template_targets"][k],
            )

        template = list(
            filter(
                lambda x: x["template_uuid"] == k, sub_level["personalized_templates"]
            )
        )[0]

        landing_page_name = landing_page
        if "landing_page_uuid" in template:
            landing_page_list = db.get_list(
                {"landing_page_uuid": template["landing_page_uuid"]},
                "landing_page",
                LandingPageModel,
                validate_landing_page,
            )
            if landing_page_list:
                landing_page_name = landing_page_list[0]["name"]

        gophish_campaigns.append(
            __create_campaign(
                subscription=subscription,
                target_group=target_group,
                landing_page=landing_page_name,
                template=template,
                targets=sub_level["template_targets"][k],
                start_date=sub_level["start_date"],
                deception_level=sub_level["deception_level"],
                index=index,
                cycle_uuid=cycle_uuid,
            )
        )

    return gophish_campaigns


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
        campaign_manager.delete(
            "email_template", template_id=campaign["email_template_id"]
        )
    except Exception as e:
        logging.exception(e)

    try:
        campaign_manager.delete("sending_profile", smtp_id=campaign["smtp"]["id"])
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

    dhs_contact_uuid = subscription["dhs_contact_uuid"]

    created_template = campaign_manager.generate_email_template(
        name=f"{base_name}.{template['name']}",
        template=template["data"],
        subject=template["subject"],
    )
    if not created_template:
        # template exists, so delete and remake
        # first get all teampletes
        gp_templates = campaign_manager.get_email_template()
        # filter out template
        gp_template = list(
            filter(lambda x: x.name == f"{base_name}.{template['name']}", gp_templates)
        )[0]
        # delete pre-exisiting template
        campaign_manager.delete_email_template(template_id=gp_template.id)
        # create new template
        created_template = campaign_manager.generate_email_template(
            name=f"{base_name}.{template['name']}",
            template=template["data"],
            subject=template["subject"],
        )

    campaign_start = start_date
    campaign_end = start_date + timedelta(days=60)

    campaign_name = f"{base_name}.{template['name']}.{campaign_start.strftime('%Y-%m-%d')}.{campaign_end.strftime('%Y-%m-%d')}"

    sending_profile = __create_campaign_smtp(
        campaign_name,
        template["from_address"],
        cycle_uuid,
        subscription["sending_profile_name"],
        dhs_contact_uuid,
    )

    campaign = campaign_manager.create(
        "campaign",
        campaign_name=campaign_name,
        smtp_name=sending_profile.name,
        page_name=landing_page,
        user_group=target_group,
        email_template=created_template,
        launch_date=start_date.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        send_by_date=(campaign_end).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
    )

    logger.info("campaign created: {}".format(campaign))

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
    campaign_name,
    template_from_address,
    cycle_uuid,
    subscription_sending_profile_name,
    dhs_contact_uuid,
):
    """[summary]

    Args:
        campaign_name (String): Generated name for campaign in gophish
        template_from_address (String): Tempate From address

    Returns:
        SMTP[object]: returning newly created sending profile from gophish
    """
    sending_profiles = campaign_manager.get("sending_profile")
    sending_profile = next(
        iter(
            [p for p in sending_profiles if p.name == subscription_sending_profile_name]
        ),
        None,
    )

    __set_smtp_headers(sending_profile, cycle_uuid, dhs_contact_uuid)

    # Get template display name
    if "<" in template_from_address:
        template_display = template_from_address.split("<")[0].strip()
    else:
        template_display = None

    # Get template sender
    template_sender = template_from_address.split("<")[-1].split("@")[0]

    # Get sending profile domain
    sp_domain = (
        sending_profile.from_address.split("<")[-1].split("@")[1].replace(">", "")
    )

    # Generate from address
    if template_display:
        from_address = f"{template_display} <{template_sender}@{sp_domain}>"
    else:
        from_address = f"{template_sender}@{sp_domain}"

    return campaign_manager.create(
        "sending_profile",
        name=campaign_name,
        username=sending_profile.username,
        password=sending_profile.password,
        host=sending_profile.host,
        interface_type=sending_profile.interface_type,
        from_address=from_address,
        ignore_cert_errors=sending_profile.ignore_cert_errors,
        headers=sending_profile.headers,
    )


def __set_smtp_headers(sending_profile, cycle_uuid, dhs_contact_uuid):
    """Set SMTP headers.

    This will set up headers: X-Gophish-Contact Header and  DHS-PHISH Header.

    Args:
        sending_profile (object): SMTP object
        cycle_uuid (string): Cycle uuid
        dhs_contact_uuid (string): dhs uuid
    """
    # Create X-Gophish-Contact Header
    dhs_contact = db.get_single(
        dhs_contact_uuid, "dhs_contact", DHSContactModel, validate_dhs_contact
    )
    dhs_contact_data = DHSContactGetSerializer(dhs_contact).data
    gophish_dhs_contact_header = {
        "key": "X-Gophish-Contact",
        "value": dhs_contact_data["email"],
    }
    # Set DHS-PHISH Header
    new_header = {"key": "DHS-PHISH", "value": cycle_uuid}

    if not sending_profile.headers:
        sending_profile.headers = [new_header, gophish_dhs_contact_header]
        return

    # check if header exists
    exists = __check_dhs_phish_header(sending_profile, new_header["value"])

    if not exists:
        sending_profile.headers.append(new_header)

    sending_profile.headers.append(gophish_dhs_contact_header)


def __check_dhs_phish_header(sending_profile, cycle_uuid):
    """Check DHS Phish Header

    Check if there is already a dhs header and update if one is found.

    Args:
        sending_profile (object): SMTP object
        cycle_uuid (string): cycle_uuid

    Returns:
        bool: if header exists and updated
    """
    for header in sending_profile.headers:
        if header["key"] == "DHS-PHISH":
            header["value"] = cycle_uuid
            return True
    return False
