from src.api.utils import landing_pages

from unittest import mock


@mock.patch("pymongo.collection.Collection.update_many")
@mock.patch("pymongo.collection.Collection.update_one")
def test_clear_and_set_default(mock_one, mock_many):
    landing_pages.clear_and_set_default("test")
    assert mock_one.call_args.args == (
        {"landing_page_uuid": "test"},
        {"$set": {"is_default_template": True}},
    )
    assert mock_many.call_args.args == ({}, {"$set": {"is_default_template": False}})
    assert mock_one.called
    assert mock_many.called


@mock.patch("api.utils.db_utils.get_single")
def test_get_landing_page(mock_get):
    landing_pages.get_landing_page("")
    assert mock_get.called
