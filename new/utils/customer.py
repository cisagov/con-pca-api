"""Customer utils."""


def get_customer_name(customer):
    """Get customer name."""
    return customer["name"]


def get_customer_identifier(customer):
    """Get customer identifier."""
    return customer["identifier"]


def get_customer_state(customer):
    """Get customer state."""
    return customer["state"]


def get_customer_city(customer):
    """Get customer city."""
    return customer["city"]


def get_customer_zip(customer):
    """Get customer zipcode."""
    return customer["zip_code"]


def get_full_customer_address(customer):
    """Get Full Customer Address."""
    full_address = []
    full_address.append(customer["address_1"])
    if customer.get("address_2"):
        full_address.append(customer["address_2"])
    full_address.append(customer["city"])
    full_address.append(customer["state"])
    full_address.append(customer["zip_code"])

    return "\n".join(full_address)
