"""ReportView Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import customer, recommendation, subscription, template


@pytest.mark.django_db
def test_report_view_get(client):
    """Test ReportView Get."""
    with mock.patch(
        "api.services.SubscriptionService.get",
        return_value=subscription(),
    ) as mock_get_single, mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[subscription()],
    ), mock.patch(
        "api.services.TemplateService.get_list",
        return_value=[template()],
    ) as mock_get_template_list, mock.patch(
        "api.services.CustomerService.get",
        return_value=customer(),
    ), mock.patch(
        "api.services.CustomerService.get_list",
        return_value=[customer()],
    ), mock.patch(
        "api.services.RecommendationService.get_list",
        return_value=[recommendation()],
    ):
        result = client.get("/api/v1/reports/1234/")
        assert mock_get_single.called
        assert mock_get_template_list.called

        assert result.status_code == 200
