"""Test cases for reports aggregate related features."""

# Third-Party Libraries
import pytest


class TestReportsAggregate:
    """Test case for reports aggregate related views."""

    # def test_reports_aggregate_view(self, client):    ### Cannot use due to mongomock incompatibility with Latest mongo operations
    #     """Test the reports aggregates view."""
    #     resp = client.get("/api/reports/aggregate/")
    #     assert resp.status_code == 200

    #     self.check_reports_aggregate_properties(resp.json)

    @staticmethod
    def check_reports_aggregate_properties(reportsaggregate):
        """Check reportsaggregate object for expected properties."""
        if not isinstance(reportsaggregate, dict):
            pytest.fail("expected a dict")

        if reportsaggregate:

            if not isinstance(reportsaggregate["email_sending_stats"], dict):
                pytest.fail("expected a dict")

            if not isinstance(reportsaggregate["new_subscriptions"], int):
                pytest.fail("expected a int")

            if not isinstance(reportsaggregate["yearly_reports_sent"], int):
                pytest.fail("expected a int")

            if not isinstance(reportsaggregate["all_customer_stats"], dict):
                pytest.fail("expected a dict")

            if reportsaggregate["all_customer_stats"]:
                if not isinstance(reportsaggregate["all_customer_stats"]["all"], dict):
                    pytest.fail("expected a dict")

                    if reportsaggregate["all_customer_stats"]["all"]:
                        if not isinstance(
                            reportsaggregate["all_customer_stats"]["all"]["reported"],
                            dict,
                        ):
                            pytest.fail("expected a dict")

                        if (
                            reportsaggregate["all_customer_stats"]["all"]["clicked"][
                                "ratio"
                            ]
                            > 1
                        ):
                            pytest.fail("A ratio should <= 1")

                        if (
                            reportsaggregate["all_customer_stats"]["all"]["opened"][
                                "ratio"
                            ]
                            > 1
                        ):
                            pytest.fail("A ratio should <= 1")

                        if (
                            reportsaggregate["all_customer_stats"]["all"]["reported"][
                                "ratio"
                            ]
                            > 1
                        ):
                            pytest.fail("A ratio should <= 1")
            try:
                if not isinstance(
                    reportsaggregate["all_customer_stats"]["all"]["reported"]["count"],
                    int,
                ):
                    pytest.fail("expected a int for count")

                if not isinstance(
                    reportsaggregate["all_customer_stats"]["all"]["reported"][
                        "average"
                    ],
                    int,
                ):
                    pytest.fail("expected a int for average")

                if not isinstance(
                    reportsaggregate["all_customer_stats"]["all"]["reported"][
                        "maximum"
                    ],
                    int,
                ):
                    pytest.fail("expected a int for maximum")

                if not isinstance(
                    reportsaggregate["all_customer_stats"]["all"]["reported"]["median"],
                    int,
                ):
                    pytest.fail("expected a int for median")

                if not isinstance(
                    reportsaggregate["all_customer_stats"]["all"]["reported"]["ratio"],
                    float,
                ):
                    pytest.fail("expected a float")
            except KeyError:
                pytest.fail("reported properties do not exist")
