"""Template selector utils."""
# Standard Python Libraries
import random


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
        groups[group].append(template)
    return groups


def group_template(template: dict) -> str:
    """Return group for a template based on deception score.."""
    levels = {"high": 5, "moderate": 3, "low": 0}
    score = template["deception_score"]
    if score < levels["moderate"]:
        return "low"
    elif score < levels["high"]:
        return "moderate"
    else:
        return "high"
