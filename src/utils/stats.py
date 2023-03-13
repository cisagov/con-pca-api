"""Stat utils."""
# Standard Python Libraries
import copy
from datetime import datetime, timedelta
import statistics

# cisagov Libraries
from api.manager import (
    CycleManager,
    NonHumanManager,
    RecommendationManager,
    SendingProfileManager,
    SubscriptionManager,
    TargetManager,
    TemplateManager,
)
from api.schemas.stats_schema import CycleStatsSchema
from utils.templates import get_indicators

template_manager = TemplateManager()
customer_manager = TemplateManager()
cycle_manager = CycleManager()
nonhuman_manager = NonHumanManager()
recommendation_manager = RecommendationManager()
subscription_manager = SubscriptionManager()
target_manager = TargetManager()
sending_profile_manager = SendingProfileManager()


def process_ratios(stats: dict):
    """Get event to sent ratios."""
    for v in stats.values():
        sent = v["sent"]["count"]
        for event in ["opened", "clicked", "reported"]:
            v[event]["ratio"] = get_ratio(v[event]["count"], sent)


def get_cycle_stats(cycle, recalculate=False):
    """Get stats for cycle."""
    if cycle.get("dirty_stats", True) or recalculate:
        data = {
            "stats": generate_cycle_stats(cycle["_id"], nonhuman=False),
            "nonhuman_stats": generate_cycle_stats(cycle["_id"], nonhuman=True),
            "dirty_stats": False,
        }
        cycle.update(data)
        if cycle.get("_id"):
            cycle_manager.update(
                document_id=cycle["_id"],
                data=data,
            )


def generate_cycle_stats(cycle_id, nonhuman=False):
    """Get stats for cycle."""
    nonhuman_orgs = get_nonhuman_orgs()

    decep_level_stats = get_deception_level_stats(cycle_id, nonhuman, nonhuman_orgs)
    indicator_stats = get_indicator_stats(cycle_id, nonhuman, nonhuman_orgs)
    maxmind_stats = get_maxmind_stats(cycle_id, nonhuman, nonhuman_orgs)
    recommendation_stats = get_recommendation_stats(cycle_id, nonhuman, nonhuman_orgs)
    stats = get_stats(cycle_id, nonhuman, nonhuman_orgs)
    target_stats = get_target_stats(cycle_id, nonhuman, nonhuman_orgs)
    template_stats = get_template_stats(cycle_id, nonhuman, nonhuman_orgs)
    time_stats = get_time_stats(cycle_id, nonhuman, nonhuman_orgs)

    return CycleStatsSchema().dump(
        {
            "stats": stats,
            "template_stats": template_stats,
            "maxmind_stats": maxmind_stats,
            "indicator_stats": indicator_stats,
            "time_stats": time_stats,
            "recommendation_stats": recommendation_stats,
            "deception_level_stats": decep_level_stats,
            "target_stats": target_stats,
        }
    )


