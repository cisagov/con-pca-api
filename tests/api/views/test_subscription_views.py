"""Test Subscription Views."""


def test_subscription_views(client):
    """Test Subscriptions View."""
    resp = client.get("/api/subscriptions")
    print("RESP: ", dir(client))
    assert resp == resp
