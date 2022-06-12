"""pytest plugin configuration.

https://docs.pytest.org/en/latest/writing_plugins.html#conftest-py-plugins
"""
# Third-Party Libraries
import pytest
import logging

from api.main import app
from api.commands.load_test_data import load_test_data

import warnings
warnings.filterwarnings("ignore")

logging.getLogger('faker').setLevel(logging.ERROR)

MAIN_SERVICE_NAME = "api"


@pytest.fixture(scope="session")
def main_container(dockerc):
    """Return the main container from the Docker composition."""
    # find the container by name even if it is stopped already
    return dockerc.containers(service_names=[MAIN_SERVICE_NAME], stopped=True)[0]


def pytest_addoption(parser):
    """Add new commandline options to pytest."""
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify collected tests based on custom marks and commandline options."""
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(scope="session")
def client():
    with app.app_context():
        load_test_data()
        with app.test_client() as client:
            yield client


@pytest.fixture()
def subscription():
    with app.app_context():
        from api.manager import SubscriptionManager
        subscription_manager = SubscriptionManager()
        subscriptions = subscription_manager.all()
        return subscriptions[0]


