"""Statistic Utils."""
# Standard Python Libraries
from datetime import timedelta
import statistics

# cisagov Libraries
from api.services import CampaignService, CustomerService, SubscriptionService
from api.utils.generic import batch, format_timedelta, parse_time

customer_service = CustomerService()
subscription_service = SubscriptionService()
campaign_service = CampaignService()


def get_cycle_campaigns(cycle_uuid, campaigns):
    """Get campaigns associated with a cycle."""
    return list(filter(lambda x: x["cycle_uuid"] == cycle_uuid, campaigns))


def get_subscription_cycle(subscription, cycle_uuid):
    """Get cycle from a subscription."""
    return next(filter(lambda x: x["cycle_uuid"] == cycle_uuid, subscription["cycles"]))


def split_override_reports(override_total_reported, campaigns, total_targets):
    """Split reports accross campaigns when override_total_reported is provided."""
    if total_targets < override_total_reported:
        override_total_reported = total_targets
    batches = batch(list(range(override_total_reported)), len(campaigns))
    if len(batches) > 0:
        for i, val in enumerate(batches):
            campaigns[i]["override_total_reported"] = len(val)
    else:
        for c in campaigns:
            c["override_total_reported"] = 0


def get_related_customer_stats(customer):
    """Get general statistics from related customers."""
    customer_list_by_sector = customer_service.get_list(
        parameters={"sector": customer["sector"]}
    )

    sector_customer_uuids = []
    industry_customer_uuids = []
    for c in customer_list_by_sector:
        sector_customer_uuids.append(c["customer_uuid"])
        if c["industry"] == customer["industry"]:
            industry_customer_uuids.append(c["customer_uuid"])

    subscriptions = subscription_service.get_list(parameters={"active": True})
    sector_subscriptions = list(
        filter(lambda x: x["customer_uuid"] in sector_customer_uuids, subscriptions)
    )
    industry_subscriptions = list(
        filter(lambda x: x["customer_uuid"] in industry_customer_uuids, subscriptions)
    )
    customer_subscriptions = list(
        filter(lambda x: x["customer_uuid"] == customer["customer_uuid"], subscriptions)
    )

    return {
        "national": get_simple_stats_from_subscriptions(subscriptions),
        "sector": get_simple_stats_from_subscriptions(sector_subscriptions),
        "industry": get_simple_stats_from_subscriptions(industry_subscriptions),
        "customer": get_simple_stats_from_subscriptions(customer_subscriptions),
    }


def get_simple_stats_from_subscriptions(subscriptions):
    """Consolidate phish_results accross multiple subscriptions."""
    region_stats = {}
    cycle_count = 0
    campaign_count = 0
    for subscription in subscriptions:
        for cycle in subscription["cycles"]:
            cycle_count += 1
            campaign_count += len(cycle["campaigns_in_cycle"])
            if cycle["phish_results_dirty"]:
                generate_cycle_phish_results(subscription, cycle)
            if not region_stats:
                region_stats = cycle["phish_results"].copy()
            else:
                for key in cycle["phish_results"]:
                    region_stats[key] += cycle["phish_results"][key]

    ret_val = {
        "consolidated_values": region_stats,
        "subscription_count": len(subscriptions),
        "campaign_count": campaign_count,
        "cycle_count": cycle_count,
    }
    ret_val.update(get_simple_stats(region_stats))

    return ret_val


def get_simple_stats_from_subscription(subscription):
    """Consolidate phish results accross cycles in a subscription."""
    stats = []
    for cycle in subscription["cycles"]:
        if cycle["phish_results_dirty"]:
            generate_cycle_phish_results(subscription, cycle)
        stat = {
            "ratios": get_simple_stats(cycle.get("phish_results", {})),
            "start_date": cycle["start_date"],
            "end_date": cycle["end_date"],
        }
        stats.append(stat)
    return stats


def get_simple_stats(data):
    """Get simple stats from phish_results."""
    stats = {
        "clicked": {"count": data.get("clicked", 0)},
        "opened": {"count": data.get("opened", 0)},
        "sent": {"count": data.get("sent", 0)},
        "reported": {"count": data.get("reported", 0)},
    }

    return get_ratios(stats)