def get_deception_level_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get deception level stats."""
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$nin": []},
            }
        },
        {"$addFields": {"template_id": {"$toObjectId": "$template_id"}}},
        {
            "$lookup": {
                "from": "template",
                "localField": "template_id",
                "foreignField": "_id",
                "as": "template",
            }
        },
        {"$unwind": {"path": "$template"}},
        {
            "$addFields": {
                "time_to_event": {"$subtract": ["$timeline.time", "$sent_date"]}
            }
        },
        {
            "$group": {
                "_id": "$template.deception_score",
                "deception_level": {"$first": "$template.deception_score"},
                "sent_count": {
                    "$sum": {"$cond": [{"$ne": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "total_clicks": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "unique_clicks": {
                    "$addToSet": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "clicked"]},
                            {"$toString": "$_id"},
                            "$$REMOVE",
                        ]
                    }
                },
                "user_reports": {
                    "$sum": {
                        "$cond": [{"$eq": ["$timeline.message", "reported"]}, 1, 0]
                    }
                },
                "unique_user_clicks": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "clicked"]},
                            {"$toString": "$_id"},
                            "$$REMOVE",
                        ]
                    }
                },
                "one_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [1, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "three_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [3, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "five_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [5, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "fifteen_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [15, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "thirty_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [30, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "sixty_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [60, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "two_hours": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [2, 60, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "three_hours": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [3, 60, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "four_hours": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [4, 60, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "one_day": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [24, 60, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
            }
        },
        {
            "$project": {
                "deception_level": "$deception_level",
                "sent_count": "$sent_count",
                "total_clicks": "$total_clicks",
                "unique_clicks": "$unique_clicks",
                "unique_user_clicks": "$unique_user_clicks",
                "user_reports": "$user_reports",
                "click_percentage_over_time.one_minutes.count": "$one_minutes",
                "click_percentage_over_time.one_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {"$round": [{"$divide": ["$one_minutes", "$total_clicks"]}, 4]},
                    ]
                },
                "click_percentage_over_time.three_minutes.count": "$three_minutes",
                "click_percentage_over_time.three_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {
                            "$round": [
                                {"$divide": ["$three_minutes", "$total_clicks"]},
                                4,
                            ]
                        },
                    ]
                },
                "click_percentage_over_time.five_minutes.count": "$five_minutes",
                "click_percentage_over_time.five_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {
                            "$round": [
                                {"$divide": ["$five_minutes", "$total_clicks"]},
                                4,
                            ]
                        },
                    ]
                },
                "click_percentage_over_time.fifteen_minutes.count": "$fifteen_minutes",
                "click_percentage_over_time.fifteen_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {
                            "$round": [
                                {"$divide": ["$fifteen_minutes", "$total_clicks"]},
                                4,
                            ]
                        },
                    ]
                },
                "click_percentage_over_time.thirty_minutes.count": "$thirty_minutes",
                "click_percentage_over_time.thirty_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {
                            "$round": [
                                {"$divide": ["$thirty_minutes", "$total_clicks"]},
                                4,
                            ]
                        },
                    ]
                },
                "click_percentage_over_time.sixty_minutes.count": "$sixty_minutes",
                "click_percentage_over_time.sixty_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {
                            "$round": [
                                {"$divide": ["$sixty_minutes", "$total_clicks"]},
                                4,
                            ]
                        },
                    ]
                },
                "click_percentage_over_time.two_hours.count": "$two_hours",
                "click_percentage_over_time.two_hours.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {"$round": [{"$divide": ["$two_hours", "$total_clicks"]}, 4]},
                    ]
                },
                "click_percentage_over_time.three_hours.count": "$three_hours",
                "click_percentage_over_time.three_hours.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {"$round": [{"$divide": ["$three_hours", "$total_clicks"]}, 4]},
                    ]
                },
                "click_percentage_over_time.four_hours.count": "$four_hours",
                "click_percentage_over_time.four_hours.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {"$round": [{"$divide": ["$four_hours", "$total_clicks"]}, 4]},
                    ]
                },
                "click_percentage_over_time.one_day.count": "$one_day",
                "click_percentage_over_time.one_day.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {"$round": [{"$divide": ["$one_day", "$total_clicks"]}, 4]},
                    ]
                },
            }
        },
    ]
    deception_level_stats = target_manager.aggregate(pipeline)

    deception_level_stats = sorted(
        deception_level_stats, key=lambda d: d["deception_level"]
    )

    for deception_level in deception_level_stats:
        deception_level["unique_clicks"] = len(deception_level["unique_clicks"])
        deception_level["unique_user_clicks"] = calculate_unique_user_clicks(
            deception_level["unique_user_clicks"]
        )

    if len(deception_level_stats) == 3:
        composite_deception_level_stats = copy.deepcopy(deception_level_stats)
        composite_deception_level_stats[0]["deception_level"] = 11
        composite_deception_level_stats[1]["deception_level"] = 12
        composite_deception_level_stats[2]["deception_level"] = 13
    else:
        composite_deception_level_stats = None

    for deception_level in [1, 2, 3, 4, 5, 6]:
        index = next(
            (
                i
                for i, item in enumerate(deception_level_stats)
                if item["deception_level"] == deception_level
            ),
            None,
        )
        if index is None:
            empty_deception_level = {
                "click_percentage_over_time": {
                    "fifteen_minutes": {"count": 0, "ratio": 0.0},
                    "five_minutes": {"count": 0, "ratio": 0.0},
                    "four_hours": {"count": 0, "ratio": 0.0},
                    "one_day": {"count": 0, "ratio": 0.0},
                    "one_minutes": {"count": 0, "ratio": 0.0},
                    "sixty_minutes": {"count": 0, "ratio": 0.0},
                    "thirty_minutes": {"count": 0, "ratio": 0.0},
                    "three_hours": {"count": 0, "ratio": 0.0},
                    "three_minutes": {"count": 0, "ratio": 0.0},
                    "two_hours": {"count": 0, "ratio": 0.0},
                },
                "deception_level": deception_level,
                "sent_count": 0,
                "total_clicks": 0,
                "unique_clicks": 0,
                "unique_user_clicks": {
                    "four_five_clicks": 0,
                    "one_click": 0,
                    "six_ten_clicks": 0,
                    "ten_plus_clicks": 0,
                    "two_three_clicks": 0,
                },
                "user_reports": 0,
            }
            deception_level_stats.append(empty_deception_level)

    deception_level_stats = sorted(
        deception_level_stats, key=lambda d: d["deception_level"]
    )

    if composite_deception_level_stats:
        deception_level_stats.extend(composite_deception_level_stats)
    else:
        calculate_composite_deception_stats(deception_level_stats, [0, 1], 11)  # Low
        calculate_composite_deception_stats(
            deception_level_stats, [2, 3], 12
        )  # Moderate
        calculate_composite_deception_stats(deception_level_stats, [4, 5], 13)  # High

    all_deception_level_stats = get_all_deception_level_stats(
        cycle_id, nonhuman, nonhuman_orgs
    )

    if all_deception_level_stats:
        deception_level_stats.extend(all_deception_level_stats)
    else:
        calculate_composite_deception_stats(deception_level_stats, [6, 7, 8], 14)  # All

    return deception_level_stats


def get_all_deception_level_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get stats for all deception levels combined."""
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$nin": []},
            }
        },
        {"$addFields": {"template_id": {"$toObjectId": "$template_id"}}},
        {
            "$lookup": {
                "from": "template",
                "localField": "template_id",
                "foreignField": "_id",
                "as": "template",
            }
        },
        {"$unwind": {"path": "$template"}},
        {
            "$addFields": {
                "time_to_event": {"$subtract": ["$timeline.time", "$sent_date"]}
            }
        },
        {
            "$group": {
                "_id": "$cycle_id",
                "deception_level": {"$first": 14},
                "sent_count": {
                    "$sum": {"$cond": [{"$ne": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "total_clicks": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "unique_clicks": {
                    "$addToSet": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "clicked"]},
                            {"$toString": "$_id"},
                            "$$REMOVE",
                        ]
                    }
                },
                "user_reports": {
                    "$sum": {
                        "$cond": [{"$eq": ["$timeline.message", "reported"]}, 1, 0]
                    }
                },
                "unique_user_clicks": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "clicked"]},
                            {"$toString": "$_id"},
                            "$$REMOVE",
                        ]
                    }
                },
                "one_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [1, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "three_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [3, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "five_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [5, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "fifteen_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [15, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "thirty_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [30, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "sixty_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [60, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "two_hours": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [2, 60, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "three_hours": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [3, 60, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "four_hours": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [4, 60, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "one_day": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [24, 60, 60000]},
                                        ]
                                    },
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
            }
        },
        {
            "$project": {
                "deception_level": "$deception_level",
                "sent_count": "$sent_count",
                "total_clicks": "$total_clicks",
                "unique_clicks": "$unique_clicks",
                "unique_user_clicks": "$unique_user_clicks",
                "user_reports": "$user_reports",
                "click_percentage_over_time.one_minutes.count": "$one_minutes",
                "click_percentage_over_time.one_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {"$round": [{"$divide": ["$one_minutes", "$total_clicks"]}, 4]},
                    ]
                },
                "click_percentage_over_time.three_minutes.count": "$three_minutes",
                "click_percentage_over_time.three_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {
                            "$round": [
                                {"$divide": ["$three_minutes", "$total_clicks"]},
                                4,
                            ]
                        },
                    ]
                },
                "click_percentage_over_time.five_minutes.count": "$five_minutes",
                "click_percentage_over_time.five_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {
                            "$round": [
                                {"$divide": ["$five_minutes", "$total_clicks"]},
                                4,
                            ]
                        },
                    ]
                },
                "click_percentage_over_time.fifteen_minutes.count": "$fifteen_minutes",
                "click_percentage_over_time.fifteen_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {
                            "$round": [
                                {"$divide": ["$fifteen_minutes", "$total_clicks"]},
                                4,
                            ]
                        },
                    ]
                },
                "click_percentage_over_time.thirty_minutes.count": "$thirty_minutes",
                "click_percentage_over_time.thirty_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {
                            "$round": [
                                {"$divide": ["$thirty_minutes", "$total_clicks"]},
                                4,
                            ]
                        },
                    ]
                },
                "click_percentage_over_time.sixty_minutes.count": "$sixty_minutes",
                "click_percentage_over_time.sixty_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {
                            "$round": [
                                {"$divide": ["$sixty_minutes", "$total_clicks"]},
                                4,
                            ]
                        },
                    ]
                },
                "click_percentage_over_time.two_hours.count": "$two_hours",
                "click_percentage_over_time.two_hours.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {"$round": [{"$divide": ["$two_hours", "$total_clicks"]}, 4]},
                    ]
                },
                "click_percentage_over_time.three_hours.count": "$three_hours",
                "click_percentage_over_time.three_hours.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {"$round": [{"$divide": ["$three_hours", "$total_clicks"]}, 4]},
                    ]
                },
                "click_percentage_over_time.four_hours.count": "$four_hours",
                "click_percentage_over_time.four_hours.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {"$round": [{"$divide": ["$four_hours", "$total_clicks"]}, 4]},
                    ]
                },
                "click_percentage_over_time.one_day.count": "$one_day",
                "click_percentage_over_time.one_day.ratio": {
                    "$cond": [
                        {"$eq": ["$total_clicks", 0]},
                        0,
                        {"$round": [{"$divide": ["$one_day", "$total_clicks"]}, 4]},
                    ]
                },
            }
        },
    ]
    all_deception_level_stats = target_manager.aggregate(pipeline)

    for deception_level in all_deception_level_stats:
        deception_level["unique_clicks"] = len(deception_level["unique_clicks"])
        deception_level["unique_user_clicks"] = calculate_unique_user_clicks(
            deception_level["unique_user_clicks"]
        )
    return all_deception_level_stats


