"""Scripts to run when application starts."""
# Standard Python Libraries
import json
import logging

# Third-Party Libraries
from marshmallow.exceptions import ValidationError

# cisagov Libraries
from api.manager import NonHumanManager, RecommendationManager, TemplateManager

recommendation_manager = RecommendationManager()
template_manager = TemplateManager()
nonhuman_manager = NonHumanManager()


def initialize_templates():
    """Create initial templates."""
    try:
        current_templates = template_manager.all()
    except ValidationError:  # TODO: Remove this after templates are initialized properly.
        logging.info("Error validating templates. Resetting.")
        template_manager.delete(params={})
        current_templates = []
    names = [t["name"] for t in current_templates]

    if len(names) > len(set(names)):
        logging.info("Duplicate templates found, reinitializing.")
        template_manager.delete(params={})
        current_templates = []

    if len(current_templates) > 0:
        logging.info("Templates already initialized.")
        return

    logging.info("Initializing templates.")
    with open("static/templates.json", "r") as f:
        templates = json.load(f)
        logging.info(f"Found {len(templates)} to create.")
        for template in templates:
            logging.info(f"Creating template {template['name']}.")
            template_manager.save(template)
    logging.info("Templates initialized")


def initialize_nonhumans():
    """Create initial set of non-human ASN orgs."""
    initial_orgs = ["GOOGLE", "AMAZON-02", "MICROSOFT-CORP-MSN-AS-BLOCK"]

    current_orgs = [o["asn_org"] for o in nonhuman_manager.all()]
    if len(current_orgs) > len(set(current_orgs)):
        logging.info("Duplicate orgs found, reinitializing.")
        nonhuman_manager.delete(params={})
        current_orgs = []

    if len(current_orgs) > 0:
        logging.info("Non humans already initialized")
        return

    logging.info("Initializing nonhumans.")
    for org in initial_orgs:
        logging.info(f"Adding asn org {org}")
        nonhuman_manager.save({"asn_org": org})
    logging.info("ASN Orgs Initialized.")


def initialize_recommendations():
    """Create an initial set of recommendations."""
    current_names = [r["title"] for r in recommendation_manager.all()]
    if len(current_names) > len(set(current_names)):
        logging.info("Duplicate recommendations found, reinitializing.")
        recommendation_manager.delete(params={})
        current_names = []

    if len(current_names) > 0:
        logging.info("Recommendations already initialized")
        return

    with open("static/recommendations.json", "r") as f:
        recommendations = json.load(f)
        logging.info(f"Found {len(recommendations)} to create.")
    recommendation_manager.save_many(recommendations)
    logging.info("Recommendations initialized")
