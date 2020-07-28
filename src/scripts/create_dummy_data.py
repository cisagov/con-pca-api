"""
This is a stript to load dummy data.

Here data is loaded via api call to test both api traffic
load and creation of data.

Steps to create:
First create templates,
then create targets,
then add targets and templates to subscriptions.

ToDo: create delete script to get all uuid's of dummy data and delete.
"""
# Standard Python Libraries
from datetime import datetime
import json
import os
import time

# Third-Party Libraries
import requests


def load_file(data_file):
    """This loads json file of dummy data from data/dummy_data.json."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, data_file)
    with open(data_file, "r") as f:
        data = json.load(f)
    return data


# def clean_up_first():
# """" drop the collections before starting to add data """
#  mongo_uri = "mongodb://{}:{}@{}:{}/".format(
#     settings.DB_CONFIG["DB_USER"],
#     settings.DB_CONFIG["DB_PW"],
#     settings.DB_CONFIG["DB_HOST"],
#     settings.DB_CONFIG["DB_PORT"],
# )
# client = MongoClient(mongo_uri)

def create_customers(customers):
    """Create Customers.

    Args:
        customers (list[dict]): Customer Post Dict

    Raises:
        err: Error from API, Non-200

    Returns:
        list: list of created uuid's
    """
    created_customer_uuids = []
    for customer in customers:
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
    
    return created_customer_uuids


def create_dhs_contacts(dhs_contacts):
    """Create DHS Contacts.

    Args:
        dhs_contacts (list[Dict]): DHS Post DICT

    Returns:
        list: Created Customer uuid
    """
    created_dhs_contacts_uuids = []
    for c in dhs_contacts:
        resp = requests.post("http://localhost:8000/api/v1/dhscontacts/", json=c)
        resp.raise_for_status()

        try:
            resp_json = resp.json()
            created_dhs_contact_uuid = resp_json["dhs_contact_uuid"]
            print("created dhs_contact_uuid: {}".format(created_dhs_contact_uuid))
            created_dhs_contacts_uuids.append(created_dhs_contact_uuid)
        except Exception as err:
            print(err)
            pass

    return created_dhs_contacts_uuids


def create_subscriptions(subscriptions, customer, dhs_contact):
    """Create Subscriptions.

    Args:
        subscriptions (list[dict]): List of subscription Post Dicts
        customer (dict): Customer data
        dhs_contact (dict): DHS Dict

    Returns:
        list: List of created uuid's
    """
    created_subcription_uuids = []
    for subscription in subscriptions:
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
    
    return created_subcription_uuids


def create_recommendations(recommendations):
    """Create Recommendations.

    Args:
        recommendations (list[dict]): List of Recommendation Post Dicts

    Returns:
        list: List of created Recommendation uuid's
    """
    created_recommendations_uuids = []
    for rec in recommendations:
        resp = requests.post("http://localhost:8000/api/v1/recommendations/", json=rec)
        resp.raise_for_status()

        try:
            resp_json = resp.json()
            created_recommendations_uuid = resp_json["recommendations_uuid"]
            print("created recommendations_uuid: {}".format(created_recommendations_uuid))
            created_recommendations_uuids.append(created_recommendations_uuid)
        except Exception as err:
            print(err)
            pass

    return created_recommendations_uuids


def main():
    """This if the main def that runs creating data."""
    print("Step 1/6: Loading Json Data")
    json_data = load_file("data/dummy_data.json")
    print("Done loading data")
    print("Step 2/6: Creating Customers")
    created_customer_uuids = create_customers(json_data["customer_data"])
    print("Step 3/6: Creating DHS Contacts")
    created_dhs_contacts_uuids = create_dhs_contacts(json_data["dhs_contacts_data"])
    print("Step 4/6: Create Recommendations")
    created_recommendations_uuids = create_recommendations(json_data["recommendations_data"])
    print("Step 5/6: Create Subscriptions")

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

    created_subcription_uuids = create_subscriptions(json_data["subscription_data"], created_customer_uuids[0], created_dhs_contacts_uuids[0])

    print("created subcription_list: {}".format(created_subcription_uuids))

    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(
        current_dir,
        "data/created_dummy_data_{}.json".format(
            datetime.now().strftime("%Y_%m_%d_%H%M%S")
        ),
    )
    print("Add previous data for reporting")
    for sub_id in created_customer_uuids:
        print(sub_id)


    print("Step 6/6: Writing values to file: {}".format(output_file))

    with open(output_file, "w") as outfile:
        data = {
            "created_customers": created_customer_uuids,
            "created_subcription_uuids": created_subcription_uuids,
            "created_recommendations_uuids": created_recommendations_uuids,
        }
        json.dump(data, outfile, indent=2)
    print("Finished.....")


if __name__ == "__main__":
    main()
