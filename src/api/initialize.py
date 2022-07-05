"""Scripts to run when application starts."""
# Standard Python Libraries
import json
import os

# cisagov Libraries
from api.manager import NonHumanManager, RecommendationManager, TemplateManager
from utils.logging import setLogger

logger = setLogger(__name__)

recommendation_manager = RecommendationManager()
template_manager = TemplateManager()
nonhuman_manager = NonHumanManager()


def initialize_templates():
    """Create initial templates."""
    current_templates = template_manager.all()
    names = [t["name"] for t in current_templates]

    if len(names) > len(set(names)):
        logger.error("Duplicate templates found, check database.")
        return

    if len(current_templates) > 0:
        logger.info("Templates already initialized.")
        return

    logger.info("Initializing templates.")

    templates_path = os.environ.get("TEMPLATES_PATH", "static/templates.json")
    with open(templates_path, "r") as f:
        templates = json.load(f)
        logger.info(f"Found {len(templates)} to create.")
        for template in templates:
            logger.info(f"Creating template {template['name']}.")
            template_manager.save(template)
    logger.info("Templates initialized")


def initialize_nonhumans():
    """Create initial set of non-human ASN orgs."""
    initial_orgs = ["GOOGLE", "AMAZON-02", "MICROSOFT-CORP-MSN-AS-BLOCK"]

    current_orgs = [o["asn_org"] for o in nonhuman_manager.all()]
    if len(current_orgs) > len(set(current_orgs)):
        logger.error("Duplicate orgs found, check database.")
        return

    if len(current_orgs) > 0:
        logger.info("Non humans already initialized")
        return

    logger.info("Initializing nonhumans.")
    for org in initial_orgs:
        logger.info(f"Adding asn org {org}")
        nonhuman_manager.save({"asn_org": org})
    logger.info("ASN Orgs Initialized.")


def initialize_recommendations():
    """Create an initial set of recommendations."""
    current_names = [f"{r['title']}-{r['type']}" for r in recommendation_manager.all()]
    if len(current_names) > len(set(current_names)):
        logger.error("Duplicate recommendations found, check database.")
        return

    if len(current_names) > 0:
        logger.info("Recommendations already initialized")
        return

    recommendations_path = os.environ.get(
        "RECOMMENDATIONS_PATH", "static/recommendations.json"
    )
    with open(recommendations_path, "r") as f:
        recommendations = json.load(f)
        logger.info(f"Found {len(recommendations)} to create.")
    recommendation_manager.save_many(recommendations)
    logger.info("Recommendations initialized")