def calculate_composite_deception_stats(
    deception_level_stats, indices, deception_level
):
    """Aggregate deception score stats to get deception level stats."""
    if len(indices) == 2:
        composite_deception_level = {
            "deception_level": deception_level,
            "sent_count": deception_level_stats[indices[0]]["sent_count"]
            + deception_level_stats[indices[1]]["sent_count"],
            "unique_clicks": deception_level_stats[indices[0]]["unique_clicks"]
            + deception_level_stats[indices[1]]["unique_clicks"],
            "total_clicks": deception_level_stats[indices[0]]["total_clicks"]
            + deception_level_stats[indices[1]]["total_clicks"],
            "user_reports": deception_level_stats[indices[0]]["user_reports"]
            + deception_level_stats[indices[1]]["user_reports"],
            "unique_user_clicks": {
                k: deception_level_stats[indices[0]]["unique_user_clicks"].get(k, 0)
                + deception_level_stats[indices[1]]["unique_user_clicks"].get(k, 0)
                for k in set(deception_level_stats[indices[0]]["unique_user_clicks"])
                | set(deception_level_stats[indices[1]]["unique_user_clicks"])
            },
            "click_percentage_over_time": {
                "one_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["one_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "one_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "three_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["three_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "three_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "five_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["five_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "five_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "fifteen_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["fifteen_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "fifteen_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "thirty_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["thirty_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "thirty_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "sixty_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["sixty_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "sixty_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "two_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["two_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "two_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "three_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["three_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "three_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "four_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["four_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "four_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "one_day": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["one_day"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "one_day"
                    ]["count"],
                    "ratio": 0.0,
                },
            },
        }
        for key in list(composite_deception_level["click_percentage_over_time"].keys()):
            composite_deception_level["click_percentage_over_time"][key][
                "ratio"
            ] = get_ratio(
                composite_deception_level["click_percentage_over_time"][key]["count"],
                composite_deception_level["total_clicks"],
            )
        deception_level_stats.append(composite_deception_level)

    elif len(indices) == 3:
        composite_deception_level = {
            "deception_level": deception_level,
            "sent_count": deception_level_stats[indices[0]]["sent_count"]
            + deception_level_stats[indices[1]]["sent_count"]
            + deception_level_stats[indices[2]]["sent_count"],
            "unique_clicks": deception_level_stats[indices[0]]["unique_clicks"]
            + deception_level_stats[indices[1]]["unique_clicks"]
            + deception_level_stats[indices[2]]["unique_clicks"],
            "total_clicks": deception_level_stats[indices[0]]["total_clicks"]
            + deception_level_stats[indices[1]]["total_clicks"]
            + deception_level_stats[indices[2]]["total_clicks"],
            "user_reports": deception_level_stats[indices[0]]["user_reports"]
            + deception_level_stats[indices[1]]["user_reports"]
            + deception_level_stats[indices[2]]["user_reports"],
            "unique_user_clicks": {
                k: deception_level_stats[indices[0]]["unique_user_clicks"].get(k, 0)
                + deception_level_stats[indices[1]]["unique_user_clicks"].get(k, 0)
                + deception_level_stats[indices[2]]["unique_user_clicks"].get(k, 0)
                for k in set(deception_level_stats[indices[0]]["unique_user_clicks"])
                | set(deception_level_stats[indices[1]]["unique_user_clicks"])
                | set(deception_level_stats[indices[2]]["unique_user_clicks"])
            },
            "click_percentage_over_time": {
                "one_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["one_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "one_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "one_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "three_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["three_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "three_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "three_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "five_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["five_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "five_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "five_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "fifteen_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["fifteen_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "fifteen_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "fifteen_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "thirty_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["thirty_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "thirty_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "thirty_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "sixty_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["sixty_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "sixty_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "sixty_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "two_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["two_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "two_hours"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "two_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "three_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["three_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "three_hours"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "three_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "four_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["four_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "four_hours"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "four_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "one_day": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["one_day"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "one_day"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "one_day"
                    ]["count"],
                    "ratio": 0.0,
                },
            },
        }
        for key in list(composite_deception_level["click_percentage_over_time"].keys()):
            composite_deception_level["click_percentage_over_time"][key][
                "ratio"
            ] = get_ratio(
                composite_deception_level["click_percentage_over_time"][key]["count"],
                composite_deception_level["total_clicks"],
            )
        deception_level_stats.append(composite_deception_level)


def calculate_unique_user_clicks(target_list):
    """Get unique user clicks stats."""
    count_list = list({i: target_list.count(i) for i in target_list}.values())
    count_dict = {i: count_list.count(i) for i in count_list}

    unique_user_clicks = {
        "four_five_clicks": count_dict.get(4, 0) + count_dict.get("5", 0),
        "one_click": count_dict.get(1, 0),
        "six_ten_clicks": count_dict.get(
            6, 0
        )  # TODO rename this field to "six_nine_clicks"
        + count_dict.get(7, 0)
        + count_dict.get(8, 0)
        + count_dict.get(
            9, 0
        ),  # + count_dict.get("10", 0), # Ten clicks should not be counted in two places, the buckets are named poorly.
        "ten_plus_clicks": 0,
        "two_three_clicks": count_dict.get(2, 0) + count_dict.get(3, 0),
    }
    unique_user_clicks["ten_plus_clicks"] = len(set(target_list)) - (
        unique_user_clicks["one_click"]
        + unique_user_clicks["two_three_clicks"]
        + unique_user_clicks["four_five_clicks"]
        + unique_user_clicks["six_ten_clicks"]
    )
    return unique_user_clicks


def get_indicator_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get indicator stats."""
    indicators = get_indicators()
    group_pipeline, project_pipeline = get_subpipelines(indicators)
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$nin": []},
            }
        },
        {"$addFields": {"template_id": {"$toObjectId": "$template_id"}}},
        {
            "$lookup": {
                "from": "template",
                "localField": "template_id",
                "foreignField": "_id",
                "as": "template",
            }
        },
        {"$unwind": {"path": "$template"}},
        {"$group": group_pipeline},
        {"$project": project_pipeline},
    ]
    indicator_stats = target_manager.aggregate(pipeline)

    # reformat to a list of dicts
    if len(indicator_stats) > 0:
        del indicator_stats[0]["_id"]
        indicator_stats = list(indicator_stats[0].values())

    return indicator_stats


def get_subpipelines(indicators):
    """Get subpipelines for the group and project stage."""
    group_pipeline = {"_id": "$cycle_id"}
    project_pipeline = {}
    for group, gv in indicators.items():
        for indicator, iv in gv.items():
            for value, label in iv["values"].items():
                label = label["label"]
                project_pipeline[f"{group}_{label}_{indicator}.group"] = group
                project_pipeline[f"{group}_{label}_{indicator}.indicator"] = indicator
                project_pipeline[f"{group}_{label}_{indicator}.label"] = label
                project_pipeline[f"{group}_{label}_{indicator}.value"] = {
                    "$toInt": value
                }
                project_pipeline[
                    f"{group}_{label}_{indicator}.sent.count"
                ] = f"${group}_{label}_{indicator}_sent"
                project_pipeline[
                    f"{group}_{label}_{indicator}.clicked.count"
                ] = f"${group}_{label}_{indicator}_clicked"
                project_pipeline[f"{group}_{label}_{indicator}.clicked.ratio"] = {
                    "$round": [
                        {
                            "$cond": [
                                {"$eq": [f"${group}_{label}_{indicator}_sent", 0]},
                                0,
                                {
                                    "$divide": [
                                        f"${group}_{label}_{indicator}_clicked",
                                        f"${group}_{label}_{indicator}_sent",
                                    ]
                                },
                            ]
                        },
                        4,
                    ]
                }
                project_pipeline[
                    f"{group}_{label}_{indicator}.opened.count"
                ] = f"${group}_{label}_{indicator}_opened"
                project_pipeline[f"{group}_{label}_{indicator}.opened.ratio"] = {
                    "$round": [
                        {
                            "$cond": [
                                {"$eq": [f"${group}_{label}_{indicator}_sent", 0]},
                                0,
                                {
                                    "$divide": [
                                        f"${group}_{label}_{indicator}_opened",
                                        f"${group}_{label}_{indicator}_sent",
                                    ]
                                },
                            ]
                        },
                        4,
                    ]
                }
                project_pipeline[
                    f"{group}_{label}_{indicator}.reported.count"
                ] = f"${group}_{label}_{indicator}_reported"
                project_pipeline[f"{group}_{label}_{indicator}.reported.ratio"] = {
                    "$round": [
                        {
                            "$cond": [
                                {"$eq": [f"${group}_{label}_{indicator}_sent", 0]},
                                0,
                                {
                                    "$divide": [
                                        f"${group}_{label}_{indicator}_reported",
                                        f"${group}_{label}_{indicator}_sent",
                                    ]
                                },
                            ]
                        },
                        4,
                    ]
                }
                for event in ["sent", "clicked", "opened", "reported"]:
                    group_pipeline[
                        f"{group}_{label}_{indicator}_{event}"
                    ] = get_indicator_subpipeline(group, indicator, value, event)
    return group_pipeline, project_pipeline


def get_indicator_subpipeline(group, indicator, value, event):
    """Get subpipeline for each indicator."""
    if event == "sent":
        return {
            "$sum": {
                "$cond": [
                    {
                        "$and": [
                            {"$ne": ["$timeline.message", "clicked"]},
                            {
                                "$eq": [
                                    f"$template.indicators.{group}.{indicator}",
                                    int(value),
                                ]
                            },
                        ]
                    },
                    1,
                    0,
                ]
            }
        }
    else:
        return {
            "$sum": {
                "$cond": [
                    {
                        "$and": [
                            {"$eq": ["$timeline.message", event]},
                            {
                                "$eq": [
                                    f"$template.indicators.{group}.{indicator}",
                                    int(value),
                                ]
                            },
                        ]
                    },
                    1,
                    0,
                ]
            }
        }


def get_maxmind_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get maxmind stats."""
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline"}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$nin": []},
            }
        },
        {
            "$group": {
                "_id": "$timeline.details.asn_org",
                "asn_org": {"$first": "$timeline.details.asn_org"},
                "ips": {"$addToSet": "$timeline.details.ip"},
                "cities": {"$addToSet": "$timeline.details.city"},
                "clicks": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "opens": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "opened"]}, 1, 0]}
                },
            }
        },
    ]
    maxmind_stats = target_manager.aggregate(pipeline)

    for asn_org in maxmind_stats:
        asn_org["is_nonhuman"] = asn_org["asn_org"] in nonhuman_orgs

    # Sort alphebetically by asn_org
    maxmind_stats = sorted(maxmind_stats, key=lambda d: d["asn_org"])

    return maxmind_stats


