"""Tempalte Selector Util."""
# Standard Python Libraries
import random

# cisagov Libraries
from api.services import TagService, TemplateService
from api.utils.template.personalize import personalize_template

tag_service = TagService()
tempalte_service = TemplateService()


def get_num_templates_per_batch(diversity_level="moderate"):
    """Get_num_templates_per_batch."""
    numbers = {"high": 8, "moderate": 5, "low": 3}
    return numbers.get(diversity_level, 5)


def group_templates(templates):
    """Group Templates by score."""
    template_score_to_level = {"high": 5, "medium": 2, "low": 0}
    template_groups = {"low": [], "medium": [], "high": []}
    for template in templates:
        if template["deception_score"] < template_score_to_level["medium"]:
            template_groups["low"].append(template)
        elif template["deception_score"] < template_score_to_level["high"]:
            template_groups["medium"].append(template)
        else:
            template_groups["high"].append(template)

    return template_groups


def randomize_templates(template_data):
    """Randomize Templates."""
    return random.sample(list(template_data.keys()), len(list(template_data.keys())))


def get_relevant_templates(templates, subscription, template_count: int):
    """Get_relevant_templates."""
    # Values as a minimum
    template_groups = group_templates(templates)

    # formats templates for alogrithm
    template_data_low = {
        t.get("template_uuid"): t.get("descriptive_words")
        for t in template_groups["low"]
    }
    template_data_medium = {
        t.get("template_uuid"): t.get("descriptive_words")
        for t in template_groups["medium"]
    }
    template_data_high = {
        t.get("template_uuid"): t.get("descriptive_words")
        for t in template_groups["high"]
    }

    # gets order of templates ranked from best to worst
    relevant_templates_low = randomize_templates(template_data_low)
    relevant_templates_medium = randomize_templates(template_data_medium)
    relevant_templates_high = randomize_templates(template_data_high)
    relevant_templates = {
        "low": relevant_templates_low,
        "medium": relevant_templates_medium,
        "high": relevant_templates_high,
    }

    return relevant_templates


def batch_templates(templates, num_per_batch, sub_levels: dict):
    """Batch_templates."""
    sub_levels["high"]["template_uuids"] = templates["high"][:num_per_batch]
    sub_levels["moderate"]["template_uuids"] = templates["medium"][:num_per_batch]
    sub_levels["low"]["template_uuids"] = templates["low"][:num_per_batch]

    return sub_levels


def personalize_templates(customer, subscription, templates, sub_levels: dict):
    """Personalize_templates."""
    # Gets list of tags for personalizing
    tags = tag_service.get_list()

    for k in sub_levels.keys():
        # Get actual list of template data
        personalize_list = list(
            filter(
                lambda x: x["template_uuid"] in sub_levels[k]["template_uuids"],
                templates,
            )
        )

        # Send to manager function for personalizing
        personalized_data = personalize_template(
            customer_info=customer,
            template_data=personalize_list,
            sub_data=subscription,
            tag_list=tags,
        )

        # Assign
        sub_levels[k]["personalized_templates"] = personalized_data

    return sub_levels


def personalize_template_batch(customer, subscription, sub_levels: dict):
    """Personalize_template_batch."""
    # Gets list of available email templates
    templates = tempalte_service.get_list({"retired": False})

    # Determines how many templates are available in each batch
    templates_per_batch = get_num_templates_per_batch()

    # Gets needed amount of relevant templates
    relevant_templates = get_relevant_templates(
        templates, subscription, 3 * templates_per_batch
    )

    # Batches templates
    sub_levels = batch_templates(relevant_templates, templates_per_batch, sub_levels)

    # Personalize Templates
    sub_levels = personalize_templates(customer, subscription, templates, sub_levels)

    return sub_levels
