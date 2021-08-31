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
    },
    "sender": {
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
    },
    "relevancy": {
        "organization": {"name": "Relevancy Orginization", "0": "No", "1": "Yes"},
        "public_news": {"name": "Public News", "0": "No", "1": "Yes"},
    },
    "behavior": {
        "fear": {"name": "Fear", "0": "Yes", "1": "No"},
        "duty_obligation": {"name": "Duty or Obligation", "0": "Yes", "1": "No"},
        "curiosity": {"name": "Curiosity", "0": "Yes", "1": "No"},
        "greed": {"name": "Greed", "0": "Yes", "1": "No"},
    },
}


def select_templates(templates: list, count: int = 5) -> dict:
    """Group Templates by score."""
    grouped_templates = group_templates(templates)
    for k, v in grouped_templates.items():
        sample_size = count if len(v) > count else len(v)
        grouped_templates[k] = random.sample(v, sample_size)
    return grouped_templates


def group_templates(templates):
    """Group all templates by deception score."""
    groups = {}
    for template in templates:
        group = group_template(template)
        if not groups.get(group):
            groups[group] = []
        groups[group].append(template["template_uuid"])
    return groups


def group_template(template: dict) -> str:
    """Return group for a template based on deception score.."""
    score = template["deception_score"]
    if score < LEVELS.moderate:
        return "low"
    elif score < LEVELS.high:
        return "moderate"
    else:
        return "high"
