"""Reporting Utils."""
# Standard Python Libraries
from datetime import datetime, timedelta
import logging
import math
import statistics

# Third-Party Libraries
import dateutil
from django.utils import timezone
import pytz

# cisagov Libraries
from api.services import (
    CampaignService,
    CustomerService,
    RecommendationService,
    SubscriptionService,
    TemplateService,
)
from api.utils.subscription.static import DELAY_MINUTES

customer_service = CustomerService()
subscription_service = SubscriptionService()
template_service = TemplateService()
recommendation_service = RecommendationService()
campaign_service = CampaignService()


def get_closest_cycle_within_day_range(subscription, start_date, day_range=90):
    """
    Get a cycle from a subscription that started the closest to the provided start_date.

    Goes through the cycles attached to a subscription and returns the cycles that is closest
    to the start date. Must be within the specified day range as well, if not will return None
    """
    # set initial closest value to the difference between the first cycle and supplied start date
    maximum_date_differnce = timedelta(days=day_range)
    closest_cycle = None
    closest_val = abs(start_date - subscription["cycles"][0]["start_date"])
    # If the initial cycle is within the maximum_data_difference, set it as the cycle before checking others
    if closest_val < maximum_date_differnce:
        closest_cycle = subscription["cycles"][0]
    cycle_start_difference = 0
    for cycle in subscription["cycles"]:
        cycle_start_difference = abs(cycle["start_date"] - start_date)
        if (
            cycle_start_difference < closest_val
            and cycle_start_difference < maximum_date_differnce
        ):
            closest_cycle = cycle
            closest_val = cycle_start_difference
    if not closest_cycle:
        return None
    if closest_cycle:
        return closest_cycle
    else:
        print(
            f"{subscription['subscription_uuid']} does not have a cycle within the specified date range"
        )
        return None


def get_cycle_by_date_in_range(subscription, date):
    """Get the cycle that contains the given date."""
    date = _check_type(date)
    utc = pytz.UTC
    if not timezone.is_aware(date):
        date = utc.localize(date)

    for cycle in subscription["cycles"]:
        start_date = _check_type(cycle["start_date"])
        end_date = _check_type(cycle["end_date"])
        if not timezone.is_aware(start_date):
            start_date = utc.localize(start_date)
        if not timezone.is_aware(end_date):
            end_date = utc.localize(end_date)

        if start_date < date and end_date >= date:
            return cycle
    return subscription["cycles"][0]


def _check_type(date):
    if type(date) is str:
        date = dateutil.parser.parse(date)
    return date


def find_send_timeline_moment(email, timeline_items):
    """
    Find the send moment in timeline.

    Look through a statistial summary dictionary and find the tracked record corresponding
    to the provided email.
    """
    for moment in timeline_items:
        if moment["email"] == email:
            return moment
    return {}


def add_moment_no_duplicates(moment, result, message_type):
    """Add a timeline moment to the statistical summary, Ignoring duplicates."""
    previous_moment = find_send_timeline_moment(moment["email"], result)
    # if message_type in previous_moment:
    #     return  # Do not count duplicates
    previous_moment[message_type] = moment["time"]
    previous_moment[message_type + "_difference"] = (
        moment["time"] - previous_moment["sent"]
    )
    return


def append_timeline_moment(moment, result):
    """Take a timeline moment and add it to the statisitcal summary for the timeline."""
    if moment["message"] == "Email Sent":
        result.append({"email": moment["email"], "sent": moment["time"]})
        return
    elif moment["message"] == "Email Opened":
        add_moment_no_duplicates(moment, result, "opened")
        return
    elif moment["message"] == "Clicked Link":
        add_moment_no_duplicates(moment, result, "clicked")
        return
    elif moment["message"] == "Submitted Data":
        add_moment_no_duplicates(moment, result, "submitted")
        return
    elif moment["message"] == "Email Reported":
        add_moment_no_duplicates(moment, result, "reported")
        return


def generate_time_difference_stats(list_of_times):
    """Given a list of time_deltas, determine the min, max, median, avg, and count."""
    count = len(list_of_times)
    avg_val = sum(list_of_times, timedelta()) / count
    min_val = min(list_of_times)
    median_val = statistics.median(list_of_times)
    max_val = max(list_of_times)
    return {
        "count": count,
        "average": avg_val,
        "minimum": min_val,
        "median": median_val,
        "maximum": max_val,
    }


def generate_campaign_statistics(campaign_timeline_summary, reported_override_value=-1):
    """
    Generate campaign statistics based off a campaign_timeline_summary.

    Returns a list with stats, containing statistics for the campaign. Also returns a full aggregate of the
    times associated with each possible action (sent,opened,clicked,submitted, and reported) for statistical
    evaluation at a subscritpion level
    """
    time_stats = _get_time_stats(campaign_timeline_summary, reported_override_value)

    stats = {}
    time_aggregate = {}
    stats["sent"] = {"count": len(time_stats["send_times"])}
    time_aggregate["sent"] = time_stats["send_times"]
    if len(time_stats["opened_times"]):
        stats["opened"] = generate_time_difference_stats(time_stats["opened_times"])
        time_aggregate["opened"] = time_stats["opened_times"]
    if len(time_stats["clicked_times"]):
        stats["clicked"] = generate_time_difference_stats(time_stats["clicked_times"])
        time_aggregate["clicked"] = time_stats["clicked_times"]
    if len(time_stats["submitted_times"]):
        stats["submitted"] = generate_time_difference_stats(
            time_stats["submitted_times"]
        )
        time_aggregate["submitted"] = time_stats["submitted_times"]
    if len(time_stats["reported_times"]):
        if reported_override_value == -1:
            stats["reported"] = generate_time_difference_stats(
                time_stats["reported_times"]
            )
            time_aggregate["reported"] = time_stats["reported_times"]
        else:
            stats["reported"] = generate_time_difference_stats(
                time_stats["reported_times"]
            )
            stats["reported"] = {
                "count": reported_override_value,
                "average": timedelta(),
                "minimum": timedelta(),
                "median": timedelta(),
                "maximum": timedelta(),
            }
            time_aggregate["reported"] = time_stats["reported_times"]

    return stats, time_aggregate


