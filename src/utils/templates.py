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