def process_overall_stats(campaign_stats):
    """Sum up stats accross high, low, moderate from campaign statistics."""
    high_campaign_stats = list(
        filter(lambda x: x["deception_level"] == 3, campaign_stats)
    )
    high_stats = get_stats(merge_stats(high_campaign_stats))
    high_stats["level_number"] = 3
    high_stats["level"] = "high"

    mid_campaign_stats = list(
        filter(lambda x: x["deception_level"] == 2, campaign_stats)
    )
    mid_stats = get_stats(merge_stats(mid_campaign_stats))
    mid_stats["level_number"] = 2
    mid_stats["level"] = "moderate"

    low_campaign_stats = list(
        filter(lambda x: x["deception_level"] == 1, campaign_stats)
    )
    low_stats = get_stats(merge_stats(low_campaign_stats))
    low_stats["level_number"] = 1
    low_stats["level"] = "low"

    stats_all = get_stats(merge_stats((high_stats, mid_stats, low_stats)))

    clicks_over_time = get_clicked_time_period_breakdown(campaign_stats)

    return_val = {
        "stats_all": stats_all,
        "stats_high_deception": high_stats,
        "stats_mid_deception": mid_stats,
        "stats_low_deception": low_stats,
        "clicks_over_time": clicks_over_time,
    }
    return_val["indicator_breakdown"] = return_val["stats_all"]["indicator_breakdown"]
    return_val["indicator_ranking"] = rank_indicators(return_val)

    return return_val


def clean_stats(stats: dict):
    """Clean up statistics."""
    stat_keys = [
        "stats_all",
        "stats_high_deception",
        "stats_mid_deception",
        "stats_low_deception",
    ]

    event_keys = ["opened", "reported", "sent", "clicked"]
    for stat_key in stat_keys:
        stats[stat_key].pop("indicator_breakdown", None)
        for event_key in event_keys:
            stats[stat_key][event_key].pop("diffs", None)


def get_ratio(numerator, denominator):
    """Get ratio from numerator and denominator."""
    return (
        0 if not denominator else round(float(numerator or 0) / float(denominator), 2)
    )


def ratio_to_percent(ratio, round_val=0):
    """Convert a ratio to a percentage."""
    if ratio:
        return "{:.{prec}f}".format(ratio * 100, prec=round_val)
    else:
        return 0


def merge_stats(stats):
    """Merge stats."""
    combined_stats = {
        "sent": {"count": 0},
        "opened": {"count": 0, "diffs": []},
        "clicked": {"count": 0, "diffs": []},
        "reported": {"count": 0, "diffs": []},
        "indicator_breakdown": {},
    }
    for s in stats:
        combined_stats["sent"]["count"] += s["sent"]["count"]

        combined_stats["opened"]["count"] += s["opened"]["count"]
        combined_stats["opened"]["diffs"].extend(s["opened"]["diffs"])

        combined_stats["clicked"]["count"] += s["clicked"]["count"]
        combined_stats["clicked"]["diffs"].extend(s["clicked"]["diffs"])

        combined_stats["reported"]["count"] += s["reported"]["count"]
        combined_stats["reported"]["diffs"].extend(s["reported"]["diffs"])

        if s.get("indicator_breakdown"):
            combined_stats["indicator_breakdown"] = merge_template_clicked_indicators(
                combined_stats["indicator_breakdown"], s["indicator_breakdown"]
            )

    return combined_stats


def merge_template_clicked_indicators(indicators_1, indicators_2):
    """Merge template clicked indicators."""
    key_vals = {
        "grammar": {"0": 0, "1": 0, "2": 0},
        "link_domain": {"0": 0, "1": 0},
        "logo_graphics": {"0": 0, "1": 0},
        "external": {"0": 0, "1": 0},
        "internal": {"0": 0, "1": 0, "2": 0},
        "authoritative": {"0": 0, "1": 0, "2": 0},
        "organization": {"0": 0, "1": 0},
        "public_news": {"0": 0, "1": 0},
        "curiosity": {"0": 0, "1": 0},
        "duty_obligation": {"0": 0, "1": 0},
        "fear": {"0": 0, "1": 0},
        "greed": {"0": 0, "1": 0},
    }

    if not indicators_1:
        indicators_1 = key_vals
    if not indicators_2:
        indicators_2 = key_vals

    for identifier in key_vals:
        for val in key_vals[identifier].keys():
            indicators_1[identifier][val] += indicators_2[identifier][val]

    return indicators_1


