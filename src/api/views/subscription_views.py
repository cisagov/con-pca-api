"""Subscription Views."""
# Standard Python Libraries
import logging

# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.manager import CampaignManager
from api.services import CampaignService, SubscriptionService
from api.utils.stats import update_phish_results
from api.utils.subscription.actions import (
    create_subscription,
    launch_subscription,
    stop_subscription,
)
from api.utils.subscription.subscriptions import add_remove_continuous_subscription_task
from api.utils.subscription.valid import is_subscription_valid

campaign_manager = CampaignManager()

subscription_service = SubscriptionService()
campaign_service = CampaignService()


class SubscriptionsListView(APIView):
    """SubscriptionsListView."""

    def get(self, request):
        """Get."""
        parameters = {"archived": {"$in": [False, None]}}
        archivedParm = request.GET.get("archived")
        if archivedParm:
            if archivedParm.lower() == "true":
                parameters["archived"] = True

        # Need to get subscriptions using templates from campaign list.
        # If a template is deleted that a subscription historically has used.
        # The subscription stops working in the UI.
        if request.GET.get("template"):
            campaigns = campaign_service.get_list(
                parameters={"template_uuid": request.GET.get("template")}
            )
            parameters["subscription_uuid"] = {
                "$in": [str(c["subscription_uuid"]) for c in campaigns]
            }

        if request.GET.get("dhs_contact"):
            parameters["dhs_contact_uuid"] = request.GET.get("dhs_contact")

        subscription_list = subscription_service.get_list(
            parameters=parameters,
            fields=[
                "subscription_uuid",
                "customer_uuid",
                "name",
                "status",
                "start_date",
                "active",
                "archived",
                "lub_timestamp",
                "primary_contact",
                "dhs_contact_uuid",
            ],
        )
        return Response(subscription_list)

    def post(self, request, format=None):
        """Post."""
        resp = create_subscription(request.data.copy())
        return Response(resp, status=status.HTTP_201_CREATED)


class SubscriptionView(APIView):
    """SubscriptionsView."""

    def get(self, request, subscription_uuid):
        """Get."""
        subscription = subscription_service.get(subscription_uuid)
        if subscription is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        update_phish_results(subscription)
        return Response(subscription)

    def patch(self, request, subscription_uuid):
        """Patch."""
        put_data = request.data.copy()
        # Don't add task if tasks dont exist. This means the subscription is already stopped.
        subscription = subscription_service.get(subscription_uuid, fields=["tasks"])
        if "continuous_subscription" in put_data and subscription.get("tasks"):
            add_remove_continuous_subscription_task(
                subscription_uuid,
                subscription["tasks"],
                put_data["continuous_subscription"],
            )
        updated_response = subscription_service.update(subscription_uuid, put_data)
        return Response(updated_response, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, subscription_uuid):
        """Delete."""
        subscription = subscription_service.get(subscription_uuid)
        if subscription["status"] != "stopped":
            try:
                # Stop subscription
                stop_subscription(subscription)
            except Exception as e:
                logging.exception(e)

        # Delete Campaigns
        campaigns = campaign_service.get_list({"subscription_uuid": subscription_uuid})
        for campaign in campaigns:
            campaign_service.delete(str(campaign["campaign_uuid"]))

        # Delete Subscription
        delete_response = subscription_service.delete(subscription_uuid)

        return Response(delete_response, status=status.HTTP_200_OK)


class SubscriptionsCustomerListView(APIView):
    """SubscriptionsCustomerListView."""

    def get(self, request, customer_uuid):
        """Get."""
        parameters = {"customer_uuid": customer_uuid, "archived": False}
        subscription_list = subscription_service.get_list(parameters)
        return Response(subscription_list)

    def post(self, request, customer_uuid):
        """Post."""
        search_data = request.data.copy()
        cust_arch = {"customer_uuid": customer_uuid, "archived": False}
        parameters = {**search_data, **cust_arch}
        subscription_list = subscription_service.get_list(parameters)
        return Response(subscription_list)


class SubscriptionsTemplateListView(APIView):
    """SubscriptionsTemplateListView."""

    def get(self, request, template_uuid):
        """Get."""
        parameters = {"templates_selected_uuid_list": template_uuid, "archived": False}
        subscription_list = subscription_service.get_list(parameters)
        return Response(subscription_list)


class SubscriptionStopView(APIView):
    """SubscriptionStopView."""

    def get(self, request, subscription_uuid):
        """Get."""
        subscription = subscription_service.get(subscription_uuid)
        resp = stop_subscription(subscription)
        return Response(resp, status=status.HTTP_202_ACCEPTED)


class SubscriptionRestartView(APIView):
    """SubscriptionRestartView."""

    def get(self, request, subscription_uuid):
        """Get."""
        created_response = launch_subscription(subscription_uuid)
        return Response(created_response, status=status.HTTP_202_ACCEPTED)


class SubscriptionTargetCacheView(APIView):
    """SubscriptionTargetCacheView."""

    def post(self, request, subscription_uuid):
        """Post."""
        target_update_data = request.data.copy()

        resp = subscription_service.update(
            subscription_uuid, {"target_email_list_cached_copy": target_update_data}
        )

        return Response(resp, status=status.HTTP_202_ACCEPTED)


class SubscriptionValidView(APIView):
    """SubscriptionValidView."""

    def post(self, request):
        """Post."""
        data = request.data.copy()
        is_valid, message = is_subscription_valid(
            data["target_count"], data["cycle_minutes"]
        )
        if is_valid:
            return Response("Subscription is valid", status=status.HTTP_200_OK)
        else:
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
