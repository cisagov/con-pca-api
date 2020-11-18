"""Customer Utils."""


def get_full_customer_address(customer_info):
    """Get Full Customer Address."""
    full_address = []
    full_address.append(customer_info["address_1"])
    if customer_info.get("address_2"):
        full_address.append(customer_info["address_2"])
    full_address.append(customer_info["city"])
    full_address.append(customer_info["state"])
    full_address.append(customer_info["zip_code"])

    return "\n".join(full_address)