def get_stats(stats):
    """Get stats for events."""
    stats["opened"] = get_time_stats_for_event(stats["opened"])
    stats["clicked"] = get_time_stats_for_event(stats["clicked"])
    stats["reported"] = get_time_stats_for_event(stats["reported"])
    stats["ratios"] = get_ratios(stats)
    return stats


def get_time_stats_for_event(stats):
    """Get time stats for an event."""
    diffs = stats["diffs"]
    count = stats["count"]
    return_val = {"count": count, "diffs": diffs}
    if len(diffs) > 0:
        return_val.update(
            {
                "average": sum(diffs, timedelta()) / count,
                "minimum": min(diffs),
                "median": statistics.median(diffs),
                "maximum": max(diffs),
            }
        )
    else:
        return_val.update(
            {
                "average": timedelta(),
                "minimum": timedelta(),
                "median": timedelta(),
                "maximum": timedelta(),
            }
        )
    return return_val


def get_ratios(stats):
    """Get clicked, opened, and reported ratios."""
    if stats["sent"]["count"] > 0:
        return {
            "clicked_ratio": stats["clicked"]["count"] / stats["sent"]["count"],
            "opened_ratio": stats["opened"]["count"] / stats["sent"]["count"],
            "reported_ratio": stats["reported"]["count"] / stats["sent"]["count"],
        }
    return {
        "clicked_ratio": 0,
        "opened_ratio": 0,
        "reported_ratio": 0,
    }


def get_template_clicked_indicators(campaign_stats):
    """Get template clicked indicators."""
    key_vals = {
        "grammar": {"0": 0, "1": 0, "2": 0},
        "link_domain": {"0": 0, "1": 0},
        "logo_graphics": {"0": 0, "1": 0},
        "external": {"0": 0, "1": 0},
        "internal": {"0": 0, "1": 0, "2": 0},
        "authoritative": {"0": 0, "1": 0, "2": 0},
        "organization": {"0": 0, "1": 0},
        "public_news": {"0": 0, "1": 0},
        "curiosity": {"0": 0, "1": 0},
        "duty_obligation": {"0": 0, "1": 0},
        "fear": {"0": 0, "1": 0},
        "greed": {"0": 0, "1": 0},
    }

    if campaign_stats["clicked"]["count"] > 0:
        appearance = campaign_stats["template_details"]["appearance"]
        behavior = campaign_stats["template_details"]["behavior"]
        relevancy = campaign_stats["template_details"]["relevancy"]
        sender = campaign_stats["template_details"]["sender"]
        all_identifiers = {**appearance, **behavior, **relevancy, **sender}
        for identifier in key_vals:
            for val in key_vals[identifier].keys():
                if all_identifiers[identifier] == int(val):
                    key_vals[identifier][val] += campaign_stats["clicked"]["count"]

    return key_vals


def campaign_templates_to_string(campaigns):
    """Convert templates to string."""
    ret_string = ""
    for campaign in campaigns:
        ret_string += (
            f"Level {campaign['deception_level']} \"{campaign['template']['name']}\""
        )
    return ret_string


def group_campaigns_by_deception_level(campaigns):
    """Split campaigns into groups based on deception level."""
    templates_by_group = [[], [], []]
    for campaign in campaigns:
        if campaign["deception_level"] == 1:
            templates_by_group[0].append(campaign)
        elif campaign["deception_level"] == 2:
            templates_by_group[1].append(campaign)
        elif campaign["deception_level"] == 3:
            templates_by_group[2].append(campaign)
    return templates_by_group


def click_time_vs_report_time(campaigns):
    """Get difference between first report and first click."""
    return_val = []
    for campaign in campaigns:
        first_click = campaign["clicked"]["minimum"]
        first_report = campaign["reported"]["minimum"]
        difference = "N/A"
        if first_click > timedelta() and first_report > timedelta():
            difference = format_timedelta(first_click - first_report)
        return_val.append(
            {
                "level": campaign["deception_level"],
                "time_to_first_click": format_timedelta(first_click),
                "time_to_first_report": format_timedelta(first_report),
                "difference": difference,
            }
        )
    return return_val


def get_most_successful_campaigns(campaigns, category):
    """
    Get a list of the most succesful campaigns by a given category (submitted, opened, clicked, reported).

    Returns a list of the most succesful campagins. Will typically only return one but a
    list is used in case of a tie in the provided category values.
    """
    category_ratio = f"{category}_ratio"
    most_succesful_campaigns = []
    for campaign in campaigns:
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


