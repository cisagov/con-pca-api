"""Personalize Templates Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
from faker import Faker

# cisagov Libraries
from src.api.utils.tag.tags import get_faker_tags
from src.api.utils.template import personalize
from src.scripts.init import load_file

fake = Faker()

customer_info = {
    "name": fake.company(),
    "address_1": fake.street_address(),
    "city": fake.city(),
    "state": fake.state(),
    "zip_code": fake.zipcode(),
}


def test_customer_name():
    """Test Customer Name."""
    tag_list = [
        {
            "tag": "<%CUSTOMER_NAME%>",
            "data_source": "customer_info['name']",
            "tag_type": "con-pca-eval",
        }
    ]
    template_data = [
        {
            "template_uuid": "2",
            "name": "test",
            "html": "<%CUSTOMER_NAME%> test",
            "subject": "test",
            "from_address": "<%CUSTOMER_NAME%> <test@test.com>",
        }
    ]
    result = personalize.personalize_template(
        customer_info, template_data, {}, tag_list
    )
    assert result[0]["data"].startswith(customer_info["name"])
    assert result[0]["from_address"] == f"{customer_info['name']} <test@test.com>"


@mock.patch("gophish.Gophish")
def test_tags_file(mocked_gophish):
    """Test tags file."""
    tags = load_file("data/tags.json")
    for tag in tags:
        template_data = [
            {
                "template_uuid": "1",
                "name": "test",
                "html": f"{tag['tag']}",
                "subject": "test",
                "from_address": "test@test.com",
            }
        ]

        result = personalize.personalize_template(
            customer_info, template_data, {}, tags
        )
        if tag["tag_type"] == "gophish":
            assert result[0]["data"].startswith(tag["data_source"])

        else:
            assert not result[0]["data"].startswith(tag["tag"])


def test_faker_tags():
    """Test faker tags."""
    tags = get_faker_tags()
    for tag in tags:
        template_data = [
            {
                "template_uuid": "1",
                "name": "test",
                "html": f"{tag['tag']}",
                "subject": "test",
                "from_address": "test@test.com",
            }
        ]

        result = personalize.personalize_template(
            customer_info, template_data, {}, tags
        )

        assert not result[0]["data"].startswith(tag["tag"])
