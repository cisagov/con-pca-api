# Third-Party Libraries
from api.models.customer_models import CustomerModel, validate_customer
from api.utils import db_utils as db


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
    customer_full_address = "{} \n {} \n {}, {}, {}".format(
        customer_info["address_1"],
        customer_info["address_2"],
        customer_info["city"],
        customer_info["state"],
        customer_info["zip_code"],
    )
    return customer_full_address