def get_recommendation_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get recommendation stats."""
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$nin": []},
            }
        },
        {"$addFields": {"template_id": {"$toObjectId": "$template_id"}}},
        {
            "$lookup": {
                "from": "template",
                "localField": "template_id",
                "foreignField": "_id",
                "as": "template",
            }
        },
        {"$unwind": {"path": "$template"}},
        {
            "$addFields": {
                "recommendation_id": {
                    "$concatArrays": ["$template.sophisticated", "$template.red_flag"]
                }
            }
        },
        {"$unwind": {"path": "$recommendation_id", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {"recommendation_id": {"$toObjectId": "$recommendation_id"}}},
        {
            "$lookup": {
                "from": "recommendation",
                "localField": "recommendation_id",
                "foreignField": "_id",
                "as": "recommendation",
            }
        },
        {"$unwind": {"path": "$recommendation"}},
        {
            "$group": {
                "_id": "$recommendation_id",
                "recommendation": {"$first": "$recommendation"},
                "templates": {"$addToSet": "$template"},
                "sent_count": {
                    "$sum": {"$cond": [{"$ne": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "clicked": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "opened": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "opened"]}, 1, 0]}
                },
                "reported": {
                    "$sum": {
                        "$cond": [{"$eq": ["$timeline.message", "reported"]}, 1, 0]
                    }
                },
            }
        },
        {
            "$project": {
                "recommendation._id": "$recommendation._id",
                "recommendation.description": "$recommendation.description",
                "recommendation.title": "$recommendation.title",
                "recommendation.type": "$recommendation.type",
                "templates": {
                    "$map": {
                        "input": "$templates",
                        "as": "template",
                        "in": {
                            "_id": {"$toString": "$$template._id"},
                            "deception_score": "$$template.deception_score",
                            "from_address": "$$template.from_address",
                            "html": "$$template.html",
                            "indicators": "$$template.indicators",
                            "name": "$$template.name",
                            "red_flag": "$$template.red_flag",
                            "retired_description": "$$template.retired_description",
                            "sophisticated": "$$template.sophisticated",
                            "subject": "$$template.subject",
                        },
                    },
                },
                "sent.count": "$sent_count",
                "clicked.count": "$clicked",
                "clicked.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$clicked", "$sent_count"]}, 4]},
                    ]
                },
                "opened.count": "$opened",
                "opened.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$opened", "$sent_count"]}, 4]},
                    ]
                },
                "reported.count": "$reported",
                "reported.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$reported", "$sent_count"]}, 4]},
                    ]
                },
            }
        },
    ]
    recommendation_stats = target_manager.aggregate(pipeline)

    return recommendation_stats


def get_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get stats."""
    stats_pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$nin": []},
            }
        },
        {
            "$group": {
                "_id": "$deception_level",
                "sent_count": {
                    "$sum": {"$cond": [{"$ne": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "clicked": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "click_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "clicked"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
                "opened": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "opened"]}, 1, 0]}
                },
                "open_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "opened"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
                "reported": {
                    "$sum": {
                        "$cond": [{"$eq": ["$timeline.message", "reported"]}, 1, 0]
                    }
                },
                "report_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "reported"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
            }
        },
        {
            "$project": {
                "sent.count": "$sent_count",
                "clicked.count": "$clicked",
                "clicked.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$clicked", "$sent_count"]}, 4]},
                    ]
                },
                "clicked.average": {"$sum": [{"$avg": "$click_times"}, 0]},
                "clicked.maximum": {"$sum": [{"$max": "$click_times"}, 0]},
                "clicked.minimum": {"$sum": [{"$min": "$click_times"}, 0]},
                "clicked.median": "$click_times",
                "opened.count": "$opened",
                "opened.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$opened", "$sent_count"]}, 4]},
                    ]
                },
                "opened.average": {"$sum": [{"$avg": "$open_times"}, 0]},
                "opened.maximum": {"$sum": [{"$max": "$open_times"}, 0]},
                "opened.minimum": {"$sum": [{"$min": "$open_times"}, 0]},
                "opened.median": "$open_times",
                "reported.count": "$reported",
                "reported.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$reported", "$sent_count"]}, 4]},
                    ]
                },
                "reported.average": {"$sum": [{"$avg": "$report_times"}, 0]},
                "reported.maximum": {"$sum": [{"$max": "$report_times"}, 0]},
                "reported.minimum": {"$sum": [{"$min": "$report_times"}, 0]},
                "reported.median": "$report_times",
            }
        },
    ]
    stats = target_manager.aggregate(stats_pipeline)
    # format from list into dictionary
    stats = {item["_id"]: item for item in stats}

    all_stats_pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$nin": []},
            }
        },
        {
            "$group": {
                "_id": "$cycle_id",
                "sent_count": {
                    "$sum": {"$cond": [{"$ne": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "clicked": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "click_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "clicked"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
                "opened": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "opened"]}, 1, 0]}
                },
                "open_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "opened"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
                "reported": {
                    "$sum": {
                        "$cond": [{"$eq": ["$timeline.message", "reported"]}, 1, 0]
                    }
                },
                "report_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "reported"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
            }
        },
        {
            "$project": {
                "sent.count": "$sent_count",
                "clicked.count": "$clicked",
                "clicked.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$clicked", "$sent_count"]}, 4]},
                    ]
                },
                "clicked.average": {"$sum": [{"$avg": "$click_times"}, 0]},
                "clicked.maximum": {"$sum": [{"$max": "$click_times"}, 0]},
                "clicked.minimum": {"$sum": [{"$min": "$click_times"}, 0]},
                "clicked.median": "$click_times",
                "opened.count": "$opened",
                "opened.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$opened", "$sent_count"]}, 4]},
                    ]
                },
                "opened.average": {"$sum": [{"$avg": "$open_times"}, 0]},
                "opened.maximum": {"$sum": [{"$max": "$open_times"}, 0]},
                "opened.minimum": {"$sum": [{"$min": "$open_times"}, 0]},
                "opened.median": "$open_times",
                "reported.count": "$reported",
                "reported.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$reported", "$sent_count"]}, 4]},
                    ]
                },
                "reported.average": {"$sum": [{"$avg": "$report_times"}, 0]},
                "reported.maximum": {"$sum": [{"$max": "$report_times"}, 0]},
                "reported.minimum": {"$sum": [{"$min": "$report_times"}, 0]},
                "reported.median": "$report_times",
            }
        },
    ]
    all_stats = target_manager.aggregate(all_stats_pipeline)

    emptyStat = {
        "clicked": {
            "average": 0,
            "count": 0,
            "maximum": 0,
            "median": 0,
            "minimum": 0,
            "ratio": 0,
        },
        "opened": {
            "average": 0,
            "count": 0,
            "maximum": 0,
            "median": 0,
            "minimum": 0,
            "ratio": 0,
        },
        "reported": {
            "average": 0,
            "count": 0,
            "maximum": 0,
            "median": 0,
            "minimum": 0,
            "ratio": 0,
        },
        "sent": {"count": 0},
    }

    stats["all"] = all_stats[0] if len(all_stats) > 0 else emptyStat
    stats["low"] = stats["low"] if "low" in stats.keys() else emptyStat
    stats["moderate"] = stats["moderate"] if "moderate" in stats.keys() else emptyStat
    stats["high"] = stats["high"] if "high" in stats.keys() else emptyStat

    # calculate medians on the python side
    for level in ["all", "low", "moderate", "high"]:
        for event in ["clicked", "opened", "reported"]:
            if stats[level][event]["median"] == 0:
                pass
            elif len(stats[level][event]["median"]) > 0:
                stats[level][event]["median"] = statistics.median(
                    stats[level][event]["median"]
                )
            else:
                stats[level][event]["median"] = 0

    return stats