def rank_indicators(stats):
    """Rank which indicators performed the highest."""
    key_vals = {
        "grammar": {
            "name": "Apperance & Grammar",
            "0": "Poor",
            "1": "Decent",
            "2": "Proper",
        },
        "link_domain": {
            "name": "Link Domain",
            "0": "Fake",
            "1": "Spoofed / Hidden",
        },
        "logo_graphics": {
            "name": "Logo / Graphics",
            "0": "Fake / None",
            "1": "Sppofed / HTML",
        },
        "external": {"name": "Sender External", "0": "Fake / NA", "1": "Spoofed"},
        "internal": {
            "name": "Internal",
            "0": "Fake / NA",
            "1": "Unknown Spoofed",
            "2": "Known Spoofed",
        },
        "authoritative": {
            "name": "Authoritative",
            "0": "None",
            "1": "Corprate / Local",
            "2": "Federal / State",
        },
        "organization": {"name": "Relevancy Orginization", "0": "No", "1": "Yes"},
        "public_news": {"name": "Public News", "0": "No", "1": "Yes"},
        "curiosity": {"name": "Curiosity", "0": "Yes", "1": "No"},
        "duty_obligation": {"name": "Duty or Obligation", "0": "Yes", "1": "No"},
        "fear": {"name": "Fear", "0": "Yes", "1": "No"},
        "greed": {"name": "Greed", "0": "Yes", "1": "No"},
    }
    # Flatten out indicators
    flat_indicators = {}
    for indicator in stats["indicator_breakdown"]:
        for level in stats["indicator_breakdown"][indicator]:
            level_val = stats["indicator_breakdown"][indicator][level]
            flat_indicators[indicator + "-" + level] = level_val
    # Sort indicators
    sorted_flat_indicators = sorted(flat_indicators.items(), key=lambda kv: kv[1])
    # Get proper name and format output
    indicator_formatted = []
    rank = 0
    previous_val = None
    for indicator in sorted_flat_indicators:
        key_and_level = indicator[0].split("-")
        key = key_and_level[0]
        level = key_and_level[1]
        formated_val = indicator[1]
        formated_name = key_vals[key]["name"]
        formated_level = key_vals[key][level]
        if previous_val is None:
            previous_val = formated_val
        else:
            if previous_val != formated_val:
                rank += 1
            previous_val = formated_val
        percent = 0
        if stats["stats_all"]["clicked"]["count"] > 0:
            percent = formated_val / stats["stats_all"]["clicked"]["count"]
        indicator_formatted.insert(
            0,
            {
                "name": formated_name,
                "level": formated_level,
                "value": formated_val,
                "percent": percent,
                "rank": rank,
            },
        )
    return indicator_formatted


def process_campaign(campaign: dict, template=None, nonhuman=False):
    """Generate stats from a campagin."""
    campaign_timeline = campaign["timeline"]
    return_val = {
        "timeline": [],
        "sent": {"count": 0},
        "opened": {"count": 0, "diffs": []},
        "clicked": {"count": 0, "diffs": []},
        "reported": {"count": 0, "diffs": []},
        "deception_level": campaign["deception_level"],
    }
    if template:
        return_val["template"] = template
        return_val["template_details"] = {
            "appearance": template["appearance"],
            "behavior": template["behavior"],
            "relevancy": template["relevancy"],
            "sender": template["sender"],
        }
        return_val["deception_score"] = template["deception_score"]
    grouped_timeline = group_campaign_timeline_by_email(campaign_timeline)
    override_total_reported = campaign.get("override_total_reported", -1)
    if override_total_reported > -1:
        return_val["reported"]["count"] = override_total_reported
    for timeline in grouped_timeline.values():
        if not nonhuman:
            timeline = clean_nonhuman_events(timeline)

        sent_event = get_event(timeline, "Email Sent", False)
        opened_event = get_event(timeline, "Email Opened", False)
        clicked_event = get_event(timeline, "Clicked Link", False)

        # If there was a clicked event, but no opened event, add one
        if clicked_event and not opened_event:
            opened_event = clicked_event.copy()
            opened_event["message"] = "Email Opened"

        # Append sent event
        return_val["timeline"].append(sent_event)
        return_val["sent"]["count"] += 1

        # Generate time differentials from sent to open, click, report
        if not override_total_reported > -1:
            reported_event = get_event(timeline, "Email Reported", False)
            if reported_event:
                reported_event["time_diff"] = (
                    reported_event["time"] - sent_event["time"]
                )
                return_val["timeline"].append(reported_event)
                return_val["reported"]["count"] += 1
                return_val["reported"]["diffs"].append(reported_event["time_diff"])

        if opened_event:
            opened_event["time_diff"] = opened_event["time"] - sent_event["time"]
            return_val["timeline"].append(opened_event)
            return_val["opened"]["count"] += 1
            return_val["opened"]["diffs"].append(opened_event["time_diff"])

        if clicked_event:
            clicked_event["time_diff"] = clicked_event["time"] - sent_event["time"]
            return_val["timeline"].append(clicked_event)
            return_val["clicked"]["count"] += 1
            return_val["clicked"]["diffs"].append(clicked_event["time_diff"])

    get_stats(return_val)
    if template:
        return_val["indicator_breakdown"] = get_template_clicked_indicators(return_val)
    return return_val