def _get_time_stats(campaign_timeline_summary, reported_override_value):
    """Get Time Stats.

    Args:
        campaign_timeline_summary (list[dict]): list of campaign timelines
        reported_override_value (int): override value
    Returns:
        dict: dict of times for each stat
    """
    send_times = []
    opened_times = []
    clicked_times = []
    submitted_times = []
    reported_times = []
    for moment in campaign_timeline_summary:
        if "sent" in moment:
            send_times.append(moment["sent"])
        if "opened" in moment:
            opened_times.append(moment["opened_difference"])
        if "clicked" in moment:
            clicked_times.append(moment["clicked_difference"])
        if "submitted" in moment:
            submitted_times.append(moment["submitted_difference"])
        if "reported" in moment and reported_override_value == -1:
            reported_times.append(moment["reported_difference"])

    return {
        "send_times": send_times,
        "opened_times": opened_times,
        "clicked_times": clicked_times,
        "submitted_times": submitted_times,
        "reported_times": reported_times,
    }


def calc_ratios(campaign_stats):
    """
    Calc the ratios for a given list of phishing results.

    Accepts click breakdown model or phish_results model and converts
    the provided stats to the necesary format for computation.
    """
    # Convert to proper format for computation if not already
    working_vals = {}
    if campaign_stats:
        key_check = next(iter(campaign_stats))
        if key_check:
            if isinstance(campaign_stats[key_check], dict):
                for key in campaign_stats:
                    working_vals[key] = campaign_stats[key]["count"]
            else:
                working_vals = campaign_stats

    return _get_ratios(working_vals)


def _get_ratios(working_vals):
    clicked_ratio, opened_ratio, submitted_ratio, reported_ratio = (
        None,
        None,
        None,
        None,
    )

    # Get ratios
    if "sent" in working_vals:
        # Make sure you dont divide by zero
        if working_vals["sent"] != 0:
            if "clicked" in working_vals:
                clicked_ratio = working_vals["clicked"] / working_vals["sent"]
            if "opened" in working_vals:
                opened_ratio = working_vals["opened"] / working_vals["sent"]
            if "submitted" in working_vals:
                submitted_ratio = working_vals["submitted"] / working_vals["sent"]
            if "reported" in working_vals:
                reported_ratio = working_vals["reported"] / working_vals["sent"]

    return {
        "clicked_ratio": clicked_ratio,
        "opened_ratio": opened_ratio,
        "submitted_ratio": submitted_ratio,
        "reported_ratio": reported_ratio,
    }


def get_clicked_time_period_breakdown(campaign_results):
    """
    Get the clicked breakdown over time in ratio form.

    Takes campaign results list and generates a ratio for how many clicks have occured
    during each specified time delta (time deltas pulled from current cycle report example)
    """
    time_deltas = {
        "one_minute": (timedelta(minutes=1), 1),
        "three_minutes": (timedelta(minutes=3), 2),
        "five_minutes": (timedelta(minutes=5), 3),
        "fifteen_minutes": (timedelta(minutes=15), 4),
        "thirty_minutes": (timedelta(minutes=30), 5),
        "one_hour": (timedelta(hours=1), 6),
        "two_hours": (timedelta(hours=2), 7),
        "three_hours": (timedelta(hours=3), 8),
        "four_hours": (timedelta(hours=4), 9),
        "one_day": (timedelta(days=1), 10),
    }
    time_counts = {}
    clicked_ratios = {}
    for key in time_deltas:
        time_counts[key] = 0
        clicked_ratios[key] = 0

    clicked_count = 0
    for campaign in campaign_results:
        if "clicked" in campaign["times"]:
            for moment in campaign["times"]["clicked"]:
                clicked_count += 1
                for key in time_deltas:
                    if moment < time_deltas[key][0]:
                        time_counts[key] += 1
                        break

    if clicked_count:
        update_clicked_ratios(time_deltas, time_counts, clicked_ratios, clicked_count)

    return clicked_ratios


def update_clicked_ratios(time_deltas, time_counts, clicked_ratios, clicked_count):
    """Update clicked ratios."""
    last_key = None
    for i, key in enumerate(time_deltas, 0):
        if not last_key:
            last_key = key
            if time_counts[key] > 0:
                clicked_ratios[key] = time_counts[key] / clicked_count
        else:
            time_counts[key] += time_counts[last_key]
            clicked_ratios[key] = time_counts[key] / clicked_count
            last_key = key


def date_in_range(date, min_date, max_date):
    """Check if date is in range."""
    if date >= min_date and date <= max_date:
        return True
    return False


def filter_campaign_timeline_by_date_range(
    campaign_timeline_summary, start_date, end_date
):
    """Filter Campaign Timeline."""
    keys_to_remove = []
    for moment in campaign_timeline_summary:
        for key in moment:
            if key in ("sent", "opened", "clicked", "submitted", "reported"):
                if not date_in_range(moment[key], start_date, end_date):
                    keys_to_remove.append(key)
        for del_key in keys_to_remove:
            del moment[del_key]
        keys_to_remove = []


