from src.api.utils import sector_industry_utils


def test_get_sector_industries():
    result = sector_industry_utils.get_sectors_industries()
    assert type(result) is list
    assert len(result) == 16
