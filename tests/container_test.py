#!/usr/bin/env pytest -vs
"""Tests for example container."""

# Standard Python Libraries
import time

# Third-Party Libraries
import requests

READY_MESSAGE = "Starting Con-PCA API"


def test_container_count(dockerc):
    """Verify the test composition and container."""
    # stopped parameter allows non-running containers in results
    assert (
        len(dockerc.containers(stopped=True)) == 3
    ), "Wrong number of containers were started."


def test_wait_for_ready(main_container):
    """Wait for container to be ready."""
    TIMEOUT = 10
    for i in range(TIMEOUT):
        if READY_MESSAGE in main_container.logs().decode("utf-8"):
            break
        time.sleep(1)
    else:
        raise Exception(
            f"Container does not seem ready.  "
            f'Expected "{READY_MESSAGE}" in the log within {TIMEOUT} seconds.'
        )

    # After container is ready, give it some time and make sure
    # it's still running.
    time.sleep(10)
    assert main_container.is_running is True
    assert main_container.is_restarting is False
    assert main_container.exit_code == 0

    # Make a request against the base url on the container
    resp = requests.get("http://localhost:8000")
    assert resp.status_code == 200
    assert "Con-PCA" in resp.text