def get_subscription_stats_for_month(subscription, end_date, cycle_uuid=None):
    """
    Generate statistics for a subscriptions given month.

    Determine the month by the provided start_date, goes x amount of days past that depending on month_length.
    """
    # Get the correct cycle based on the provided start_date
    if cycle_uuid:
        active_cycle = subscription["cycles"][0]
        for cycle in subscription["cycles"]:
            if cycle["cycle_uuid"] == cycle_uuid:
                active_cycle = cycle
    else:
        active_cycle = get_cycle_by_date_in_range(subscription, end_date)

    # start_date = active_cycle["start_date"]
    # Get all the campaigns for the specified cycle from the campaigns
    campaigns_in_cycle = []
    for campaign in subscription["campaigns"]:
        if campaign["campaign_id"] in active_cycle["campaigns_in_cycle"]:
            campaigns_in_cycle.append(campaign)

    # Loop through all campaigns in cycle. Check for unique moments, and appending to campaign_timeline_summary
    campaign_timeline_summary = []
    campaign_results = []
    for campaign in campaigns_in_cycle:
        unique_moments = get_unique_moments(campaign["timeline"])
        for unique_moment in unique_moments:
            append_timeline_moment(unique_moment, campaign_timeline_summary)

        # Get stats and aggregate of all time differences (all times needed for stats like median when consolidated)
        stats, time_aggregate = generate_campaign_statistics(
            campaign_timeline_summary, active_cycle["override_total_reported"]
        )
        campaign_results.append(
            {
                "campaign_id": campaign["campaign_id"],
                "deception_level": campaign["deception_level"],
                "campaign_stats": stats,
                "times": time_aggregate,
                "ratios": calc_ratios(stats),
                "template_name": campaign["email_template"],
                "template_uuid": campaign["template_uuid"],
            }
        )
        campaign_timeline_summary = []

    return generate_subscription_stat_details(
        campaign_results, active_cycle["override_total_reported"]
    )


def get_subscription_stats_for_cycle(subscription, cycle_uuid=None, start_date=None):
    """
    Generate statistics for a subscriptions given cycle.

    Determine the cycle by the provided start_date.
    """
    if cycle_uuid:
        active_cycle = subscription["cycles"][0]
        for cycle in subscription["cycles"]:
            if cycle["cycle_uuid"] == cycle_uuid:
                active_cycle = cycle
    else:
        active_cycle = get_cycle_by_date_in_range(subscription, start_date)

    # Get all the campaigns for the specified cycle from the campaigns
    campaigns_in_cycle = []
    for campaign in subscription["campaigns"]:
        if campaign["campaign_id"] in active_cycle["campaigns_in_cycle"]:
            campaigns_in_cycle.append(campaign)

    # Loop through all campaigns in cycle. Check for unique moments, and appending to campaign_timeline_summary
    campaign_timeline_summary = []
    campaign_results = []
    for campaign in campaigns_in_cycle:
        unique_moments = get_unique_moments(campaign["timeline"])
        for unique_moment in unique_moments:
            append_timeline_moment(unique_moment, campaign_timeline_summary)
        # Get stats and aggregate of all time differences (all times needed for stats like median when consolidated)
        stats, time_aggregate = generate_campaign_statistics(
            campaign_timeline_summary, active_cycle["override_total_reported"]
        )
        campaign_results.append(
            {
                "campaign_id": campaign["campaign_id"],
                "deception_level": campaign["deception_level"],
                "campaign_stats": stats,
                "times": time_aggregate,
                "ratios": calc_ratios(stats),
                "template_name": campaign["email_template"],
                "template_uuid": campaign["template_uuid"],
            }
        )
        campaign_timeline_summary = []

    return (
        generate_subscription_stat_details(
            campaign_results, active_cycle["override_total_reported"]
        ),
        active_cycle["total_targets"],
    )


def get_subscription_stats_for_yearly(subscription, start_date=None, end_date=None):
    """
    Generate statistics for a subscriptions given span, Defaults to the last year if no dates provided.

    Determine the time span using start_date and end_date
    """
    # Determine start date if None
    if not end_date:
        # add offset to delay to capture todays cycles
        end_date = datetime.now() + timedelta(minutes=DELAY_MINUTES + 5)
    if not start_date:
        start_date = end_date - timedelta(days=365.25)

    if not timezone.is_aware(start_date):
        utc = pytz.UTC
        start_date = utc.localize(start_date)
    if not timezone.is_aware(end_date):
        utc = pytz.UTC
        end_date = utc.localize(end_date)

    # Get all cycles that have a date that lies within the given time gap
    cycles_in_year = list(
        filter(
            lambda x: cycle_in_yearly_timespan(
                x["start_date"], x["end_date"], start_date, end_date
            ),
            subscription["cycles"],
        )
    )

    _check_for_missing_values(cycles_in_year)
    campaigns_in_year = []
    for cycle in cycles_in_year:
        for campaign in cycle["campaigns_in_cycle"]:
            campaigns_in_year.append(campaign)
            cycle["campaigns"].append(campaign)

    campaigns_in_year = list(dict.fromkeys(campaigns_in_year))

    # Get all the campaigns for the specified cycle from the campaigns

    # Get the campaign info from the campaigns, and store in aggregate array
    # and hte cycle specific array
    campaigns_in_time_gap = list(
        filter(
            lambda x: x["campaign_id"] in campaigns_in_year, subscription["campaigns"]
        )
    )
    all_targets_dirty = []
    for campaign in subscription["campaigns"]:
        for cycle in cycles_in_year:
            if campaign["campaign_id"] in cycle["campaigns"]:
                cycle["campaign_list"].append(campaign)
                all_targets_dirty.extend(campaign["target_email_list"])

    # remove dups in list of targets
    all_targets_clean = []
    [
        all_targets_clean.append(x)
        for x in all_targets_dirty
        if x not in all_targets_clean
    ]

    total_unique_targets_in_year = len(all_targets_clean)

    # Loop through all campaigns in cycle. Check for unique moments, and appending to campaign_timeline_summary

    (
        campaign_results,
        reported_override_val,
        reported_override_val_total,
    ) = _get_campaign_results(campaigns_in_time_gap, subscription)

    _get_cycle_results(cycles_in_year, reported_override_val)

    return (
        generate_subscription_stat_details(
            campaign_results, reported_override_val_total
        ),
        cycles_in_year,
        total_unique_targets_in_year,
    )


