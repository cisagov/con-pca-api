from src.api.utils.tag import tags


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
