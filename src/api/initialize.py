"""Scripts to run when application starts."""
# Standard Python Libraries
from datetime import datetime, timedelta
import json
import os

# Third-Party Libraries
from bson.objectid import ObjectId
from pymongo import errors as pymongo_errors
import pytz  # type: ignore
import redis  # type: ignore

# cisagov Libraries
from api.app import app
from api.config.environment import DB, REDIS_HOST, REDIS_PORT, TESTING
from api.manager import (
    CustomerManager,
    CycleManager,
    LandingPageManager,
    LoggingManager,
    NonHumanManager,
    RecommendationManager,
    SendingProfileManager,
    SubscriptionManager,
    TargetManager,
    TemplateManager,
)
from utils.logging import setLogger
from utils.subscriptions import start_subscription, stop_subscription
from utils.templates import select_templates

logger = setLogger(__name__)

customer_manager = CustomerManager()
cycle_manager = CycleManager()
landing_page_manager = LandingPageManager()
logging_manager = LoggingManager()
recommendation_manager = RecommendationManager()
sending_profile_manager = SendingProfileManager()
subscription_manager = SubscriptionManager()
template_manager = TemplateManager()
target_manager = TargetManager()
nonhuman_manager = NonHumanManager()


def _initialize_templates():
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


def _initialize_nonhumans():
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


def _initialize_recommendations():
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


def _populate_stakeholder_shortname():
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


def _reset_processing():
    """Set processing to false for all subscriptions."""
    subscriptions = subscription_manager.all(
        params={"processing": True}, fields=["name", "processing"]
    )
    if not subscriptions:
        logger.info("No subscriptions stuck in the processing state found.")
        return

    for subscription in subscriptions:
        logger.info(
            f"Resetting processing for subscription {subscription.get('name')} to False."
        )
        subscription_manager.update(
            document_id=subscription["_id"],
            data={
                "processing": False,
            },
        )


def _duplicate_oid_fields():
    """For every string id field, create a duplicate which is an objectid."""
    # Subscriptions
    subscriptions = subscription_manager.all(
        fields=[
            "_id",
            "name",
            "customer_id",
            "customer_oid",
            "sending_profile_id",
            "sending_profile_oid",
            "landing_page_id",
            "landing_page_oid",
        ]
    )
    if not subscriptions:
        logger.info("No subscriptions found for oid field duplication.")
        return
    for subscription in subscriptions:
        for id_name in ["customer_id", "sending_profile_id", "landing_page_id"]:
            if id_name in subscription and ObjectId.is_valid(
                subscription.get(id_name, "")
            ):
                oid_name = id_name.replace("_id", "_oid")
                update_data = {}
                if oid_name not in subscription or subscription.get(id_name, "") != str(
                    subscription.get(oid_name, "")
                ):
                    logger.info(
                        f"Updating {oid_name} for subscription {subscription.get('name', '')} to match {subscription.get(id_name, '')}."
                    )
                    update_data[oid_name] = ObjectId(subscription.get(id_name, None))
                subscription_manager.update(
                    document_id=subscription["_id"], data=update_data
                )

    # Cycles
    cycles = cycle_manager.all(
        fields=[
            "_id",
            "name",
            "subscription_id",
            "subscription_oid",
            "template_ids",
            "template_oids",
        ]
    )
    if not cycles:
        logger.info("No cycles found for oid field duplication.")
        return
    for cycle in cycles:
        if "subscription_id" in cycle and ObjectId.is_valid(
            cycle.get("subscription_id", "")
        ):
            if "subscription_oid" not in cycle or cycle.get(
                "subscription_id", ""
            ) != str(cycle.get("subscription_oid", "")):
                logger.info(
                    f"Updating subscription_oid for cycle {cycle.get('_id', '')} to match {cycle.get('subscription_id', '')}."
                )
                cycle_manager.update(
                    document_id=cycle.get("_id", ""),
                    data={
                        "subscription_oid": ObjectId(
                            cycle.get("subscription_id", None)
                        ),
                    },
                )
        if "template_ids" in cycle and all(
            ObjectId.is_valid(template_id)
            for template_id in cycle.get("template_ids", [])
        ):
            if "template_oids" not in cycle or cycle.get("template_ids", "") != [
                str(each) for each in cycle.get("template_oids", "")
            ]:
                logger.info(
                    f"Updating template_oids for cycle {cycle.get('_id', '')} to match {cycle.get('template_ids', [])}."
                )
                template_oids = []
                for id in cycle.get("template_ids", []):
                    template_oids.append(ObjectId(id))
                cycle_manager.update(
                    document_id=cycle["_id"],
                    data={
                        "template_oids": template_oids,
                    },
                )

    # Templates
    templates = template_manager.all(
        fields=[
            "_id",
            "name",
            "sending_profile_id",
            "sending_profile_oid",
            "landing_page_id",
            "landing_page_oid",
        ]
    )
    if not templates:
        logger.info("No templates found for oid field duplication.")
        return
    for template in templates:
        for id_name in ["sending_profile_id", "landing_page_id"]:
            if id_name in template and ObjectId.is_valid(template.get(id_name, "")):
                oid_name = id_name.replace("_id", "_oid")
                update_data = {"name": template.get("name")}
                if oid_name not in template or template.get(id_name, "") != str(
                    template.get(oid_name, "")
                ):
                    logger.info(
                        f"Updating {oid_name} for template {template.get('name', '')} to match {template.get(id_name, '')}."
                    )
                    update_data[oid_name] = ObjectId(template.get(id_name, None))
                    template_manager.update(
                        document_id=template["_id"], data=update_data
                    )


def _restart_logging_ttl_index(ttl_in_seconds=345600):
    """Create the ttl index."""
    try:
        DB.logging.drop_indexes()
    except Exception as e:
        logger.exception(e)
    try:
        DB.logging.create_index("created", expireAfterSeconds=ttl_in_seconds)
    except Exception as e:
        logger.exception(e)


def _reset_dirty_stats():
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


def _restart_subscriptions():
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


def _initialize_db_indexes():
    """Create Mongo DB indexes if missing."""
    managers = (
        ("customers", customer_manager),
        ("cycles", cycle_manager),
        ("landing pages", landing_page_manager),
        ("logging", logging_manager),
        ("recommendations", recommendation_manager),
        ("sending profile", sending_profile_manager),
        ("subscriptions", subscription_manager),
    )
    for name, manager in managers:
        try:
            manager.create_indexes()
            logger.info(f"Creating db index for {name}")
        except pymongo_errors.DuplicateKeyError:
            logger.error(
                f"Creating db index for {name} failed due to duplicate key error."
            )
            continue


def _flush_redis_db():
    """Flush the redis database."""
    if TESTING:
        logger.info("Skipping redis flush in test mode.")
        return
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    logger.info("Flushing redis database.")
    r.flushdb()


def initialization_tasks():
    """Run all initialization tasks."""
    with app.app_context():
        _flush_redis_db()
        _initialize_db_indexes()
        _initialize_nonhumans()
        _reset_dirty_stats()
        _populate_stakeholder_shortname()
