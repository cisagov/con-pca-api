"""Template utils."""
# Standard Python Libraries
import random


class LEVELS:
    """Deception levels."""

    high = 5
    moderate = 3
    low = 0


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
        groups[group].append(template["_id"])
    return groups


def get_deception_level(deception_score: int) -> str:
    """Return group for a template based on deception score.."""
    if deception_score < LEVELS.moderate:
        return "low"
    elif deception_score < LEVELS.high:
        return "moderate"
    else:
        return "high"


def get_indicators():
    """Get recommendations from db."""
    return {
        "appearance": {
            "grammar": {
                "name": "Grammar",
                "values": {
                    "0": {"label": "Poor"},
                    "1": {"label": "Decent"},
                    "2": {"label": "Proper"},
                },
            },
            "link_domain": {
                "name": "Link/Domain",
                "values": {
                    "0": {"label": "Unrelated"},
                    "1": {"label": "Related/Hidden/Spoofed"},
                },
            },
            "logo_graphics": {
                "name": "Logo/Graphics",
                "values": {
                    "0": {"label": "Plain Text"},
                    "1": {"label": "Visual Appeal"},
                },
            },
        },
        "behavior": {
            "curiosity": {"name": "Curiosity", "values": {"1": {"label": "Yes"}}},
            "duty_obligation": {
                "name": "Duty or Obligation",
                "values": {"1": {"label": "Yes"}},
            },
            "fear": {"name": "Fear", "values": {"1": {"label": "Yes"}}},
            "greed": {"name": "Greed", "values": {"1": {"label": "Yes"}}},
        },
        "relevancy": {
            "organization": {
                "name": "Organization",
                "values": {"0": {"label": "No"}, "1": {"label": "Yes"}},
            },
            "public_news": {
                "name": "Public News",
                "values": {"0": {"label": "No"}, "1": {"label": "Yes"}},
            },
        },
        "sender": {
            "authoritative": {
                "name": "Authoritative",
                "values": {
                    "0": {"label": "None"},
                    "1": {"label": "Peer"},
                    "2": {"label": "Superior"},
                },
            },
            "external": {
                "name": "External",
                "values": {
                    "0": {"label": "Not External/Unpsecified"},
                    "1": {"label": "Specified"},
                },
            },
            "internal": {
                "name": "Internal",
                "values": {
                    "0": {"label": "Not Internal/Unspecified"},
                    "1": {"label": "Generic/Close"},
                    "2": {"label": "Spoofed"},
                },
            },
        },
    }