def get_event(timeline, event, many=True):
    """Get specified event/events from timeline."""
    events = list(filter(lambda x: x["message"] == event, timeline))
    if many:
        return events

    if events:
        return min(events, key=lambda x: x["time"])
    return None


def group_campaign_timeline_by_email(timeline):
    """Group timeline events by email."""
    grouped_timeline = {}
    for event in timeline:
        if event["message"] in [
            "Email Sent",
            "Email Opened",
            "Clicked Link",
            "Email Reported",
        ]:
            email = event["email"]
            event["time"] = parse_time(event["time"])
            if not grouped_timeline.get(email):
                grouped_timeline[email] = []
            grouped_timeline[email].append(event)
    return grouped_timeline


def clean_nonhuman_events(email_timeline: list):
    """Clean nonhuman events from timeline."""
    for event in email_timeline.copy():
        if is_nonhuman_event(event.get("asn_org", "UNKNOWN")):
            email_timeline.remove(event)
    return email_timeline


def is_nonhuman_event(asn_org):
    """Determine if nonhuman event."""
    if asn_org in ["GOOGLE", "AMAZON-02", "MICROSOFT-CORP-MSN-AS-BLOCK"]:
        return True
    return False


def update_phish_results(subscription):
    """Update Phish Results."""
    if not subscription.get("cycles"):
        return
    for cycle in subscription["cycles"]:
        if not cycle.get("phish_results_dirty"):
            generate_cycle_phish_results(subscription, cycle)


def generate_cycle_phish_results(subscription, cycle):
    """Generate Cycle Phish Results."""
    cycle_phish_results = {
        "sent": 0,
        "opened": 0,
        "clicked": 0,
        "reported": 0,
    }
    campaigns = list(
        filter(
            lambda x: x["cycle_uuid"] == cycle["cycle_uuid"], subscription["campaigns"]
        )
    )

    if cycle.get("override_total_reported", -1) > -1:
        split_override_reports(
            cycle["override_total_reported"], campaigns, cycle["total_targets"]
        )

    for campaign in campaigns:
        stats = process_campaign(campaign)
        phish_results = {
            "sent": stats["sent"]["count"],
            "opened": stats["opened"]["count"],
            "clicked": stats["clicked"]["count"],
            "reported": stats["reported"]["count"],
        }
        cycle_phish_results["sent"] += phish_results["sent"]
        cycle_phish_results["opened"] += phish_results["opened"]
        cycle_phish_results["clicked"] += phish_results["clicked"]
        cycle_phish_results["reported"] += phish_results["reported"]
        campaign_service.update(
            campaign["campaign_uuid"],
            {"phish_results": phish_results, "phish_results_dirty": False},
        )
        campaign["phish_results_dirty"] = False
        campaign["phish_results"] = phish_results

    cycle["phish_result"] = cycle_phish_results
    cycle["phish_results_dirty"] = False

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
        for moment in campaign["clicked"]["diffs"]:
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


def deception_stats_to_graph_format(stats):
    """Convert deception stats to graph format."""
    levels = []
    levels.append(detail_deception_to_simple(stats["stats_high_deception"], "high", 3))
    levels.append(
        detail_deception_to_simple(stats["stats_mid_deception"], "moderate", 2)
    )
    levels.append(detail_deception_to_simple(stats["stats_low_deception"], "low", 1))
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


