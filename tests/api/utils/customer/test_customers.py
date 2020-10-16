from faker import Faker

from src.api.utils.customer import customers


def test_get_full_customer_address():
    fake = Faker()
    street_address = fake.street_address()
    city = fake.city()
    state = fake.state()
    zip_code = fake.zipcode()

    customer_info = {
        "address_1": street_address,
        "address_2": "",
        "city": city,
        "state": state,
        "zip_code": zip_code,
    }

    full_address = customers.get_full_customer_address(customer_info)
    assert full_address == f"{street_address}\n{city}\n{state}\n{zip_code}"

    customer_info["address_2"] = street_address
    full_address = customers.get_full_customer_address(customer_info)
    assert (
        full_address
        == f"{street_address}\n{street_address}\n{city}\n{state}\n{zip_code}"
    )
