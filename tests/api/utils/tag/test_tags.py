from unittest import mock

from src.api.utils.tag import tags


@mock.patch("api.utils.db_utils.get_list")
def test_get_tags(db_get_list):
    tags.get_tags()
    assert db_get_list.called


def test_check_tag_format():
    tag1 = "<%TEST%>"
    assert tags.check_tag_format(tag1)

    tag2 = "<%test%>"
    assert not tags.check_tag_format(tag2)

    tag3 = "%test%"
    assert not tags.check_tag_format(tag3)


def test_get_faker_tags():
    faker_tags = tags.get_faker_tags()
    for tag in faker_tags:
        assert tag["tag"].startswith("<%FAKER")
        assert tags.check_tag_format(tag["tag"])
