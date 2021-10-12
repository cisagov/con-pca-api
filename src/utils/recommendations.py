"""Recommendation Utils."""
# cisagov Libraries
from api.manager import RecommendationManager

recommendation_manager = RecommendationManager()


def get_recommendations():
    """Get recommendations from db."""
    response = {
        "levels": {
            "1": {
                "name": "Level 1",
                "recommendation": "",
            },
            "2": {
                "name": "Level 2",
                "recommendation": "",
            },
            "3": {
                "name": "Level 3",
                "recommendation": "",
            },
            "4": {
                "name": "Level 4",
                "recommendation": "",
            },
            "5": {
                "name": "Level 5",
                "recommendation": "",
            },
            "6": {
                "name": "Level 6",
                "recommendation": "",
            },
        },
        "indicators": {
            "appearance": {
                "grammar": {
                    "name": "Grammar",
                    "values": {
                        "0": {"recommendation": "", "label": "Poor"},
                        "1": {"recommendation": "", "label": "Decent"},
                        "2": {"recommendation": "", "label": "Proper"},
                    },
                },
                "link_domain": {
                    "name": "Link/Domain",
                    "values": {
                        "0": {"recommendation": "", "label": "Unrelated"},
                        "1": {"recommendation": "", "label": "Related/Hidden/Spoofed"},
                    },
                },
                "logo_graphics": {
                    "name": "Logo/Graphics",
                    "values": {
                        "0": {"recommendation": "", "label": "Plain Text"},
                        "1": {"recommendation": "", "label": "Visual Appeal"},
                    },
                },
            },
            "sender": {
                "external": {
                    "name": "External",
                    "values": {
                        "0": {
                            "recommendation": "",
                            "label": "Not External/Unpsecified",
                        },
                        "1": {"recommendation": "", "label": "Specified"},
                    },
                },
                "internal": {
                    "name": "Internal",
                    "values": {
                        "0": {
                            "recommendation": "",
                            "label": "Not Internal/Unspecified",
                        },
                        "1": {"recommendation": "", "label": "Generic/Close"},
                        "2": {"recommendation": "", "label": "Spoofed"},
                    },
                },
                "authoritative": {
                    "name": "Authoritative",
                    "values": {
                        "0": {"recommendation": "", "label": "None"},
                        "1": {"recommendation": "", "label": "Peer"},
                        "2": {"recommendation": "", "label": "Superior"},
                    },
                },
            },
            "relevancy": {
                "organization": {
                    "name": "Orginization",
                    "values": {
                        "0": {"recommendation": "", "label": "No"},
                        "1": {"recommendation": "", "label": "Yes"},
                    },
                },
                "public_news": {
                    "name": "Public News",
                    "values": {
                        "0": {"recommendation": "", "label": "No"},
                        "1": {"recommendation": "", "label": "Yes"},
                    },
                },
            },
            "behavior": {
                "fear": {
                    "name": "Fear",
                    "values": {
                        "0": {"recommendation": "", "label": "No"},
                        "1": {"recommendation": "", "label": "Yes"},
                    },
                },
                "duty_obligation": {
                    "name": "Duty or Obligation",
                    "values": {
                        "0": {"recommendation": "", "label": "No"},
                        "1": {"recommendation": "", "label": "Yes"},
                    },
                },
                "curiosity": {
                    "name": "Curiosity",
                    "values": {
                        "0": {"recommendation": "", "label": "No"},
                        "1": {"recommendation": "", "label": "Yes"},
                    },
                },
                "greed": {
                    "name": "Greed",
                    "values": {
                        "0": {"recommendation": "", "label": "No"},
                        "1": {"recommendation": "", "label": "Yes"},
                    },
                },
            },
        },
    }
    recommendations = recommendation_manager.all()
    for recommendation in recommendations:
        value = recommendation["value"]
        if recommendation["type"] == "level":
            response["levels"][recommendation["value"]][
                "recommendation"
            ] = recommendation["recommendation"]
        elif recommendation["type"] == "indicator":
            group = recommendation["group"]
            indicator = recommendation["indicator"]

            if (
                group in response["indicators"]
                and indicator in response["indicators"][group]
            ):
                response["indicators"][group][indicator]["values"][value][
                    "recommendation"
                ] = recommendation["recommendation"]

    return response


def save_recommendations(recommendations):
    """Save recommendations to db."""
    for group, gv in recommendations["indicators"].items():
        for indicator, iv in gv.items():
            for value, v in iv["values"].items():
                query = {
                    "type": "indicator",
                    "group": group,
                    "indicator": indicator,
                    "value": value,
                }
                data = dict(query)
                data["recommendation"] = v["recommendation"]
                recommendation_manager.upsert(query=query, data=data)
    for value, v in recommendations["levels"].items():
        query = {"type": "level", "value": value}
        data = dict(query)
        data["recommendation"] = v["recommendation"]
        recommendation_manager.upsert(query=query, data=data)
