"""Reports Cycle View Test."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import customer, cycle, dhs_contact, recommendation, subscription, template


@pytest.mark.django_db
def test_cycle_view_get(client):
    """Test Get."""
    with mock.patch(
        "api.services.SubscriptionService.get",
        return_value=subscription(),
    ), mock.patch(
        "api.services.CustomerService.get",
        return_value=customer(),
    ), mock.patch(
        "api.services.DHSContactService.get",
        return_value=dhs_contact(),
    ), mock.patch(
        "api.services.TemplateService.get_list",
        return_value=[template()],
    ), mock.patch(
        "reports.utils.get_closest_cycle_within_day_range",
        return_value=cycle(),
    ), mock.patch(
        "api.services.CustomerService.get_list",
        return_value=[customer()],
    ), mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[subscription()],
    ), mock.patch(
        "api.services.RecommendationService.get_list",
        return_value=[recommendation()],
    ):
        result = client.get("/reports/1234/cycle/2020-07-30T19:37:54.960Z/")
        assert result.status_code == 202


@pytest.mark.django_db
def test_cycle_status_view_get(client):
    """Test Get."""
    with mock.patch(
        "api.services.SubscriptionService.get",
        return_value=subscription(),
    ), mock.patch(
        "api.services.CustomerService.get",
        return_value=customer(),
    ), mock.patch(
        "api.services.DHSContactService.get",
        return_value=dhs_contact(),
    ), mock.patch(
        "api.services.TemplateService.get_list",
        return_value=[template()],
    ), mock.patch(
        "reports.utils.get_closest_cycle_within_day_range",
        return_value=cycle(),
    ), mock.patch(
        "api.services.CustomerService.get_list",
        return_value=[customer()],
    ), mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[subscription()],
    ), mock.patch(
        "api.services.RecommendationService.get_list",
        return_value=[recommendation()],
    ):
        result = client.get("/reports/1234/subscription-stats-page/1234/")
        assert result.status_code == 202