def _get_cycle_results(cycles_in_year, reported_override_val):
    for cycle in cycles_in_year:
        cycle_timeline_summary = []
        cycle_results = []
        for campaign in cycle["campaign_list"]:
            unique_moments = get_unique_moments(campaign["timeline"])
            for unique_moment in unique_moments:
                append_timeline_moment(unique_moment, cycle_timeline_summary)
            reported_override_val = cycle["override_total_reported"]
            stats = None
            stats, time_aggregate = generate_campaign_statistics(
                cycle_timeline_summary, reported_override_val
            )
            cycle_results.append(
                {
                    "campaign_id": campaign["campaign_id"],
                    "deception_level": campaign["deception_level"],
                    "campaign_stats": stats,
                    "reported_override_val": reported_override_val,
                    "times": time_aggregate,
                    "ratios": calc_ratios(stats),
                    "template_name": campaign["email_template"],
                    "template_uuid": campaign["template_uuid"],
                }
            )
            cycle_timeline_summary = []
        cycle["cycle_results"] = generate_subscription_stat_details(
            cycle_results, reported_override_val
        )


def _get_campaign_results(campaigns_in_time_gap, subscription):
    campaign_timeline_summary = []
    campaign_results = []
    reported_override_val = -1
    reported_override_val_total = -1
    for campaign in campaigns_in_time_gap:
        unique_moments = get_unique_moments(campaign["timeline"])
        for unique_moment in unique_moments:
            append_timeline_moment(unique_moment, campaign_timeline_summary)
        # Get stats and aggregate of all time differences (all times needed for stats like median when consolidated)
        reported_override_val = get_override_total_reported_for_campagin(
            subscription, campaign
        )
        stats, time_aggregate = generate_campaign_statistics(
            campaign_timeline_summary, reported_override_val
        )
        campaign_results.append(
            {
                "campaign_id": campaign["campaign_id"],
                "deception_level": campaign["deception_level"],
                "campaign_stats": stats,
                "reported_override_val": reported_override_val,
                "times": time_aggregate,
                "ratios": calc_ratios(stats),
                "template_name": campaign["email_template"],
                "template_uuid": campaign["template_uuid"],
            }
        )
        if reported_override_val != -1:
            if reported_override_val_total == -1:
                reported_override_val_total = 0
            else:
                reported_override_val_total += reported_override_val
        reported_override_val = -1
        campaign_timeline_summary = []
    return campaign_results, reported_override_val, reported_override_val_total


def _check_for_missing_values(cycles_in_year):
    for cycle in cycles_in_year:
        if "campaigns" not in cycle:
            cycle["campaigns"] = []
        if "campaign_list" not in cycle:
            cycle["campaign_list"] = []


def get_override_total_reported_for_campagin(subscription, campaign):
    """Get override total reported."""
    for cycle in subscription["cycles"]:
        if campaign["campaign_id"] in cycle["campaigns_in_cycle"]:
            return cycle["override_total_reported"]


def cycle_in_yearly_timespan(cycle_start, cycle_end, yearly_start, yearly_end):
    """Check cycle in yearly timespan."""
    # Determine the cycels that lie within a yearly timespan
    # Three checks needed,
    # One: the first cycle possible
    # Two: any cycle directly within the yearly timespan
    # Three: the last cycle possible on that lies within the yearly timespan

    # Cycles: [-----][-----][-----][-----][-----]
    # Yearly:  [--------------------------]
    #            1      2       2     2      3
    # 1
    if cycle_start < yearly_start and cycle_end > yearly_start:
        return True
    # 2
    if cycle_start > yearly_start and cycle_end < yearly_end:
        return True
    # 3
    if cycle_start < yearly_end and cycle_end > yearly_end:
        return True
    return False


def get_unique_moments(campaign_timeline):
    """Get Unique Moments."""
    retVal = []
    sent_moments = []
    user_moments = []

    sent_moments[:] = (x for x in campaign_timeline if x["message"] == "Email Sent")
    user_moments[:] = (x for x in campaign_timeline if x["message"] != "Email Sent")

    # Sort the working timeline by date, first occurence of a moment
    # will be the one that is used for calculations
    user_moments.sort(key=lambda x: x["time"])

    # Find the first occurence of a opened/clicked/submitted/reported moment

    for sent_moment in sent_moments:
        sent_action_moments = []
        moments_to_get = [
            "Email Opened",
            "Clicked Link",
            "Submitted Data",
            "Email Reported",
        ]
        retVal.append(sent_moment)
        sent_action_moments = (
            x for x in user_moments if x["email"] == sent_moment["email"]
        )

        for action_moment in sent_action_moments:
            if action_moment["message"] in moments_to_get:
                retVal.append(action_moment)
                moments_to_get.remove(action_moment["message"])
            # user_moments.remove(action_moment)

    return retVal


def set_cycle_quarters(cycles):
    """Set Cycle Quarters."""
    cycles = sorted(cycles, key=lambda cycle: cycle["start_date"])
    working_cycle_year = cycles[0]["start_date"].year
    current_quarter = 1
    # Count the cycle order from the year or try to match up to standard 'quarters'?
    for num, cycle in enumerate(cycles, 0):
        if cycle["start_date"].year > working_cycle_year:
            current_quarter = 1
            working_cycle_year = cycle["start_date"].year
        cycle["quarter"] = f"{cycle['start_date'].year} - {current_quarter}"
        cycle["increment"] = num
        current_quarter += 1


