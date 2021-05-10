"""Template selector utils."""
# Standard Python Libraries
import itertools
import random


def select_templates(templates: list, count: int = 5) -> dict:
    """Group Templates by score."""
    result = {}
    for k, g in itertools.groupby(templates, group_template):
        selected = list(g)
        sample_size = count if len(selected) > count else len(selected)
        result[k] = random.sample(selected, sample_size)
    return result


def group_template(template: dict) -> str:
    """Return group for a template."""
    levels = {"high": 5, "moderate": 3, "low": 0}
    score = template["deception_score"]
    if score < levels["moderate"]:
        return "low"
    elif score < levels["high"]:
        return "moderate"
    else:
        return "high"
