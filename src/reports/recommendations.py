from api.services import RecommendationService
from pprint import pprint

recommendation_service = RecommendationService()


def get_relevant_recommendations(subscription_stats):
    recommendations_list = recommendation_service.get_list()
    if not recommendations_list:
        return {}

    template_stats = get_template_stats(subscription_stats)
    deception_level_stats = get_deception_level_stats(template_stats)
    print(f"{deception_level_stats=}")

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


def get_template_stats(subscription_stats):
    stats = []
    for i in subscription_stats.get("campaign_results"):
        clicked_count = i["campaign_stats"].get("opened", {}).get("count", 0)
        stats.append(
            {
                "template_uuid": i["template_uuid"],
                "clicked_count": clicked_count,
                "template_details": i["template_details"],
                "deception_level": i["deception_level"],
            }
        )
    return stats


def get_indicator_stats(template_stats):
    indicator_stats = {}
    for t in template_stats:
        relevancy = t["template_details"]["relevancy"]


def get_deception_level_stats(template_stats):
    deception_level_stats = {}
    for t in template_stats:
        deception_level = t["deception_level"]
        if deception_level not in deception_level_stats:
            deception_level_stats[deception_level] = 0
        deception_level_stats[deception_level] += t["clicked_count"]
    return deception_level_stats


def get_recomendations_uuid(recommendations_list, sorted_templates):
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
