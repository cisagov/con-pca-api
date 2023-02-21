#!/usr/bin/env pytest -vs
"""Tests for example container."""

# Standard Python Libraries
import time

# import requests  # type: ignore

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
    for _ in range(TIMEOUT):
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
    time.sleep(5)
    assert main_container.is_running is True
    assert main_container.is_restarting is False
    assert main_container.exit_code == 0

    # for url in {"http://localhost:8000", "http://localhost:5000"}:
    #     for i in range(TIMEOUT):
    #         try:
    #             resp = requests.get(url)
    #             assert resp.status_code == 200
    #             assert "Con-PCA" in resp.text
    #             break
    #         except requests.exceptions.ConnectionError as e:
    #             time.sleep(0.5)
    #             if i == TIMEOUT - 1:
    #                 raise Exception(f"Container port {url.split(':')[2]} error: {e}")

    # Make a request against templates to see if they were initialized properly
    # resp = requests.get("http://localhost:5000/api/templates/")
    # templates = resp.json()
    # template_names = [t["name"] for t in templates]
    # assert len(template_names) == len(set(template_names))
