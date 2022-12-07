"""Scripts to run when application starts."""
# Standard Python Libraries
from datetime import datetime, timedelta
import json
import os

# Third-Party Libraries
import pytz  # type: ignore

# cisagov Libraries
from api.manager import (
    CustomerManager,
    CycleManager,
    NonHumanManager,
    RecommendationManager,
    SubscriptionManager,
    TemplateManager,
)
from utils.logging import setLogger
from utils.subscriptions import start_subscription, stop_subscription
from utils.templates import select_templates

logger = setLogger(__name__)

customer_manager = CustomerManager()
cycle_manager = CycleManager()
recommendation_manager = RecommendationManager()
subscription_manager = SubscriptionManager()
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
    with open(templates_path) as f:
        templates = json.load(f)
        logger.info(f"Found {len(templates)} to create.")
        for template in templates:
            logger.info(f"Creating template {template['name']}.")
            template_manager.save(template)
    logger.info("Templates initialized")


def initialize_nonhumans():
    """Create initial set of non-human ASN orgs."""
    initial_orgs = [
        "MICROSOFT-CORP-MSN-AS-BLOCK",
        "CLOUDFLARENET",
        "DIGITALOCEAN-ASN",
        "AMAZON-AES",
        "GOOGLE",
        "OVH SAS",
        "AMAZON-02",
        "AS-CHOOPA",
        "OPENDNS",
        "PAN0001",
        "HostRoyale Technologies Pvt Ltd",
        "Green Floid LLC",
        "GOOGLE-CLOUD-PLATFORM",
    ]

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
    with open(recommendations_path) as f:
        recommendations = json.load(f)
        logger.info(f"Found {len(recommendations)} to create.")
    recommendation_manager.save_many(recommendations)
    logger.info("Recommendations initialized")


def populate_stakeholder_shortname():
    """Populate the stakeholder_shortname field with the same name as customer_identifier if empty."""
    customers = customer_manager.all(
        fields=["_id", "name", "identifier", "stakeholder_shortname"]
    )
    for customer in customers:
        if not customer.get("stakeholder_shortname"):
            customer_manager.update(
                document_id=customer["_id"],
                data={
                    "name": customer["name"],
                    "stakeholder_shortname": customer["identifier"],
                },
            )


def reset_dirty_stats():
    """Reset the dirty_stats field to true whenever the app is initialized."""
    cycles = cycle_manager.all(
        fields=["_id", "name", "identifier", "stakeholder_shortname"]
    )
    for cycle in cycles:
        cycle_manager.update(
            document_id=cycle["_id"],
            data={
                "dirty_stats": True,
            },
        )


def restart_subscriptions():
    """
    Restart all overdue continuous Subscriptions.

    Note: This is a temporary solution and will be removed soon.
    """
    subscriptions = subscription_manager.all(
        params={
            "status": {"$in": ["running"]},
            "continuous_subscription": True,
        },
    )
    cycles = cycle_manager.all(fields=["subscription_id", "end_date", "active"])

    if not subscriptions:
        logger.info("No subscriptions to needed restart.")
        return

    for subscription in subscriptions:
        cycles = cycle_manager.all(params={"subscription_id": subscription["_id"]})
        # get the most recent cycle
        end_date = sorted(
            cycles,
            key=lambda x: x["start_date"]
            + timedelta(
                minutes=(
                    subscription.get("cycle_length_minutes", 0)
                    + subscription.get("cooldown_minutes", 0)
                    + subscription.get("buffer_time_minutes", 0)
                )
            ),
            reverse=True,
        )[0]["end_date"]

        now = pytz.utc.localize(datetime.now())

        if not end_date <= now:
            logger.info(f"{subscription['name']} are not overdue.")
        else:
            logger.info(f"Restarting subscription {subscription['name']}.")
            stop_subscription(subscription["_id"])
            # randomize templates between cycles
            templates = [
                t
                for t in template_manager.all({"retired": False})
                if t not in subscription["templates_selected"]
            ]
            templates_selected = sum(select_templates(templates), [])
            start_subscription(
                str(subscription["_id"]), templates_selected=templates_selected
            )
