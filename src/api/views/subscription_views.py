"""
Subscription Views.

This handles the api for all the Subscription urls.
"""
# Standard Python Libraries
import logging

# Third-Party Libraries
# Local Libraries
from api.manager import CampaignManager, TemplateManager
from api.serializers.subscriptions_serializers import (
    SubscriptionPatchSerializer,
    SubscriptionPostSerializer,
)
from api.services import SubscriptionService, CampaignService
from api.utils.subscription.actions import start_subscription, stop_subscription
from reports.utils import update_phish_results
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# GoPhish API Manager
campaign_manager = CampaignManager()
# Template Calculator Manager
template_manager = TemplateManager()

subscription_service = SubscriptionService()
campaign_service = CampaignService()


class SubscriptionsListView(APIView):
    """
    This is the SubscriptionsListView APIView.

    This handles the API to get a List of Subscriptions.
    """

    @swagger_auto_schema(operation_id="List of Subscriptions")
    def get(self, request):
        """Get method."""
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
            parameters[
                {
                    "subscription_uuid": {
                        "$in": [c["subscription_uuid"] for c in campaigns]
                    }
                }
            ]

        if request.GET.get("dhs_contact"):
            parameters["dhs_contact_uuid"] = request.GET.get("dhs_contact")

        subscription_list = subscription_service.get_list(parameters)
        return Response(subscription_list)

    @swagger_auto_schema(
        request_body=SubscriptionPostSerializer,
        operation_id="Create Subscription",
    )
    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()
        created_response = start_subscription(data=post_data)
        return Response(created_response, status=status.HTTP_201_CREATED)


class SubscriptionView(APIView):
    """SubscriptionsView."""

    @swagger_auto_schema(operation_id="Get single Subscription")
    def get(self, request, subscription_uuid):
        """Get method."""
        subscription = subscription_service.get(subscription_uuid)
        if subscription is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        update_phish_results(subscription)
        return Response(subscription)

    @swagger_auto_schema(
        request_body=SubscriptionPatchSerializer,
        operation_id="Update and Patch single subscription",
    )
    def patch(self, request, subscription_uuid):
        """Patch method."""
        put_data = request.data.copy()
        updated_response = subscription_service.update(subscription_uuid, put_data)
        return Response(updated_response, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(operation_id="Delete single subscription")
    def delete(self, request, subscription_uuid):
        """Delete method."""
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
            campaign_service.delete(campaign["campaign_uuid"])

        # Delete Subscription
        delete_response = subscription_service.delete(subscription_uuid)

        return Response(delete_response, status=status.HTTP_200_OK)


class SubscriptionsCustomerListView(APIView):
    """SubscriptionsCustomerListView."""

    @swagger_auto_schema(operation_id="Get list of Subscriptions via customer_uuid")
    def get(self, request, customer_uuid):
        """Get method."""
        parameters = {"customer_uuid": customer_uuid, "archived": False}
        subscription_list = subscription_service.get_list(parameters)
        return Response(subscription_list)

    @swagger_auto_schema(
        request_body=SubscriptionPostSerializer,
        operation_id="Get list of Subs with customer id and primary contact via customer_uuid",
    )
    def post(self, request, customer_uuid):
        """Post method."""
        search_data = request.data.copy()
        cust_arch = {"customer_uuid": customer_uuid, "archived": False}
        parameters = {**search_data, **cust_arch}
        subscription_list = subscription_service.get_list(parameters)
        return Response(subscription_list)


class SubscriptionsTemplateListView(APIView):
    """SubscriptionsTemplateListView."""

    @swagger_auto_schema(operation_id="Get list of subscriptions via template_uuid")
    def get(self, request, template_uuid):
        """Get method."""
        parameters = {"templates_selected_uuid_list": template_uuid, "archived": False}
        subscription_list = subscription_service.get_list(parameters)
        return Response(subscription_list)


class SubscriptionStopView(APIView):
    """SubscriptionStopView."""

    @swagger_auto_schema(operation_id="Endpoint for manually stopping a subscription")
    def get(self, request, subscription_uuid):
        """Get method."""
        subscription = subscription_service.get(subscription_uuid)
        resp = stop_subscription(subscription)
        return Response(resp, status=status.HTTP_202_ACCEPTED)


class SubscriptionRestartView(APIView):
    """SubscriptionRestartView."""

    @swagger_auto_schema(operation_id="Restart Subscription")
    def get(self, request, subscription_uuid):
        created_response = start_subscription(subscription_uuid=subscription_uuid)
        return Response(created_response, status=status.HTTP_202_ACCEPTED)


class SubscriptionTargetCacheView(APIView):
    """SubscriptionTargetCacheView."""

    @swagger_auto_schema(
        request_body=SubscriptionPostSerializer,
        operation_id="update the subscription target cache",
    )
    def post(self, request, subscription_uuid):
        """
        If the campaign is currently running then save the target cache but leave the
        template_target alone.
        else
            copy the target_cache
        """
        target_update_data = request.data.copy()

        resp = subscription_service.update(
            subscription_uuid, {"target_email_list_cached_copy": target_update_data}
        )

        return Response(resp, status=status.HTTP_202_ACCEPTED)
