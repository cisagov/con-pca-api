import logging

log = logging.getLogger(__name__)


class TestSubscriptions:
    def test_subscriptions_view(self, client):
        resp = client.get('/api/subscriptions/')
        assert resp.status_code == 200

        sub = resp.json[0]
        assert self.check_subscription_properties(sub)

    def test_get_subscription(self, client, subscription):
        sub_id = subscription.get("_id")
        assert sub_id is not None

        resp = client.get(f'/api/subscription/{sub_id}')
        assert resp.status_code == 200

        sub = resp.json
        assert self.check_subscription_properties(sub)

    @staticmethod
    def check_subscription_properties(sub):
        # test some attributes of the subscription object
        if sub.get("name") != "test_subscription":
            return False

        if sub.get("created_by") != "bot":
            return False

        if sub.get("continuous_subscription") is True:
            return False

        if len(sub.get("target_email_list", [])) != 4:
            return False

        return True

