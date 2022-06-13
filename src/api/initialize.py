"""Scripts to run when application starts."""
# Standard Python Libraries
import json
import logging
import os

# cisagov Libraries
from api.manager import NonHumanManager, RecommendationManager, TemplateManager

recommendation_manager = RecommendationManager()
template_manager = TemplateManager()
nonhuman_manager = NonHumanManager()


def initialize_templates():
    """Create initial templates."""
    current_templates = template_manager.all()
    names = [t["name"] for t in current_templates]

    if len(names) > len(set(names)):
        logging.error("Duplicate templates found, check database.")
        return

    if len(current_templates) > 0:
        logging.info("Templates already initialized.")
        return

    logging.info("Initializing templates.")

    templates_path = os.environ.get("TEMPLATES_PATH", "static/templates.json")
    with open(templates_path, "r") as f:
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
        logging.error("Duplicate orgs found, check database.")
        return

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
    current_names = [f"{r['title']}-{r['type']}" for r in recommendation_manager.all()]
    if len(current_names) > len(set(current_names)):
        logging.error("Duplicate recommendations found, check database.")
        return

    if len(current_names) > 0:
        logging.info("Recommendations already initialized")
        return

    recommendations_path = os.environ.get(
        "RECOMMENDATIONS_PATH", "static/recommendations.json"
    )
    with open(recommendations_path, "r") as f:
        recommendations = json.load(f)
        logging.info(f"Found {len(recommendations)} to create.")
    recommendation_manager.save_many(recommendations)
    logging.info("Recommendations initialized")
