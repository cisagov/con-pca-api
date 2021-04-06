"""
This is a stript to load dummy reporting data.

Here data is loaded via api call to test both api traffic
load and creation of data.
"""
# Standard Python Libraries
from datetime import datetime, timedelta
import json
import os
import random
import time

# Third-Party Libraries
import requests


def load_file(data_file):
    """Load json file of dummy data from data/dummy_data.json."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, data_file)
    with open(data_file, "r") as f:
        data = json.load(f)
    return data


def main():
    """Run Main."""
    print("loading dummy json data")
    json_data = load_file("data/reporting_dummy_data.json")
    print("done loading data")

    print("Step 2/3: create customers...")

    customers = json_data["customer_data"]
    created_customer_uuids = []
    for customer in customers:
        print(customer)
        try:
            resp = requests.post(
                "http://localhost:8000/api/v1/customers/", json=customer
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise err

        try:
            resp_json = resp.json()
            created_customer_uuid = resp_json["customer_uuid"]
            print("created customer_uuid: {}".format(created_customer_uuid))
            created_customer_uuids.append(created_customer_uuid)
        except Exception as err:
            print(err)
            pass

    print("Creating dhs contacts")
    dhs_contacts = json_data["dhs_contacts_data"]
    created_dhs_contacts_uuids = []
    for c in dhs_contacts:
        resp = requests.post("http://localhost:8000/api/v1/dhscontacts/", json=c)
        resp.raise_for_status()

        try:
            resp_json = resp.json()
            uuid = resp_json["dhs_contact_uuid"]
            print(f"created dhs contact uuid: {uuid}")
        except Exception as e:
            print(e)
            pass

        try:
            resp_json = resp.json()
            created_dhs_contact_uuid = resp_json["dhs_contact_uuid"]
            print("created customer_uuid: {}".format(created_dhs_contact_uuid))
            created_dhs_contacts_uuids.append(created_dhs_contact_uuid)
        except Exception as err:
            print(err)
            pass

    print("Step 3/3: create subscriptions...")

    subscriptions = json_data["subscription_data"]
    if not created_customer_uuids:
        print("customers already exist.. skipping")
        try:
            resp = requests.get("http://localhost:8000/api/v1/customers/")
            customers = resp.json()
            created_customer_uuids = [
                customer["customer_uuid"] for customer in customers
            ]
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise err

    if not created_dhs_contacts_uuids:
        print("dhs contacts already exist.. skipping")
        try:
            resp = requests.get("http://localhost:8000/api/v1/dhscontacts/")
            dhs_contacts = resp.json()
            created_dhs_contacts_uuids = [
                contact["dhs_contact_uuid"] for contact in dhs_contacts
            ]
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise err

    customer = created_customer_uuids[0]
    dhs_contact = created_dhs_contacts_uuids[0]
    created_subcription_uuids = []
    subscription = subscriptions[0]
    for customer in created_customer_uuids:
        subscription["customer_uuid"] = customer
        subscription["dhs_contact_uuid"] = dhs_contact
        subscription["start_date"] = datetime.today().strftime(
            "%Y-%m-%dT%H:%M:%S"
        )  # 2020-03-10T09:30:25"
        try:
            print(subscription)

            resp = requests.post(
                "http://localhost:8000/api/v1/subscriptions/", json=subscription
            )
            resp.raise_for_status()
            resp_json = resp.json()
            created_subcription_uuids.append(resp_json["subscription_uuid"])
        except requests.exceptions.HTTPError as err:
            print(err)

        time.sleep(5)

    print("created subcription_list: {}".format(created_subcription_uuids))
    print("Add previous data for reporting")
    for sub_id in created_customer_uuids:
        print(sub_id)

    customers = []
    try:
        resp = requests.get("http://localhost:8000/api/v1/customers/")
        resp.raise_for_status()
        customers = resp.json()
    except requests.exceptions.HTTPError as err:
        raise err
    subscriptions = []
    try:
        resp = requests.get("http://localhost:8000/api/v1/subscriptions/")
        resp.raise_for_status()
        subscriptions = resp.json()
    except requests.exceptions.HTTPError as err:
        raise err

    active_campaigns = []

    reporting_customer_idents = []
    for customer in json_data["customer_data"]:
        reporting_customer_idents.append(customer["identifier"])
    dummy_reporting_customers = []
    for customer in customers:
        if customer["identifier"] in reporting_customer_idents:
            dummy_reporting_customers.append(customer["customer_uuid"])

    dummy_reporting_subscriptions = []
    for subscription in subscriptions:
        if subscription["customer_uuid"] in dummy_reporting_customers:
            dummy_reporting_subscriptions.append(subscription)

    target_count = 0
    for sub in dummy_reporting_subscriptions:
        target_count += len(sub["target_email_list"])

    print(target_count)

    target_on = 0
    for subscription in subscriptions:
        active_campaigns = []
        for cycle in subscription["cycles"]:
            if cycle["active"]:
                active_campaigns = cycle["campaigns_in_cycle"]
        for campaign in subscription["campaigns"]:
            if campaign["campaign_id"] in active_campaigns:
                for target in campaign["target_email_list"]:
                    generate_webhooks_for_target(target, campaign["campaign_id"])
                    print(f"{target_on}/{target_count}")
                    target_on += 1


def generate_webhooks_for_target(target, campaign_id, start_date=-1, deception_rate=-1):
    """Generate Webhooks."""
    # Everywhere nosec is defined it's ignoring bandit random error, not used for security/cryptography purposes.
    # https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b311-random
    if deception_rate < 0:

        random.seed()  # nosec
        deception_rate = random.random()  # nosec
    webhooks = []
    if start_date == -1:
        last_event_time = datetime.utcnow()
    end_date = last_event_time + timedelta(days=90)

    webhooks.append(
        build_webhook(campaign_id, target["email"], last_event_time, "Email Sent")
    )
    if deception_rate > 0.3 and deception_rate < 0.95:
        last_event_time = get_date_in_range(
            last_event_time, end_date, random.random(), 0.5  # nosec
        )
        webhooks.append(
            build_webhook(campaign_id, target["email"], last_event_time, "Email Opened")
        )
        if deception_rate > 0.6 and deception_rate < 0.9:
            last_event_time = get_date_in_range(
                last_event_time, end_date, random.random()  # nosec
            )
            webhooks.append(
                build_webhook(
                    campaign_id, target["email"], last_event_time, "Clicked Link"
                )
            )
        if deception_rate > 0.75 and deception_rate < 0.85:
            last_event_time = get_date_in_range(
                last_event_time, end_date, random.random()  # nosec
            )
            webhooks.append(
                build_webhook(
                    campaign_id, target["email"], last_event_time, "Submitted Data"
                )
            )
    if deception_rate > 0.85:
        last_event_time = get_date_in_range(
            last_event_time, end_date, random.random()  # nosec
        )
        webhooks.append(
            build_webhook(
                campaign_id, target["email"], last_event_time, "Email Reported"
            )
        )

    for item in webhooks:
        try:
            resp = requests.post("http://localhost:8000/api/v1/inboundwebhook/", item)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise err


def build_webhook(camp_id, target_email, time, message):
    """Build Webhook."""
    return {
        "campaign_id": camp_id,
        "email": target_email,
        "time": time.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
        "message": message,
        "details": "",
    }


def get_date_in_range(start, end, rand_val, val_mod=1):
    """Get Date in Range."""
    if val_mod > 1:
        val_mod = 1 / val_mod
    start_time = start
    end_time = end

    delta = end_time - start_time
    result_time = start_time + ((delta * rand_val) * val_mod)

    return result_time


if __name__ == "__main__":
    main()