def set_cycle_year_increments(cycles):
    """Set Cycle Quarters."""
    cycles = sorted(cycles, key=lambda cycle: cycle["start_date"])
    year = 0
    cycle_quarter = 1
    cycle_increment = 1
    for cycle in cycles:
        cycle["year"] = cycle["start_date"].year
        if cycle["year"] != year:
            year = cycle["year"]
            cycle_quarter = 1
        cycle["quarter"] = f"{year} - {cycle_quarter}"
        cycle["increment"] = cycle_increment
        cycle_quarter += 1
        cycle_increment += 1

    # for num, cycle in enumerate(cycles, 0):
    #     quarter = get_date_quarter(cycle["start_date"])
    #     cycle["quarter"] = f"{cycle['start_date'].year} - {quarter}"
    #     cycle["increment"] = num


def get_yearly_cycles(yearly_start, yearly_end, cycles):
    """Get cycles within a year."""
    # Determine the cycels that lie within a yearly timespan
    # Three checks needed,
    # One: the first cycle possible
    # Two: any cycle directly within the yearly timespan
    # Three: the last cycle possible on that lies within the yearly timespan

    # Cycles: [-----][-----][-----][-----][-----]
    # Yearly:  [--------------------------]
    #            1      2       2     2      3
    yearly_cycles = []
    for cycle in cycles:
        cycle_start = cycle["start_date"]
        cycle_end = cycle["end_date"]
        if cycle_start <= yearly_start and cycle_end >= yearly_start:
            yearly_cycles.append(cycle)
        if cycle_start >= yearly_start and cycle_end <= yearly_end:
            yearly_cycles.append(cycle)
        if cycle_start <= yearly_end and cycle_end >= yearly_end:
            yearly_cycles.append(cycle)
    return yearly_cycles


def cycle_stats_to_percentage_trend_graph_data(cycles):
    """Convert stats to percentage trend."""
    clicked_series = []
    reported_series = []

    for cycle in cycles:
        clicked_series.insert(
            0,
            {
                "name": cycle["start_date"],
                "value": cycle["cycle_stats"]["stats_all"]["clicked"]["count"],
            },
        )
        reported_series.insert(
            0,
            {
                "name": cycle["start_date"],
                "value": cycle["cycle_stats"]["stats_all"]["reported"]["count"],
            },
        )

    ret_val = [
        {"name": "Clicked", "series": clicked_series},
        {"name": "Reported", "series": reported_series},
    ]
    return ret_val


def cycle_stats_to_click_rate_vs_report_rate(cycles):
    """Convert to click rate vs report rate."""
    low_click_rate = []
    low_report_rate = []
    medium_click_rate = []
    medium_report_rate = []
    high_click_rate = []
    high_report_rate = []

    for cycle in cycles:
        low_click_rate.insert(
            0,
            {
                "name": cycle["start_date"],
                "value": cycle["cycle_stats"]["stats_low_deception"]["clicked"][
                    "count"
                ],
            },
        )
        low_report_rate.insert(
            0,
            {
                "name": cycle["start_date"],
                "value": cycle["cycle_stats"]["stats_low_deception"]["reported"][
                    "count"
                ],
            },
        )
        medium_click_rate.insert(
            0,
            {
                "name": cycle["start_date"],
                "value": cycle["cycle_stats"]["stats_mid_deception"]["clicked"][
                    "count"
                ],
            },
        )
        medium_report_rate.insert(
            0,
            {
                "name": cycle["start_date"],
                "value": cycle["cycle_stats"]["stats_mid_deception"]["reported"][
                    "count"
                ],
            },
        )
        high_click_rate.insert(
            0,
            {
                "name": cycle["start_date"],
                "value": cycle["cycle_stats"]["stats_high_deception"]["clicked"][
                    "count"
                ],
            },
        )
        high_report_rate.insert(
            0,
            {
                "name": cycle["start_date"],
                "value": cycle["cycle_stats"]["stats_high_deception"]["reported"][
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


def determine_trend(cycles):
    """Determine Trend."""
    trend = "OneCycle"
    previous_cycle = None
    for cycle in cycles:
        if not previous_cycle:
            previous_cycle = cycle
        else:
            if (
                previous_cycle["cycle_stats"]["stats_all"]["reported"]["count"]
                > cycle["cycle_stats"]["stats_all"]["reported"]["count"]
            ):
                trend = "degrading"
            else:
                trend = "improving"
    return trend