def generate_subscription_stat_details(campaign_results, over_ride_report_val):
    """Generate Subscription Stat Details."""
    # generate campaign_group stats based off deception level and consolidation of all campaigns
    # All
    consolidated_stats = consolidate_campaign_group_stats(
        campaign_results, over_ride_report_val
    )

    consolidated_stats["ratios"] = calc_ratios(consolidated_stats)

    reported_override_val = -1
    if over_ride_report_val >= 0:
        reported_override_val = 0

    # Low
    low_decp_stats = consolidate_campaign_group_stats(
        list(filter(lambda x: x["deception_level"] == 1, campaign_results)),
        reported_override_val,
    )
    low_decp_stats["ratios"] = calc_ratios(low_decp_stats)

    # Moderate
    moderate_decp_stats = consolidate_campaign_group_stats(
        list(filter(lambda x: x["deception_level"] == 2, campaign_results)),
        reported_override_val,
    )
    moderate_decp_stats["ratios"] = calc_ratios(moderate_decp_stats)

    # High
    high_decp_stats = consolidate_campaign_group_stats(
        list(filter(lambda x: x["deception_level"] == 3, campaign_results)),
        reported_override_val,
    )
    high_decp_stats["ratios"] = calc_ratios(high_decp_stats)

    clicks_over_time = get_clicked_time_period_breakdown(campaign_results)

    return {
        "campaign_results": campaign_results,
        "stats_all": consolidated_stats,
        "stats_low_deception": low_decp_stats,
        "stats_mid_deception": moderate_decp_stats,
        "stats_high_deception": high_decp_stats,
        "clicks_over_time": clicks_over_time,
    }


def consolidate_campaign_group_stats(campaign_data_list, reported_override_value=-1):
    """Consolidate a group of campaign results."""
    consolidated_times = {
        "sent": [],
        "opened": [],
        "clicked": [],
        "submitted": [],
        "reported": [],
    }
    if not reported_override_value:
        reported_override_value = -1
    for campaign in campaign_data_list:
        for key in campaign["times"]:
            consolidated_times[key] += campaign["times"][key]

    return _get_consolidated_stats(consolidated_times, reported_override_value)


def _get_consolidated_stats(consolidated_times, reported_override_value):
    consolidated_stats = {}
    for key in consolidated_times:
        if reported_override_value >= 0 and key == "reported":
            consolidated_stats[key] = reported_override_value
        elif len(consolidated_times[key]) > 0 and key != "sent":
            consolidated_stats[key] = generate_time_difference_stats(
                consolidated_times[key]
            )
        elif len(consolidated_times[key]) > 0 and key == "sent":
            consolidated_stats[key] = {"count": len(consolidated_times[key])}
        else:
            consolidated_stats[key] = {"count": 0}

    if reported_override_value >= 0:
        consolidated_stats["reported"] = {"count": reported_override_value}

    return consolidated_stats


def count_timeline_moments(moments):
    """Count Timeline Moments."""
    phishing_result = {
        "sent": 0,
        "opened": 0,
        "clicked": 0,
        "submitted": 0,
        "reported": 0,
    }
    for moment in moments:
        if moment["message"] == "Email Sent":
            phishing_result["sent"] += 1
        if moment["message"] == "Email Opened":
            phishing_result["opened"] += 1
        if moment["message"] == "Clicked Link":
            phishing_result["clicked"] += 1
        if moment["message"] == "Submitted Data":
            phishing_result["submitted"] += 1
        if moment["message"] == "Email Reported":
            phishing_result["reported"] += 1
    return phishing_result


def update_phish_results(subscription):
    """Update Phish Results."""
    if not subscription.get("cycles"):
        return
    for cycle in subscription["cycles"]:
        if "phish_results_dirty" not in cycle or cycle.get("phish_results_dirty"):
            generate_cycle_phish_results(subscription, cycle)


def generate_cycle_phish_results(subscription, cycle):
    """Generate Cycle Phish Results."""
    cycle_phish_results = {
        "sent": 0,
        "opened": 0,
        "clicked": 0,
        "submitted": 0,
        "reported": 0,
    }
    for campaign in subscription["campaigns"]:
        if campaign["campaign_id"] in cycle["campaigns_in_cycle"]:
            # If campaign timeline is dirty, recalculate the phish results
            if "phish_results_dirty" not in campaign or campaign.get(
                "phish_results_dirty"
            ):

                unique_moments = get_unique_moments(campaign["timeline"])
                phishing_results = count_timeline_moments(unique_moments)

                # Update database with new phish results
                campaign_service.update(
                    campaign["campaign_uuid"],
                    {"phish_results": phishing_results, "phish_results_dirty": False},
                )
                campaign["phish_results"] = phishing_results

            # append campaign results to cycle results
            for key in campaign["phish_results"]:
                cycle_phish_results[key] += campaign["phish_results"][key]

    cycle["phish_result"] = cycle_phish_results

    # update the cycle phish results
    subscription_service.update_nested(
        uuid=subscription["subscription_uuid"],
        field="cycles.$.phish_results",
        data=cycle_phish_results,
        params={"cycles.cycle_uuid": cycle["cycle_uuid"]},
    )

    # Mark cycle data as clean
    subscription_service.update_nested(
        uuid=subscription["subscription_uuid"],
        field="cycles.$.phish_results_dirty",
        data=False,
        params={"cycles.cycle_uuid": cycle["cycle_uuid"]},
    )


def generate_region_stats(subscription_list, cycle_date=None):
    """
    Generate statistics for multiple subscriptions.

    Can provide cycle_date to specify a cycle range to use. Given a list of subscriptions, get the phishing results from the cycle value and summarize.
    """
    region_stats = {}
    campaign_count = 0
    cycle_count = 0
    for subscription in subscription_list:
        target_cycles = []
        if cycle_date:
            cycle_to_add = get_closest_cycle_within_day_range(subscription, cycle_date)
            if cycle_to_add:
                target_cycles.append(cycle_to_add)
            else:
                continue
        else:
            target_cycles = subscription["cycles"]
        for target_cycle in target_cycles:
            cycle_count += 1
            campaign_count += len(target_cycle["campaigns_in_cycle"])
            if target_cycle["phish_results_dirty"]:
                generate_cycle_phish_results(subscription, target_cycle)
            if not region_stats:
                region_stats = target_cycle["phish_results"].copy()
            else:
                for key in target_cycle["phish_results"]:
                    region_stats[key] += target_cycle["phish_results"][key]

    ratios = calc_ratios(region_stats)
    ret_val = {
        "consolidated_values": region_stats,
        "subscription_count": len(subscription_list),
        "campaign_count": campaign_count,
        "cycle_count": cycle_count,
        "clicked_ratio": ratios["clicked_ratio"],
        "opened_ratio": ratios["opened_ratio"],
        "submitted_ratio": ratios["submitted_ratio"],
        "reported_ratio": ratios["reported_ratio"],
    }
    return ret_val