def get_target_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get target stats."""
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$nin": []},
            }
        },
        {
            "$group": {
                "_id": "$position",
                "group": {"$first": "$position"},
                "sent_count": {
                    "$sum": {"$cond": [{"$ne": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "clicks": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "opens": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "opened"]}, 1, 0]}
                },
                "reports": {
                    "$sum": {
                        "$cond": [{"$eq": ["$timeline.message", "reported"]}, 1, 0]
                    }
                },
            }
        },
        {
            "$project": {
                "group": "$_id",
                "sent.count": "$sent_count",
                "clicked.count": "$clicks",
                "opened.count": "$opens",
                "reported.count": "$reports",
            }
        },
    ]

    target_stats = target_manager.aggregate(pipeline)

    # Sort alphebetically by group
    target_stats = sorted(target_stats, key=lambda d: d["group"])

    return target_stats


def get_template_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get template stats."""
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$nin": []},
            }
        },
        {"$addFields": {"template_id": {"$toObjectId": "$template_id"}}},
        {
            "$lookup": {
                "from": "template",
                "localField": "template_id",
                "foreignField": "_id",
                "as": "template",
            }
        },
        {"$unwind": {"path": "$template"}},
        {
            "$group": {
                "_id": "$template._id",
                "template": {"$first": "$template"},
                "template_id": {"$first": {"$toString": "$template._id"}},
                "sent_count": {
                    "$sum": {"$cond": [{"$ne": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "clicked": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "opened": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "opened"]}, 1, 0]}
                },
                "reported": {
                    "$sum": {
                        "$cond": [{"$eq": ["$timeline.message", "reported"]}, 1, 0]
                    }
                },
            }
        },
        {
            "$project": {
                "recommendation": "$recommendation",
                "template._id": "$template._id",
                "template.deception_score": "$template.deception_score",
                "template.from_address": "$template.from_address",
                "template.html": "$template.html",
                "template.indicators": "$template.indicators",
                "template.name": "$template.name",
                "template.red_flag": "$template.red_flag",
                "template.retired_description": "$template.retired_description",
                "template.sophisticated": "$template.sophisticated",
                "template.subject": "$template.subject",
                "template_id": {"$toString": "$template._id"},
                "deception_level": {
                    "$switch": {
                        "branches": [
                            {
                                "case": {"$lte": ["$template.deception_score", 2]},
                                "then": "low",
                            },
                            {
                                "case": {
                                    "$and": [
                                        {"$gt": ["$template.deception_score", 2]},
                                        {"$lte": ["$template.deception_score", 4]},
                                    ]
                                },
                                "then": "moderate",
                            },
                            {
                                "case": {
                                    "$and": [
                                        {"$gt": ["$template.deception_score", 4]},
                                        {"$lte": ["$template.deception_score", 11]},
                                    ]
                                },
                                "then": "high",
                            },
                        ],
                        "default": "low",
                    }
                },
                "sent.count": "$sent_count",
                "clicked.count": "$clicked",
                "clicked.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$clicked", "$sent_count"]}, 4]},
                    ]
                },
                "opened.count": "$opened",
                "opened.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$opened", "$sent_count"]}, 4]},
                    ]
                },
                "reported.count": "$reported",
                "reported.ratio": {
                    "$cond": [
                        {"$eq": ["$sent_count", 0]},
                        0,
                        {"$round": [{"$divide": ["$reported", "$sent_count"]}, 4]},
                    ]
                },
            }
        },
    ]
    template_stats = target_manager.aggregate(pipeline)

    if len(template_stats) == 3:
        rank_templates(template_stats)
        # Sort low, moderate, high
        template_stats = sorted(template_stats, key=lambda d: d["deception_level"])
        template_stats = [template_stats[1], template_stats[2], template_stats[0]]

    return template_stats


