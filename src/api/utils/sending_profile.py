import uuid
import copy
import logging
from api.manager import CampaignManager


def deal_with_sending_profiles(subscription):
    # determine if we need to create a new default sending profile
    # for this subscription or not
    # the basic rule is each subscription should have only one sending profile
    # if a sending profile ends with the subscription name then don't create a new one
    # just update it with the new header guid
    # else create a new one.
    campaign_manager = CampaignManager()
    sending_profiles = campaign_manager.get("sending_profile")
    sending_profile_name = subscription["sending_profile_name"]
    new_header_value = str(uuid.uuid4())

    if sending_profile_name.endswith(subscription["name"]):
        # we are going to update it
        sending_profile_to_clone = next(
            iter([p for p in sending_profiles if p.name == sending_profile_name]), None
        )
    else:
        sending_profile_to_clone = next(
            iter([p for p in sending_profiles if p.name == sending_profile_name]), None
        )
        # check to make sure it is really not there
        sending_profile_name = sending_profile_name + "_" + subscription["name"]
        sending_profile_to_new_name = next(
            iter([p for p in sending_profiles if p.name == sending_profile_name]), None
        )
        if sending_profile_to_new_name:
            sending_profile_to_clone = sending_profile_to_new_name
        else:
            # ok it is really not there so clone it
            # this is not necessary
            sending_profile_to_clone = copy.deepcopy(sending_profile_to_clone)

    # check to see if sending profile exists
    # if so update it else create it.
    # get the id of the sending profile we want

    new_headers = None
    if not sending_profile_to_clone.headers:
        new_headers = [{"key": "DHS-PHISH", "value": new_header_value}]
    else:
        # update the header with the new value
        header = next(
            iter(
                [h for h in sending_profile_to_clone.headers if h["key"] == "DHS-PHISH"]
            ),
            None,
        )
        header["value"] = new_header_value

    if sending_profile_to_clone is None:
        logging.info("Creating sending profile")
        campaign_manager.create(
            "sending_profile",
            name=sending_profile_name,
            username=sending_profile_to_clone.username,
            password=sending_profile_to_clone.password,
            host=sending_profile_to_clone.host,
            interface_type=sending_profile_to_clone.interface_type,
            from_address=sending_profile_to_clone.from_address,
            ignore_cert_errors=sending_profile_to_clone.ignore_cert_errors,
            headers=new_headers,
        )
    else:
        campaign_manager.put_sending_profile(sending_profile_to_clone)

    subscription["sending_profile_name"] = sending_profile_name
    # clone the sending profile changing the header value
    # create the new sending profile
    # tell the new campaigns to and cycle to use that profile
