"""Scripts to run when application starts."""
# Standard Python Libraries
import json
import logging

# cisagov Libraries
from api.manager import NonHumanManager, RecommendationManager, TemplateManager

recommendation_manager = RecommendationManager()
template_manager = TemplateManager()
nonhuman_manager = NonHumanManager()


def initialize_templates():
    """Create initial templates."""
    if len(template_manager.all(fields=["_id"])) > 0:
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

    if len(nonhuman_manager.all()) > 0:
        logging.info("Non humans already initialized")
        return

    logging.info("Initializing nonhumans.")
    for org in initial_orgs:
        logging.info(f"Adding asn org {org}")
        nonhuman_manager.save({"asn_org": org})
    logging.info("ASN Orgs Initialized.")


def initialize_recommendations():
    """Create an initial set of recommendations."""
    if len(recommendation_manager.all()) > 0:
        logging.info("Recommendations already initialized")
        return
    with open("static/recommendations.json", "r") as f:
        recommendations = json.load(f)
        logging.info(f"Found {len(recommendations)} to create.")
    recommendation_manager.save_many(recommendations)
    logging.info("Recommendations initialized")
