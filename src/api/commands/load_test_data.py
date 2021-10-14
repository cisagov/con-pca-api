"""Load Test Data."""
# Standard Python Libraries
import json
import os

# cisagov Libraries
from api.config import logger
from api.manager import CycleManager, SendingProfileManager, SubscriptionManager

current_dir = os.path.dirname(__file__)

cycle_manager = CycleManager()
sending_profile_manager = SendingProfileManager()
subscription_manager = SubscriptionManager()


def open_json_file(file_name: str):
    """Open json file from path."""
    return open(os.path.join(current_dir, f"data/{file_name}"))


def load_sending_profile():
    """Load sample sending profile."""
    if sending_profile_manager.get(filter_data={"name": "Test Sending Profile"}):
        logger.info("Test data for sending profile already exists.")
        return

    with open_json_file("sending_profile.json") as json_file:
        logger.info("loading sending profile test data...")
        sending_profile_manager.save(json.load(json_file))
