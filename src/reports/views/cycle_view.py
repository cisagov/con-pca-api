"""Cycle Report View."""
# Standard Python Libraries
from datetime import datetime, timedelta

# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.manager import CampaignManager
from api.services import (
    CustomerService,
    DHSContactService,
    RecommendationService,
    SubscriptionService,
)
from reports.utils import (
    campaign_templates_to_string,
    deception_stats_to_graph_format,
    format_timedelta,
    get_closest_cycle_within_day_range,
    get_cycles_breakdown,
    get_most_successful_campaigns,
    get_related_subscription_stats,
    get_relevant_recommendations,
    get_reports_to_click,
    get_statistic_from_group,
    get_statistic_from_region_group,
    get_subscription_stats_for_cycle,
    get_template_details,
    ratio_to_percent,
    ratio_to_percent_zero_default,
    set_cycle_quarters,
)

# GoPhish API Manager
campaign_manager = CampaignManager()

recommendation_service = RecommendationService()
subscription_service = SubscriptionService()
dhs_contact_service = DHSContactService()
customer_service = CustomerService()


class CycleReportsView(APIView):
    """CycleReportsView."""

    def get(self, request, **kwargs):
        """Generate the cycle report based off of the provided start date."""
        # Get Args from url
        subscription_uuid = self.kwargs["subscription_uuid"]
        start_date_param = self.kwargs["start_date"]
        start_date = datetime.strptime(start_date_param, "%Y-%m-%dT%H:%M:%S.%f%z")
        # Get targeted subscription and associated customer data
        subscription = subscription_service.get(subscription_uuid)
        _customer = customer_service.get(subscription.get("customer_uuid"))

        company = {
            "name": _customer.get("name"),
            "address": f"{_customer.get('address_1')} {_customer.get('address_2')}",
            "city": _customer.get("city"),
            "state": _customer.get("state"),
            "zip_code": _customer.get("zip_code"),
        }

        # start_date = subscription["start_date"]

        subscription_primary_contact = subscription.get("primary_contact")

        customer = {
            "full_name": _customer.get("name"),
            "short_name": _customer.get("identifier"),
            "address_1": _customer.get("address_1"),
            "address_2": _customer.get("address_2"),
            "city": _customer.get("city"),
            "state": _customer.get("state"),
            "zip_code": _customer.get("zip_code"),
            "identifier": _customer.get("identifier"),
            "poc_email": None,
            "vulnerabilty_team_lead_name": None,
            "vulnerabilty_team_lead_email": None,
        }
        cycles = subscription["cycles"]
        set_cycle_quarters(cycles)

        current_cycle = None

        cycles_filter = list(filter(lambda x: x["start_date"] == start_date, cycles))

        if cycles_filter:
            current_cycle = cycles_filter[0]
        else:
            current_cycle = get_closest_cycle_within_day_range(subscription, start_date)

        # if cycle is None:
        #     return "Cycle not found"
        dates = {
            "start": current_cycle["start_date"],
            "end": current_cycle["end_date"],
        }

        # Get statistics for the specified subscription during the specified cycle
        subscription_stats, total_targets = get_subscription_stats_for_cycle(
            subscription, cycle_uuid=current_cycle["cycle_uuid"], start_date=None
        )
        region_stats = get_related_subscription_stats(subscription, start_date)
        previous_cycle_stats = get_cycles_breakdown(subscription["cycles"])

        # Get template details for each campaign template
        get_template_details(subscription_stats["campaign_results"])

        metrics = {
            "total_users_targeted": total_targets,
            "number_of_email_sent_overall": get_statistic_from_group(
                subscription_stats, "stats_all", "sent", "count"
            ),
            "number_of_clicked_emails": get_statistic_from_group(
                subscription_stats, "stats_all", "clicked", "count"
            ),
            "percent_of_clicked_emails": ratio_to_percent(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "ratios", "clicked_ratio"
                )
            ),
            "percent_of_submits": ratio_to_percent(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "ratios", "submitted_ratio"
                )
            ),
            "number_of_opened_emails": get_statistic_from_group(
                subscription_stats, "stats_all", "opened", "count"
            ),
            "number_of_phished_users_overall": get_statistic_from_group(
                subscription_stats, "stats_all", "submitted", "count"
            ),
            "percent_report_rate": ratio_to_percent(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "ratios", "reported_ratio"
                )
            ),
            "number_of_reports_to_helpdesk": get_statistic_from_group(
                subscription_stats, "stats_all", "reported", "count"
            ),
            "reports_to_clicks_ratio": ratio_to_percent(
                get_reports_to_click(subscription_stats), 2
            ),
            "avg_time_to_first_click": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "clicked", "average"
                )
            ),
            "median_time_to_first_click": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "clicked", "median"
                )
            ),
            "avg_time_to_first_report": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "reported", "average"
                )
            ),
            "most_successful_template": campaign_templates_to_string(
                get_most_successful_campaigns(subscription_stats, "reported")
            ),
            "emails_sent_over_target_count": round(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "sent", "count", zeroIfNone=True
                )
                / total_targets,
                0,
            ),
            "customer_clicked_avg": ratio_to_percent_zero_default(
                get_statistic_from_region_group(
                    region_stats, "customer", "clicked_ratio"
                ),
                0,
            ),
            "national_clicked_avg": ratio_to_percent_zero_default(
                get_statistic_from_region_group(
                    region_stats, "national", "clicked_ratio"
                ),
                0,
            ),
            "industry_clicked_avg": ratio_to_percent_zero_default(
                get_statistic_from_region_group(
                    region_stats, "industry", "clicked_ratio"
                ),
                0,
            ),
            "sector_clicked_avg": ratio_to_percent_zero_default(
                get_statistic_from_region_group(
                    region_stats, "sector", "clicked_ratio"
                ),
                0,
            ),
            "shortest_time_to_open": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "opened", "minimum"
                )
            ),
            "shortest_time_to_report": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "reported", "minimum"
                )
            ),
            "median_time_to_report": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "reported", "median"
                )
            ),
            "median_time_to_open": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "opened", "median"
                )
            ),
            "longest_time_to_open": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "opened", "maximum"
                )
            ),
        }

        # ------
        dhs_contact = dhs_contact_service.get(subscription.get("dhs_contact_uuid"))
        dhs_contact_name = (
            f"{dhs_contact.get('first_name')} {dhs_contact.get('last_name')}"
        )
        primary_contact = subscription.get("primary_contact")

        click_time_vs_report_time = self._click_time_vs_report_time(subscription_stats)

        templates_by_group = []

        templates_by_group.append(
            [
                x
                for x in subscription_stats["campaign_results"]
                if x["deception_level"] == 1
            ]
        )
        templates_by_group.append(
            [
                x
                for x in subscription_stats["campaign_results"]
                if x["deception_level"] == 2
            ]
        )
        templates_by_group.append(
            [
                x
                for x in subscription_stats["campaign_results"]
                if x["deception_level"] == 3
            ]
        )

        # Get recommendations for campaign
        recommendation_uuids = get_relevant_recommendations(subscription_stats)

        _recomendations = recommendation_service.get_list()
        recomendations = []
        for rec in _recomendations:
            if rec["recommendations_uuid"] in recommendation_uuids:
                recomendations.append(rec)

        context = {}
        context["dhs_contact_name"] = dhs_contact_name
        context["subscription_uuid"] = subscription_uuid
        context["primary_contact"] = primary_contact
        context["primary_contact_email"] = primary_contact.get("email")
        context["company"] = company
        context["subscription_primary_contact"] = subscription_primary_contact
        context["DHS_contact"] = dhs_contact
        context["customer"] = customer
        context["dates"] = dates
        context["cycles"] = cycles
        context["target_cycle"] = current_cycle
        context["metrics"] = metrics
        context["previous_cycles"] = previous_cycle_stats
        context["region_stats"] = region_stats
        context["subscription_stats"] = subscription_stats
        context["click_time_vs_report_time"] = click_time_vs_report_time
        context["templates_by_group"] = templates_by_group
        context["recommendations"] = recomendations

        return Response(context, status=status.HTTP_202_ACCEPTED)

    def _click_time_vs_report_time(self, subscription_stats):
        click_time_vs_report_time = []
        for campaign in subscription_stats["campaign_results"]:
            try:
                first_click = campaign["campaign_stats"]["clicked"]["minimum"]
            except Exception:
                first_click = timedelta()
            try:
                first_report = campaign["campaign_stats"]["reported"]["minimum"]
            except Exception:
                first_report = timedelta()

            difference = "N/A"
            if first_click > timedelta() and first_report > timedelta():
                difference = format_timedelta(first_click - first_report)
            click_time_vs_report_time.append(
                {
                    "level": campaign["deception_level"],
                    "time_to_first_click": format_timedelta(first_click),
                    "time_to_first_report": format_timedelta(first_report),
                    "difference": difference,
                }
            )
        return click_time_vs_report_time


class CycleStatusView(APIView):
    """CycleStatusView."""

    def get(self, request, **kwargs):
        """Get."""
        cycle_uuid = self.kwargs["cycle_uuid"]

        # Get targeted subscription and associated customer data
        subscription_uuid = self.kwargs["subscription_uuid"]
        subscription = subscription_service.get(subscription_uuid)

        # Get statistics for the specified subscription during the specified cycle
        subscription_stats, total_targets = get_subscription_stats_for_cycle(
            subscription, cycle_uuid=cycle_uuid, start_date=None
        )
        get_template_details(subscription_stats["campaign_results"])

        context = {
            "avg_time_to_first_click": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "clicked", "average"
                )
            ),
            "avg_time_to_first_report": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "reported", "average"
                )
            ),
            "sent": get_statistic_from_group(
                subscription_stats, "stats_all", "sent", "count"
            ),
            "target_count": total_targets,
            "campaign_details": subscription_stats["campaign_results"],
            "aggregate_stats": subscription_stats["stats_all"],
            # "stats": subscription_stats,
            "levels": deception_stats_to_graph_format(subscription_stats),
        }

        return Response(context, status=status.HTTP_202_ACCEPTED)