def get_related_subscription_stats(subscription, start_date=None):
    """Get base stats for all related subscriptions (national, sector, industry, and customer)."""
    # Get the customer associated with the subscription
    _customer = customer_service.get(subscription["customer_uuid"])

    # Get a list of all customers with the same sector so sector/industry averages can be calculated
    parameters = {"sector": _customer["sector"]}
    customer_list_by_sector = customer_service.get_list(parameters=parameters)

    sector_customer_uuids = []
    industry_customer_uuids = []
    # sector_customer_uuids = customer_list_by_sector
    # industry_customer_uuids = list(filter(lambda x: x["industry"] ==_customer["industry"], customer_list_by_sector))
    for cust in customer_list_by_sector:
        sector_customer_uuids.append(cust["customer_uuid"])
        if cust["industry"] == _customer["industry"]:
            industry_customer_uuids.append(cust["customer_uuid"])

    parameters = {
        "active": True,
    }
    subscription_list = subscription_service.get_list(parameters=parameters)

    sector_subscriptions = []
    industry_subscriptions = []
    customer_subscriptions = []

    sector_subscriptions = list(
        filter(lambda x: x["customer_uuid"] in sector_customer_uuids, subscription_list)
    )
    industry_subscriptions = list(
        filter(
            lambda x: x["customer_uuid"] in industry_customer_uuids, subscription_list
        )
    )
    customer_subscriptions = list(
        filter(
            lambda x: x["customer_uuid"] == _customer["customer_uuid"],
            subscription_list,
        )
    )

    # Generate region stats, use all cycles. Get cycle specific query for customer data
    national_stats = generate_region_stats(subscription_list)
    sector_stats = generate_region_stats(sector_subscriptions)
    industry_stats = generate_region_stats(industry_subscriptions)
    customer_stats = generate_region_stats(customer_subscriptions)

    return {
        "national": national_stats,
        "sector": sector_stats,
        "industry": industry_stats,
        "customer": customer_stats,
    }


def get_gov_group_stats():
    """Get base stats for all related subscriptions (national, sector, industry, and customer)."""
    customers = customer_service.get_list()

    fed_customer_uuids = []
    state_customer_uuids = []
    local_customer_uuids = []
    tribal_customer_uuids = []
    private_customer_uuids = []

    for cust in customers:
        if cust["customer_type"] == "FED":
            fed_customer_uuids.append(cust["customer_uuid"])
        if cust["customer_type"] == "State":
            state_customer_uuids.append(cust["customer_uuid"])
        if cust["customer_type"] == "Local":
            local_customer_uuids.append(cust["customer_uuid"])
        if cust["customer_type"] == "Tribal":
            tribal_customer_uuids.append(cust["customer_uuid"])
        if cust["customer_type"] == "Private":
            private_customer_uuids.append(cust["customer_uuid"])

    subscription_list = subscription_service.get_list()

    fed_subscriptions = []
    state_subscriptions = []
    local_subscriptions = []
    tribal_subscriptions = []
    private_subscriptions = []

    fed_subscriptions = list(
        filter(lambda x: x["customer_uuid"] in fed_customer_uuids, subscription_list)
    )
    state_subscriptions = list(
        filter(lambda x: x["customer_uuid"] in state_customer_uuids, subscription_list)
    )
    local_subscriptions = list(
        filter(lambda x: x["customer_uuid"] in local_customer_uuids, subscription_list)
    )
    tribal_subscriptions = list(
        filter(lambda x: x["customer_uuid"] in tribal_customer_uuids, subscription_list)
    )
    private_subscriptions = list(
        filter(
            lambda x: x["customer_uuid"] in private_customer_uuids, subscription_list
        )
    )

    # Generate region stats, use all cycles. Get cycle specific query for customer data
    fed_stats = generate_region_stats(fed_subscriptions)
    state_stats = generate_region_stats(state_subscriptions)
    local_stats = generate_region_stats(local_subscriptions)
    tribal_stats = generate_region_stats(tribal_subscriptions)
    private_stats = generate_region_stats(private_subscriptions)

    return {
        "fed_stats": fed_stats,
        "state_stats": state_stats,
        "local_stats": local_stats,
        "tribal_stats": tribal_stats,
        "private_stats": private_stats,
    }


def get_cycles_breakdown(cycles):
    """Get a breakdown of all cycles for a given subscription."""
    cycle_stats = []
    for cycle in cycles:
        cycle_stats.append(
            {
                "ratios": calc_ratios(cycle["phish_results"]),
                "start_date": cycle["start_date"],
                "end_date": cycle["end_date"],
            }
        )
    return cycle_stats


def get_statistic_from_group(
    subscription_stats, deception_level, category, stat, zeroIfNone=False
):
    """
    Get a specific stat if it exists off of the subscription stats consolidation.

    Stats : Average, Count, Maximum, Median, Minimum
    """
    try:
        return subscription_stats[deception_level][category][stat]
    except Exception:
        if zeroIfNone:
            return 0
        return None


def get_statistic_from_region_group(region_stats, group, stat):
    """Get a specific stat if it exists off of the region stats consolidation."""
    if stat in ("sent", "opened", "clicked", "submitted", "reported"):
        try:
            return region_stats[group]["consolidated_values"][stat]
        except Exception:
            logging.info("Get stats from group failure")
    try:
        return region_stats[group][stat]
    except Exception:
        return None


def ratio_to_percent(ratio, round_val=2):
    """Convert ratio to percent."""
    if ratio:
        return "{:.{prec}f}".format(ratio * 100, prec=round_val)
    else:
        return "N/A"


