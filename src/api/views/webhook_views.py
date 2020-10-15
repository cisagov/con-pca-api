"""Webhook View."""
from datetime import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.manager import CampaignManager

from api.serializers import webhook_serializers

from api.utils import webhooks
from api.utils.generic import format_ztime
from api.utils.template.templates import update_target_history
from api.services import SubscriptionService, CampaignService

manager = CampaignManager()
subscription_service = SubscriptionService()
campaign_service = CampaignService()


class IncomingWebhookView(APIView):
    """This is the a IncomingWebhookView."""

    @swagger_auto_schema(
        request_body=webhook_serializers.InboundWebhookSerializer,
        operation_id="Incoming WebHook from gophish ",
    )
    def post(self, request):
        """Post method."""
        data = request.data.copy()
        return self.__handle_webhook_data(data)

    def is_duplicate_timeline_entry(self, timeline, webhook_data):
        """Check if webhook data is already registered in the timeline data."""
        for moment in timeline:
            if (
                moment["message"] == webhook_data["message"]
                and moment["email"] == webhook_data["email"]
            ):
                return True
        return False

    def has_corresponding_opened_event(self, timeline, webhook_data):
        """Check if webhook click response has corresponding opened timeline entry"""
        for moment in timeline:
            if (
                moment["message"] == "Email Opened"
                and moment["email"] == webhook_data["email"]
            ):
                return True
        return False

    def mark_phishing_results_dirty(self, subscription, campaign):
        for cycle in subscription["cycles"]:
            if campaign["campaign_id"] in cycle["campaigns_in_cycle"]:
                cycle["phish_results_dirty"] = True

    def __handle_webhook_data(self, data):
        """
        Handle Webhook Data.

        The Webhook doesnt give us much besides:
        campaign_id = serializers.IntegerField()
        email = serializers.EmailField()
        time = serializers.DateTimeField()
        message = serializers.CharField()
        details = serializers.CharField()

        But using this, we can call the gophish api and update out db on each
        webhook event.
        """
        if "message" in data:
            seralized = webhook_serializers.InboundWebhookSerializer(data)
            seralized_data = seralized.data
            subscription = subscription_service.get_single_subscription_webhook(
                seralized_data["campaign_id"]
            )

            campaign = CampaignService.get_list(
                parameters={"campaign_id": seralized_data["campaign_id"]}
            )[0]

            subscription = SubscriptionService.get(campaign["subscription_uuid"])

            if subscription is None:
                return Response(status=status.HTTP_404_NOT_FOUND)

            campaign_event = seralized_data["message"]
            if campaign_event in [
                "Email Sent",
                "Email Opened",
                "Clicked Link",
                "Submitted Data",
                "Email Reported",
            ]:
                if (
                    subscription["status"] == "Queued"
                    and campaign_event == "Email Sent"
                ):
                    subscription_service.update(
                        subscription["subscription_uuid"], {"status": "In Progress"}
                    )

                # If there is not a corresponding opened event to a link being clicked, create one
                if campaign_event == "Clicked Link":
                    if not webhooks.check_opened_event(
                        campaign["timeline"], seralized_data["email"]
                    ):
                        webhooks.push_webhook(
                            campaign_uuid=campaign["campaign_uuid"],
                            email=seralized_data["email"],
                            message="Email Opened",
                            time=datetime.now(),
                            details=seralized_data["details"],
                        )

                # Add Timeline Data
                webhooks.push_webhook(
                    campaign_uuid=campaign["campaign_uuid"],
                    email=seralized_data["email"],
                    message=seralized_data["message"],
                    time=format_ztime(seralized_data["time"]),
                    details=seralized_data["details"],
                )

                # update campaign to be marked as dirty
                campaign_service.update(
                    campaign["campaign_uuid"], {"phish_results_dirty": True}
                )

                # update cycle to be marked as dirty
                for cycle in subscription["cycles"]:
                    if campaign["campaign_id"] in cycle["campaigns_in_cycle"]:
                        subscription_service.update_nested(
                            uuid=subscription["subscription_uuid"],
                            field="cycles.$.phish_results_dirty",
                            data=True,
                            params={"cycles.cycle_uuid": cycle["cycle_uuid"]},
                        )
                # update target history
                if campaign_event == "Email Sent":
                    # send campaign info and email gophish_campaign_data, seralized_data
                    update_target_history(campaign, seralized_data)

            return Response(status=status.HTTP_202_ACCEPTED)

        return Response(status=status.HTTP_200_OK)
