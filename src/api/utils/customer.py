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


def format_customer_address(customer):
    """Format customer address."""
    return f"""
    {customer.get('address_1')} {customer.get('address_2')},
    {customer.get('state')} USA {customer.get('zip_code')},
    """


def format_customer_address_1(customer):
    """Format customer address."""
    return f"{customer.get('address_1')},\n{customer.get('address_2')}"


def format_customer_address_2(customer):
    """Format customer address."""
    return f"{customer.get('city')}, {customer.get('state')} {customer.get('zip_code')} USA"


def get_company(customer):
    """Get customer info."""
    return {
        "name": customer.get("name"),
        "address": f"{customer.get('address_1')} {customer.get('address_2')}",
        "city": customer.get("city"),
        "state": customer.get("state"),
        "zip_code": customer.get("zip_code"),
    }