def ratio_to_percent_zero_default(ratio, round_val=2):
    """Convert Ratio to Percent."""
    if ratio:
        return "{:.{prec}f}".format(ratio * 100, prec=round_val)
    else:
        return 0


def format_timedelta(timedelta):
    """Format Timedelta."""
    ret_val = ""
    plural = ""
    if timedelta:
        secondsLeftAfterHours = timedelta.seconds
        if timedelta.days:
            plural = "s" if timedelta.days != 1 else ""
            ret_val += f"{timedelta.days} day{plural}, "
            plural = ""
        if timedelta.seconds / 3600 >= 1:
            hours = int(math.floor(timedelta.seconds / 3600))
            plural = "s" if hours > 1 else ""
            ret_val += f"{hours} hour{plural}, "
            secondsLeftAfterHours = timedelta.seconds - (hours * 3600)
            plural = ""
        if secondsLeftAfterHours != 0:
            plural = "s" if timedelta.seconds >= 120 else ""
            ret_val += f"{int(secondsLeftAfterHours / 60)} minute{plural}, "
    return ret_val.rstrip(" ,")


def get_reports_to_click(subscription_stats):
    """Get reports to click ratio."""
    try:
        return (
            subscription_stats["stats_all"]["reported"]["count"]
            / subscription_stats["stats_all"]["clicked"]["count"]
        )
    except Exception:
        return None


def get_most_successful_campaigns(subscription_stats, category):
    """
    Get a list of the most succesful campaigns by a given category (submitted, opened, clicked, reported).

    Returns a list of the most succesful campagins. Will typically only return one but a
    list is used in case of a tie in the provided category values.
    """
    category_ratio = f"{category}_ratio"
    most_succesful_campaigns = []
    for campaign in subscription_stats["campaign_results"]:
        if not most_succesful_campaigns:
            if campaign["ratios"][category_ratio]:
                most_succesful_campaigns.append(campaign)
        else:
            for current_campaign in most_succesful_campaigns:
                if campaign["ratios"][category_ratio]:
                    if (
                        campaign["ratios"][category_ratio]
                        > current_campaign["ratios"][category_ratio]
                    ):
                        most_succesful_campaigns = []
                        most_succesful_campaigns.append(campaign)
    return most_succesful_campaigns


def campaign_templates_to_string(most_succesful_campaigns):
    """Given a list of campaigns, create a display string using there names."""
    ret_string = ""
    for campaign in most_succesful_campaigns:
        ret_string += (
            f"Level {campaign['deception_level']} \"{campaign['template_name']}\""
        )
    return ret_string


def get_template_details(campaign_results):
    """Given a list of campaigns, retrieve the template data for each one."""
    template_list = template_service.get_list()
    total_sent = 0
    for camp in campaign_results:
        try:
            total_sent += camp["campaign_stats"]["sent"]["count"]
        except Exception as e:
            logging.exception(e)

    percent_of_camps = 0
    for camp in campaign_results:
        try:
            percent_of_camps = ratio_to_percent(
                camp["campaign_stats"]["sent"]["count"] / total_sent
            )
            camp["campaign_stats"]["percent_of_campaigns"] = percent_of_camps
        except Exception:
            camp["campaign_stats"]["percent_of_campaigns"] = 0

    # Possible large performance hit here. Break out repository to use built in mongo $in functionallity to fix
    for template in template_list:
        for campaign in campaign_results:
            if campaign["template_uuid"] == template["template_uuid"]:
                campaign["template_details"] = {}
                for key in template:
                    campaign["template_details"][key] = template[key]


def get_stats_low_med_high_by_level(subscription_stats):
    """Get stats by level."""
    data = []
    v = get_statistic_from_group(
        subscription_stats, "stats_low_deception", "sent", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_mid_deception", "sent", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_high_deception", "sent", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_low_deception", "opened", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_mid_deception", "opened", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_high_deception", "opened", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_low_deception", "clicked", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_mid_deception", "clicked", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_high_deception", "clicked", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_low_deception", "submitted", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_mid_deception", "submitted", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_high_deception", "submitted", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_low_deception", "reported", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_mid_deception", "reported", "count"
    )
    data.append(_get_v_else(v))
    v = get_statistic_from_group(
        subscription_stats, "stats_high_deception", "reported", "count"
    )
    data.append(_get_v_else(v))
    return data


def _get_v_else(v):
    value = 0 if v is None else v
    return value


def get_relevant_recommendations(subscription_stats):
    """Get recommendations."""
    recommendations_list = recommendation_service.get_list()
    if not recommendations_list:
        return {}

    template_performance = [
        (i.get("template_uuid"), i.get("ratios"), i.get("template_details"))
        for i in subscription_stats.get("campaign_results")
    ]
    if not template_performance:
        return {}

    # Sort the top five performing templates from high to low open ratio
    sorted_templates = sorted(template_performance, key=lambda x: x[0], reverse=True)[
        :5
    ]

    recommendations_uuid = get_recomendations_uuid(
        recommendations_list, sorted_templates
    )

    sorted_recommendations_uuid = sorted(
        recommendations_uuid, key=lambda x: x[1], reverse=True
    )
    return sorted_recommendations_uuid


def get_recomendations_uuid(recommendations_list, sorted_templates):
    """Get recommendation uuids."""
    recommendations_set = set(recommendations_list[0])
    try:
        templates_set = set([template[2] for template in sorted_templates][0])
    except Exception:
        return {}
    recommendations_uuid = {}
    for matching_key in recommendations_set.intersection(templates_set):
        for index, recommendation in enumerate(recommendations_list):
            for sorted_template in sorted_templates:
                if recommendation.get(matching_key) == sorted_template[2].get(
                    matching_key
                ):
                    tmp_uuid = str(recommendation.get("recommendations_uuid"))
                    if tmp_uuid in recommendations_uuid:
                        recommendations_uuid[tmp_uuid] += 1
                    else:
                        recommendations_uuid[tmp_uuid] = 1

    return recommendations_uuid


