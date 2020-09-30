"""Target Util."""
# Third-Party Libraries
from api.models.template_models import TargetHistoryModel, validate_history
from api.utils import db_utils as db
import random


def batch_targets(subscription, sub_levels: dict):
    """Batch targets.

    Args:
        subscription (dict): subscription dict
        sub_levels (dict): sub_levels dict

    Returns:
        dict: updated sub_levels
    """
    targets = random.shuffle(
        subscription["target_email_list"], len(subscription["target_email_list"])
    )
    avg = len(targets) / float(3)

    batches = []
    last = 0.0
    while last < len(targets):
        batches.append(targets[int(last) : int(last + avg)])
        last += avg

    # if less than one target, the final targets will be in the last batches
    # when single targets they should be put in high group
    sub_levels["low"]["targets"] = batches[0]
    sub_levels["moderate"]["targets"] = batches[1]
    sub_levels["high"]["targets"] = batches[2]


def get_target_available_templates(email, templates):
    """Returns a list of avaiable template uuids."""
    # Check history of target
    history = db.get_list(
        {"email": email}, "target", TargetHistoryModel, validate_history
    )

    # If no history, return all templates
    if not history:
        return templates

    # Compile list of sent uuids
    sent_uuids = [x["template_uuid"] for x in history[0].get("history_list", [])]

    # Find available templates
    available_templates = list(set(templates) - set(sent_uuids))

    # If no available templates, return all back
    if not available_templates:
        return templates

    # Return available templates
    return available_templates


def assign_targets(sub_level):
    """Assign Targets.

    Args:
        sub_level (dict): sub_level

    Returns:
        dict: updated sub_level
    """
    for target in sub_level["targets"]:
        available_templates = get_target_available_templates(
            target["email"], sub_level["template_uuids"]
        )
        randomized_templates = random.sample(
            available_templates, len(available_templates)
        )
        print(randomized_templates)
        selected_template = randomized_templates[0]
        if not sub_level["template_targets"].get(selected_template):
            sub_level["template_targets"][selected_template] = []

        sub_level["template_targets"][selected_template].append(target)
