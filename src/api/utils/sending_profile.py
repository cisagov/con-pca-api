import uuid
from api.manager import CampaignManager

campaign_manager = CampaignManager()


def deal_with_sending_profiles(subscription):
    sending_profiles = campaign_manager.get("sending_profile")
    sending_profile_name = subscription["sending_profile_name"]

    sending_profile = next(
        iter([p for p in sending_profiles if p.name == sending_profile_name]), None
    )

    if not sending_profile_name.endswith(subscription["name"]):
        sending_profile_name = sending_profile_name + "_" + subscription["name"]

        # check to make sure it is really not there
        existing_sending_profile = next(
            iter([p for p in sending_profiles if p.name == sending_profile_name]), None
        )

        # If sending profile already exists, update existing profile
        if existing_sending_profile:
            update_existing_sending_profile(existing_sending_profile)
        # Otherwise Create new profile
        else:
            create_new_sending_profile(sending_profile_name, sending_profile)
    # If sending profile unchanged, update header
    else:
        update_existing_sending_profile(sending_profile)

    subscription["sending_profile_name"] = sending_profile_name


def update_existing_sending_profile(sending_profile):
    set_sending_profile_headers(sending_profile)
    campaign_manager.put_sending_profile(sending_profile)


def create_new_sending_profile(name, sending_profile):
    set_sending_profile_headers(sending_profile)
    campaign_manager.create(
        "sending_profile",
        name=name,
        username=sending_profile.username,
        password=sending_profile.password,
        host=sending_profile.host,
        interface_type=sending_profile.interface_type,
        from_address=sending_profile.from_address,
        ignore_cert_errors=sending_profile.ignore_cert_errors,
        headers=sending_profile.headers,
    )


def set_sending_profile_headers(sending_profile):
    new_header = {"key": "DHS-PHISH", "value": str(uuid.uuid4())}

    if not sending_profile.headers:
        sending_profile.headers = [new_header]
        return

    # check if header exists
    exists = check_dhs_phish_header(sending_profile, new_header["value"])

    if not exists:
        sending_profile.headers.append(new_header)


def check_dhs_phish_header(sending_profile, new_uuid):
    for header in sending_profile.headers:
        if header["key"] == "DHS-PHISH":
            header["value"] = new_uuid
            return True
    return False
