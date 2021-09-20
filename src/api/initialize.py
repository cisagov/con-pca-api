"""Scripts to run when application starts."""
# Standard Python Libraries
import json
import logging

# cisagov Libraries
from api.manager import TemplateManager

template_manager = TemplateManager()


def initialize_templates():
    """Create initial templates."""
    if len(template_manager.all(fields=["template_uuid"])) > 0:
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
