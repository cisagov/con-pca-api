"""Target Util."""
# Standard Python Libraries
import random

# cisagov Libraries
from api.services import TargetHistoryService

target_history_service = TargetHistoryService()


def batch_targets(subscription, sub_levels: dict):
    """Batch targets."""
    targets = random.sample(
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


def get_target_available_templates(email, history, templates):
    """Get avaiable template uuids."""
    # Check history of target
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
    """Assign Targets."""
    target_emails = [target["email"] for target in sub_level["targets"]]
    target_history = target_history_service.get_list({"email": {"$in": target_emails}})

    for target in sub_level["targets"]:
        history = list(filter(lambda x: x["email"] == target["email"], target_history))
        available_templates = get_target_available_templates(
            target["email"], history, sub_level["template_uuids"]
        )

        # Ignore this bandit error, not used for security/cryptography purposes.
        # https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b311-random
        selected_template = random.choice(available_templates)  # nosec

        if not sub_level["template_targets"].get(selected_template):
            sub_level["template_targets"][selected_template] = []

        sub_level["template_targets"][selected_template].append(target)