def deception_stats_to_graph_format(stats):
    """Convert deception stats to graph format."""
    levels = []
    if stats["stats_high_deception"]:
        levels.append(
            detail_deception_to_simple(stats["stats_high_deception"], "high", 3)
        )
    if stats["stats_mid_deception"]:
        levels.append(
            detail_deception_to_simple(stats["stats_mid_deception"], "moderate", 2)
        )
    if stats["stats_low_deception"]:
        levels.append(
            detail_deception_to_simple(stats["stats_low_deception"], "low", 1)
        )
    return levels


def detail_deception_to_simple(decep_stats, level_name, level_num):
    """Convert deception to simple detail."""
    return {
        "level": level_name,
        "clicked": decep_stats["clicked"]["count"],
        "level_number": level_num,
        "opened": decep_stats["opened"]["count"],
        "sent": decep_stats["sent"]["count"],
    }


def cycle_stats_to_percentage_trend_graph_data(cycle_stats):
    """Convert stats to percentage trend."""
    clicked_series = []
    submitted_series = []
    reported_series = []

    for cycle in cycle_stats:
        clicked_series.insert(
            0,
            {
                # "name": f"{cycle['start_date'].year} - {cycle['start_date'].month}",
                "name": cycle["start_date"],
                "value": cycle["cycle_results"]["stats_all"]["clicked"]["count"],
            },
        )
        submitted_series.insert(
            0,
            {
                # "name": f"{cycle['start_date'].year} - {cycle['start_date'].month}",
                "name": cycle["start_date"],
                "value": cycle["cycle_results"]["stats_all"]["submitted"]["count"],
            },
        )
        reported_series.insert(
            0,
            {
                # "name": f"{cycle['start_date'].year} - {cycle['start_date'].month}",
                "name": cycle["start_date"],
                "value": cycle["cycle_results"]["stats_all"]["reported"]["count"],
            },
        )

    ret_val = [
        {"name": "Clicked", "series": clicked_series},
        {"name": "Submitted", "series": submitted_series},
        {"name": "Reported", "series": reported_series},
    ]
    return ret_val


def cycle_stats_to_click_rate_vs_report_rate(cycle_stats):
    """Convert to click rate vs report rate."""
    low_click_rate = []
    low_report_rate = []
    medium_click_rate = []
    medium_report_rate = []
    high_click_rate = []
    high_report_rate = []

    for cycle in cycle_stats:
        low_click_rate.insert(
            0,
            {
                # "name": f"{cycle['start_date'].year} - {cycle['start_date'].month}",
                "name": cycle["start_date"],
                "value": cycle["cycle_results"]["stats_low_deception"]["clicked"][
                    "count"
                ],
            },
        )
        low_report_rate.insert(
            0,
            {
                # "name": f"{cycle['start_date'].year} - {cycle['start_date'].month}",
                "name": cycle["start_date"],
                "value": cycle["cycle_results"]["stats_low_deception"]["reported"][
                    "count"
                ],
            },
        )
        medium_click_rate.insert(
            0,
            {
                # "name": f"{cycle['start_date'].year} - {cycle['start_date'].month}",
                "name": cycle["start_date"],
                "value": cycle["cycle_results"]["stats_mid_deception"]["clicked"][
                    "count"
                ],
            },
        )
        medium_report_rate.insert(
            0,
            {
                # "name": f"{cycle['start_date'].year} - {cycle['start_date'].month}",
                "name": cycle["start_date"],
                "value": cycle["cycle_results"]["stats_mid_deception"]["reported"][
                    "count"
                ],
            },
        )
        high_click_rate.insert(
            0,
            {
                # "name": f"{cycle['start_date'].year} - {cycle['start_date'].month}",
                "name": cycle["start_date"],
                "value": cycle["cycle_results"]["stats_high_deception"]["clicked"][
                    "count"
                ],
            },
        )
        high_report_rate.insert(
            0,
            {
                # "name": f"{cycle['start_date'].year} - {cycle['start_date'].month}",
                "name": cycle["start_date"],
                "value": cycle["cycle_results"]["stats_high_deception"]["reported"][
                    "count"
                ],
            },
        )

    ret_val = [
        {"name": "L-CR", "series": low_click_rate},
        {"name": "L-RR", "series": low_report_rate},
        {"name": "M-CR", "series": medium_click_rate},
        {"name": "M-RR", "series": medium_report_rate},
        {"name": "H-CR", "series": high_click_rate},
        {"name": "H-RR", "series": high_report_rate},
    ]
    return ret_val


def determine_trend(cycle_stats):
    """Determine Trend."""
    trend = "OneCycle"
    previous_cycle = None
    for cycle in cycle_stats:
        if not previous_cycle:
            previous_cycle = cycle
        else:
            if (
                previous_cycle["cycle_results"]["stats_all"]["reported"]["count"]
                > cycle["cycle_results"]["stats_all"]["reported"]["count"]
            ):
                trend = "degrading"
            else:
                trend = "improving"
    return trend


def get_yearly_start_dates(subscription, target_date):
    """Get yearly start dates."""
    # target_cycle = get_cycle_by_date_in_range(subscription,target_date)
    # defaulting to None since this was commented out.
    target_cycle = None
    start_date = end_date = ""
    for cycle in subscription["cycles"]:
        if cycle["start_date"] == target_date:
            target_cycle = cycle
    if target_cycle:
        end_date = target_cycle["end_date"]
        earliest_date = end_date - timedelta(days=365.25)
        cycles_in_range = []
        for cycle in subscription["cycles"]:
            if cycle["end_date"] > earliest_date and cycle["start_date"] < end_date:
                cycles_in_range.append(cycle)
        start_date = end_date
        for cycle in cycles_in_range:
            if cycle["start_date"] < start_date:
                start_date = cycle["start_date"]

    return (start_date, end_date)
