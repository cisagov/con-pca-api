"""Subscription Campaign Utils."""

# Standard Python Libraries
from datetime import datetime, timedelta
import logging

# Third-Party Libraries
from bs4 import BeautifulSoup

# cisagov Libraries
from api.manager import CampaignManager
from api.serializers import campaign_serializers
from api.services import CampaignService, LandingPageService
from api.utils.generic import format_ztime
from api.utils.subscription.subscriptions import get_campaign_minutes
from api.utils.subscription.targets import assign_targets
from config.settings import DEFAULT_X_GOPHISH_CONTACT, GP_LANDING_SUBDOMAIN

campaign_manager = CampaignManager()
landing_page_service = LandingPageService()
campaign_service = CampaignService()


def generate_campaigns(subscription, landing_page, sub_levels):
    """
    Generate_campaigns.

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
        try:
            assign_targets(sub_levels[k])
            gophish_campaigns.extend(
                create_campaigns_for_level(subscription, sub_levels[k], landing_page)
            )
        except Exception as e:
            for campaign in gophish_campaigns:
                stop_campaign(campaign, cleanup=True)
            raise e

    return gophish_campaigns


def create_campaigns_for_level(subscription, sub_level, landing_page):
    """
    Create campaign.

    Args:
        subscription (dict): subscription
        sub_level (dict): sub_level
        landing_page (dict): landing_page

    Returns:
        list(dict): gophish_campaigns
    """
    gophish_campaigns = []

    for index, k in enumerate(sub_level["template_targets"].keys()):
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

        try:
            campaign = create_campaign(
                subscription=subscription,
                landing_page=landing_page_name,
                template=template,
                targets=sub_level["template_targets"][k],
                start_date=sub_level["start_date"],
                deception_level=sub_level["deception_level"],
                index=index,
            )
            gophish_campaigns.append(campaign)
        except Exception as e:
            for c in gophish_campaigns:
                stop_campaign(c, cleanup=True)
            raise e

    return gophish_campaigns


def stop_campaigns(campaigns):
    """Stop Campaigns."""
    for campaign in campaigns:
        if campaign["status"] != "stopped":
            stop_campaign(campaign)


def stop_campaign(campaign, cleanup=False):
    """Stop Campaign."""
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
        pass

    # Delete Templates
    try:
        campaign_manager.delete_email_template(
            template_id=campaign["email_template_id"]
        )
    except Exception as e:
        logging.exception(e)
        pass

    # Delete Sending Profile
    try:
        campaign_manager.delete_sending_profile(smtp_id=campaign["smtp"]["id"])
    except Exception as e:
        logging.exception(e)
        pass

    # Delete User Groups
    for group in campaign["groups"]:
        try:
            campaign_manager.delete_user_group(group_id=group["id"])
        except Exception as e:
            logging.exception(e)
            pass

    if not cleanup:
        campaign_service.update(campaign["campaign_uuid"], campaign)


def create_campaign(
    subscription,
    landing_page,
    template,
    targets,
    start_date,
    deception_level,
    index,
):
    """Create a campaign."""
    return_data = {}

    try:
        base_name = f"{subscription['name']}.{deception_level}.{index}"

        # Create Target Group
        target_group = campaign_manager.create_user_group(
            subscription_name=subscription["name"],
            deception_level=deception_level,
            index=index,
            target_list=targets,
        )
        return_data.update(
            {"groups": [campaign_serializers.GoPhishGroupSerializer(target_group).data]}
        )

        # Create Email Template
        created_template = campaign_manager.create_email_template(
            name=f"{base_name}.{template['name']}",
            template=template["data"],
            text=BeautifulSoup(template["data"], "html.parser").get_text(),
            subject=template["subject"],
        )
        return_data.update(
            {
                "email_template": created_template.name,
                "email_template_id": created_template.id,
                "template_uuid": str(template["template_uuid"]),
            }
        )

        # Calculate Campaign Start and End Date
        campaign_start = start_date
        campaign_end = start_date + timedelta(
            minutes=get_campaign_minutes(
                subscription.get("cycle_length_minutes", 129600)
            )
        )

        # Generate Campaign Name
        campaign_name = f"{base_name}.{template['name']}.{campaign_start.strftime('%Y-%m-%d')}.{campaign_end.strftime('%Y-%m-%d')}"

        # Create Sending Profile
        sending_profile = __create_campaign_smtp(
            campaign_name,
            template["from_address"],
            subscription["subscription_uuid"],
            subscription["sending_profile_name"],
        )
        return_data.update(
            {"smtp": campaign_serializers.GoPhishSmtpSerializer(sending_profile).data}
        )

        # Create Campaign
        campaign = campaign_manager.create_campaign(
            campaign_name=campaign_name,
            smtp_name=sending_profile.name,
            page_name=landing_page,
            user_group=target_group,
            email_template=created_template,
            launch_date=start_date.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            send_by_date=(campaign_end).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            url=__get_campaign_url(sending_profile),
        )
        return_data.update(
            {
                "campaign_id": campaign.id,
                "name": campaign_name,
                "created_date": format_ztime(campaign.created_date),
                "launch_date": campaign_start,
                "send_by_date": campaign_end,
                "landing_page_template": campaign.page.name,
                "deception_level": deception_level,
                "status": campaign.status,
                "results": [],
                "phish_results": {
                    "sent": 0,
                    "opened": 0,
                    "clicked": 0,
                    "submitted": 0,
                    "reported": 0,
                },
                "timeline": [
                    {
                        "email": None,
                        "time": format_ztime(campaign.created_date),
                        "message": "Campaign Created",
                        "details": "",
                    }
                ],
                "target_email_list": targets,
            }
        )
    except Exception as e:
        logging.exception(e)
        stop_campaign(return_data, cleanup=True)
        raise e

    # Return Campaign
    return return_data


def __get_campaign_url(sending_profile):
    sp_domain = (
        sending_profile.from_address.split("<")[-1].split("@")[1].replace(">", "")
    )
    return f"http://{GP_LANDING_SUBDOMAIN}.{sp_domain}"


def __create_campaign_smtp(
    campaign_name,
    template_from_address,
    subscription_uuid,
    subscription_sending_profile_name,
):
    sending_profiles = campaign_manager.get_sending_profile()
    sending_profile = next(
        iter(
            [p for p in sending_profiles if p.name == subscription_sending_profile_name]
        ),
        None,
    )

    __set_smtp_headers(sending_profile, subscription_uuid)

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
    """Get campaign from address."""
    # Get template display name
    if "<" in template_from_address:
        template_display = template_from_address.split("<")[0].strip()
    else:
        template_display = None

    # Get template sender
    template_sender = template_from_address.split("@")[0].split("<")[-1]

    # Get sending profile domain
    if type(sending_profile) is dict:
        sp_from = sending_profile["from_address"]
    else:
        sp_from = sending_profile.from_address
    sp_domain = sp_from.split("<")[-1].split("@")[1].replace(">", "")

    # Generate from address
    if template_display:
        from_address = f"{template_display} <{template_sender}@{sp_domain}>"
    else:
        from_address = f"{template_sender}@{sp_domain}"
    return from_address


def __set_smtp_headers(sending_profile, subscription_uuid):
    if not sending_profile.headers:
        sending_profile.headers = []

    set_x_gophish_contact_header(sending_profile)

    set_dhs_phish_header(sending_profile, subscription_uuid)


def set_dhs_phish_header(sending_profile, subscription_uuid):
    """Set DHS Phish Header."""
    for header in sending_profile.headers:
        if header["key"] == "CISA-PHISH":
            header["value"] = subscription_uuid
            return

    new_header = {"key": "CISA-PHISH", "value": subscription_uuid}
    sending_profile.headers.append(new_header)
    return


def set_x_gophish_contact_header(sending_profile):
    """Set X Gophish Contact Header."""
    for header in sending_profile.headers:
        if header["key"] == "X-Gophish-Contact":
            header["value"] = DEFAULT_X_GOPHISH_CONTACT
            return

    if DEFAULT_X_GOPHISH_CONTACT:
        new_header = {"key": "X-Gophish-Contact", "value": DEFAULT_X_GOPHISH_CONTACT}
        sending_profile.headers.append(new_header)

    return
