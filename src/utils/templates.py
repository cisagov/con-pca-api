"""Template utils."""
# Standard Python Libraries
import random


class LEVELS:
    """Deception levels."""

    high = 5
    moderate = 3
    low = 0


TEMPLATE_INDICATORS = {
    "appearance": {
        "grammar": {
            "name": "Grammar",
            "values": {
                "0": "Poor",
                "1": "Decent",
                "2": "Proper",
            },
        },
        "link_domain": {
            "name": "Link/Domain",
            "values": {
                "0": "Unrelated",
                "1": "Related/Hidden/Spoofed",
            },
        },
        "logo_graphics": {
            "name": "Logo/Graphics",
            "values": {
                "0": "Plain Text",
                "1": "Visual Appeal",
            },
        },
    },
    "sender": {
        "external": {
            "name": "External",
            "values": {
                "0": "Not External/Unpsecified",
                "1": "Specified",
            },
        },
        "internal": {
            "name": "Internal",
            "values": {
                "0": "Not Internal/Unspecified",
                "1": "Generic/Close",
                "2": "Spoofed",
            },
        },
        "authoritative": {
            "name": "Authoritative",
            "values": {
                "0": "None",
                "1": "Peer",
                "2": "Superior",
            },
        },
    },
    "relevancy": {
        "organization": {
            "name": "Orginization",
            "values": {
                "0": "No",
                "1": "Yes",
            },
        },
        "public_news": {
            "name": "Public News",
            "values": {
                "0": "No",
                "1": "Yes",
            },
        },
    },
    "behavior": {
        "fear": {
            "name": "Fear",
            "values": {
                "0": "Yes",
                "1": "No",
            },
        },
        "duty_obligation": {
            "name": "Duty or Obligation",
            "values": {
                "0": "Yes",
                "1": "No",
            },
        },
        "curiosity": {
            "name": "Curiosity",
            "values": {
                "0": "Yes",
                "1": "No",
            },
        },
        "greed": {
            "name": "Greed",
            "values": {
                "0": "Yes",
                "1": "No",
            },
        },
    },
}


def select_templates(templates: list, count: int = 1) -> list:
    """Group Templates by score."""
    response = []
    grouped_templates = group_templates(templates)
    for k, v in grouped_templates.items():
        sample_size = count if len(v) > count else len(v)
        response.append(random.sample(v, sample_size))
    return response


def group_templates(templates):
    """Group all templates by deception score."""
    groups = {}
    for template in templates:
        group = get_deception_level(template["deception_score"])
        if not groups.get(group):
            groups[group] = []
        groups[group].append(template["template_uuid"])
    return groups


def get_deception_level(deception_score: int) -> str:
    """Return group for a template based on deception score.."""
    if deception_score < LEVELS.moderate:
        return "low"
    elif deception_score < LEVELS.high:
        return "moderate"
    else:
        return "high"