def rank_templates(template_stats: list):
    """Rank templates by opened and clicked counts."""
    for event in ["opened", "clicked", "reported"]:
        template_stats = sorted(
            template_stats, key=lambda d: d[event]["ratio"], reverse=True
        )
        template_stats[0][event]["rank"] = 1
        template_stats[1][event]["rank"] = (
            template_stats[0][event]["rank"] + 1
            if template_stats[0][event]["ratio"] != template_stats[1][event]["ratio"]
            else template_stats[0][event]["rank"]
        )
        template_stats[2][event]["rank"] = (
            template_stats[1][event]["rank"] + 1
            if template_stats[1][event]["ratio"] != template_stats[2][event]["ratio"]
            else template_stats[1][event]["rank"]
        )


def get_time_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get time stats."""
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline"}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$nin": []},
            }
        },
        {
            "$addFields": {
                "time_to_event": {"$subtract": ["$timeline.time", "$sent_date"]}
            }
        },
        {
            "$group": {
                "_id": "$timeline.message",
                "events": {"$sum": 1},
                "one_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [1, 60000]},
                                        ]
                                    },
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "three_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [3, 60000]},
                                        ]
                                    },
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "five_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [5, 60000]},
                                        ]
                                    },
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "fifteen_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [15, 60000]},
                                        ]
                                    },
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "thirty_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [30, 60000]},
                                        ]
                                    },
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "sixty_minutes": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [60, 60000]},
                                        ]
                                    },
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "two_hours": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [2, 60, 60000]},
                                        ]
                                    },
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "three_hours": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [3, 60, 60000]},
                                        ]
                                    },
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "four_hours": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [4, 60, 60000]},
                                        ]
                                    },
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "one_day": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gt": ["$time_to_event", 0]},
                                    {
                                        "$lte": [
                                            "$time_to_event",
                                            {"$multiply": [24, 60, 60000]},
                                        ]
                                    },
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
            }
        },
        {
            "$project": {
                "one_minutes.count": "$one_minutes",
                "one_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$events", 0]},
                        0,
                        {"$round": [{"$divide": ["$one_minutes", "$events"]}, 4]},
                    ]
                },
                "three_minutes.count": "$three_minutes",
                "three_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$events", 0]},
                        0,
                        {"$round": [{"$divide": ["$three_minutes", "$events"]}, 4]},
                    ]
                },
                "five_minutes.count": "$five_minutes",
                "five_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$events", 0]},
                        0,
                        {"$round": [{"$divide": ["$five_minutes", "$events"]}, 4]},
                    ]
                },
                "fifteen_minutes.count": "$fifteen_minutes",
                "fifteen_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$events", 0]},
                        0,
                        {"$round": [{"$divide": ["$fifteen_minutes", "$events"]}, 4]},
                    ]
                },
                "thirty_minutes.count": "$thirty_minutes",
                "thirty_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$events", 0]},
                        0,
                        {"$round": [{"$divide": ["$thirty_minutes", "$events"]}, 4]},
                    ]
                },
                "sixty_minutes.count": "$sixty_minutes",
                "sixty_minutes.ratio": {
                    "$cond": [
                        {"$eq": ["$events", 0]},
                        0,
                        {"$round": [{"$divide": ["$sixty_minutes", "$events"]}, 4]},
                    ]
                },
                "two_hours.count": "$two_hours",
                "two_hours.ratio": {
                    "$cond": [
                        {"$eq": ["$events", 0]},
                        0,
                        {"$round": [{"$divide": ["$two_hours", "$events"]}, 4]},
                    ]
                },
                "three_hours.count": "$three_hours",
                "three_hours.ratio": {
                    "$cond": [
                        {"$eq": ["$events", 0]},
                        0,
                        {"$round": [{"$divide": ["$three_hours", "$events"]}, 4]},
                    ]
                },
                "four_hours.count": "$four_hours",
                "four_hours.ratio": {
                    "$cond": [
                        {"$eq": ["$events", 0]},
                        0,
                        {"$round": [{"$divide": ["$four_hours", "$events"]}, 4]},
                    ]
                },
                "one_day.count": "$one_day",
                "one_day.ratio": {
                    "$cond": [
                        {"$eq": ["$events", 0]},
                        0,
                        {"$round": [{"$divide": ["$one_day", "$events"]}, 4]},
                    ]
                },
            }
        },
    ]
    time_stats = target_manager.aggregate(pipeline)

    time_stats = {item["_id"]: item for item in time_stats}

    return time_stats


def get_rolling_emails(n_days):
    """Get total number of emails sent/clicked by the system over the last x days."""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "sent": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {
                                        "$gte": [
                                            "$sent_date",
                                            datetime.now() - timedelta(days=n_days),
                                        ]
                                    },
                                    {"$lte": ["$sent_date", datetime.now()]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "scheduled": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {
                                        "$gte": [
                                            "$send_date",
                                            datetime.now() - timedelta(days=n_days),
                                        ]
                                    },
                                    {"$lte": ["$send_date", datetime.now()]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "clicked": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {
                                        "$gte": [
                                            "$send_date",
                                            datetime.now() - timedelta(days=n_days),
                                        ]
                                    },
                                    {"$lte": ["$send_date", datetime.now()]},
                                    {"$eq": ["$timeline.message", "clicked"]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
            }
        }
    ]
    aggregate = target_manager.aggregate(pipeline)
    aggregate = aggregate[0] if len(aggregate) > 0 else {}

    try:
        ratio = aggregate.get("sent", 0) / aggregate.get("scheduled", 0)
    except ZeroDivisionError:
        ratio = 1
    ratio = round(ratio, 4)

    return (
        aggregate.get("sent", 0),
        aggregate.get("scheduled", 0),
        ratio,
        aggregate.get("clicked", 0),
    )


def get_rolling_tasks(n_days):
    """Get total number of tasks scheduled/succeeded by the system over the last x days."""
    pipeline = [
        {"$match": {"active": {"$eq": True}}},
        {"$unwind": {"path": "$tasks"}},
        {
            "$match": {
                "tasks.executed": {"$eq": True},
                "tasks.scheduled_date": {
                    "$gte": datetime.now() - timedelta(days=n_days),
                    "$lte": datetime.now() - timedelta(minutes=5),
                },
            }
        },
        {"$count": "succeeded"},
    ]
    aggregate = cycle_manager.aggregate(pipeline)
    succeeded = (
        aggregate[0].get("succeeded", 0)
        if len(cycle_manager.aggregate(pipeline)) > 0
        else 0
    )

    pipeline = [
        {"$match": {"active": {"$eq": True}}},
        {"$unwind": {"path": "$tasks"}},
        {
            "$match": {
                "tasks.scheduled_date": {
                    "$gte": datetime.now() - timedelta(days=n_days),
                    "$lte": datetime.now() - timedelta(minutes=5),
                },
            }
        },
        {"$count": "scheduled"},
    ]

    aggregate = cycle_manager.aggregate(pipeline)
    scheduled = (
        aggregate[0].get("scheduled", 0)
        if len(cycle_manager.aggregate(pipeline)) > 0
        else 0
    )

    try:
        ratio = succeeded / scheduled
    except ZeroDivisionError:
        ratio = 1
    ratio = round(ratio, 4)

    return succeeded, scheduled, ratio


def get_ratio(numerator, denominator):
    """Get ratio from numerator and denominator."""
    return (
        0
        if not denominator
        else round(float(numerator or 0) / float(denominator), ndigits=4)
    )


def get_nonhuman_orgs():
    """Get nonhuman orgs from database."""
    return [x["asn_org"] for x in nonhuman_manager.all()]


def get_all_customer_stats():
    """Get all customer stats."""
    levels = ["all", "low", "moderate", "high"]
    actions = ["sent", "opened", "clicked", "reported"]
    all_stats = {}
    for level in levels:
        all_stats[level] = {}
        for action in actions:
            all_stats[level][action] = {"count": 0, "ratios": []}

    cycles = cycle_manager.all(fields=["_id", "dirty_stats", "stats"])
    for cycle in cycles:
        if cycle.get("dirty_stats", True):
            cycle = cycle_manager.get(cycle["_id"])
            get_cycle_stats(cycle)

        for level in levels:
            for action in actions:
                all_stats[level][action]["count"] += cycle["stats"]["stats"][level][
                    action
                ]["count"]
                if action != "sent":
                    all_stats[level][action]["ratios"].append(
                        cycle["stats"]["stats"][level][action]["ratio"]
                    )

    # Process average of ratios
    for level in levels:
        for action in actions:
            if action != "sent":
                ratios = all_stats[level][action]["ratios"]
                length = len(ratios)
                all_stats[level][action]["average"] = (
                    sum(ratios) / length if length != 0 else 0
                )
                all_stats[level][action]["minimum"] = min(ratios) if ratios else 0
                all_stats[level][action]["maximum"] = max(ratios) if ratios else 0
                all_stats[level][action]["median"] = (
                    statistics.median(ratios) if ratios else 0
                )

    process_ratios(all_stats)
    return all_stats


def get_sending_profile_metrics(subscriptions, sending_profiles):
    """Get stats on Sending Profiles."""
    templates = template_manager.all(
        fields=["_id", "sending_profile_id"],
        params={"sending_profile_id": {"$in": [s["_id"] for s in sending_profiles]}},
    )

    cycles = cycle_manager.all(
        fields=["_id", "subscription_id", "template_ids"], params={"active": True}
    )

    for sp in sending_profiles:
        active_subs = list(
            filter(
                lambda x: x["sending_profile_id"] == sp["_id"]
                and x["status"] == "running",
                subscriptions,
            )
        )
        templs = [
            t["_id"]
            for t in list(
                filter(lambda x: x["sending_profile_id"] == sp["_id"], templates)
            )
        ]

        cycles_using = list(
            filter(
                lambda x: any(item in templs for item in x["template_ids"])
                or x["subscription_id"] in [sub["_id"] for sub in active_subs],
                cycles,
            )
        )

        subs_using = list(
            filter(
                lambda x: x["_id"] in [c["subscription_id"] for c in cycles_using],
                subscriptions,
            )
        )

        sp["customers_using"] = len(list({s["customer_id"] for s in subs_using}))
