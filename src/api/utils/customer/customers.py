from api.utils import db_utils as db
from api.models.customer_models import CustomerModel, validate_customer


def get_customer(customer_uuid: str):
    """
    Returns a customer from database

    Parameters:
        customer_uuid (str): uuid of customer to return.

    Returns:
        dict: returns a customer in dict format
    """
    return db.get_single(customer_uuid, "customer", CustomerModel, validate_customer)


def get_full_customer_address(customer_info):
    """
    Get_full_customer_address.

    When passed customer info, it will return an assemebed full address.
    """
    full_address = []
    full_address.append(customer_info["address_1"])
    if customer_info.get("address_2"):
        full_address.append(customer_info["address_2"])
    full_address.append(customer_info["city"])
    full_address.append(customer_info["state"])
    full_address.append(customer_info["zip_code"])

    return "\n".join(full_address)
