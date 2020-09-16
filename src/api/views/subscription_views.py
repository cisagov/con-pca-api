"""
Subscription Views.

This handles the api for all the Subscription urls.
"""
# Standard Python Libraries
import logging

# Third-Party Libraries
# Local Libraries
from api.manager import CampaignManager, TemplateManager
from api.models.subscription_models import SubscriptionModel, validate_subscription
from api.serializers.subscriptions_serializers import (
    SubscriptionDeleteResponseSerializer,
    SubscriptionGetSerializer,
    SubscriptionPatchResponseSerializer,
    SubscriptionPatchSerializer,
    SubscriptionPostResponseSerializer,
    SubscriptionPostSerializer,
)
from api.utils.db_utils import (
    delete_single,
    get_list,
    get_single,
    update_single,
)
from api.utils.subscription.actions import start_subscription, stop_subscription
from reports.utils import update_phish_results
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)
# GoPhish API Manager
campaign_manager = CampaignManager()
# Template Calculator Manager
template_manager = TemplateManager()


class SubscriptionsListView(APIView):
    """
    This is the SubscriptionsListView APIView.

    This handles the API to get a List of Subscriptions.
    """

    @swagger_auto_schema(
        responses={"200": SubscriptionGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="List of Subscriptions",
        operation_description="This handles the API to get a List of Subscriptions.",
        manual_parameters=[
            openapi.Parameter(
                "archived",
                openapi.IN_QUERY,
                description="Show archived subscriptions",
                type=openapi.TYPE_BOOLEAN,
                default=False,
            ),
            openapi.Parameter(
                "template",
                openapi.IN_QUERY,
                description="Show only subscriptions that are using a template",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def get(self, request):
        """Get method."""
        parameters = {"archived": {"$in": [False, None]}}
        archivedParm = request.GET.get("archived")
        if archivedParm:
            if archivedParm.lower() == "true":
                parameters["archived"] = True

        if request.GET.get("template"):
            parameters["templates_selected_uuid_list"] = request.GET.get("template")

        if request.GET.get("dhs_contact"):
            parameters["dhs_contact_uuid"] = request.GET.get("dhs_contact")

        subscription_list = get_list(
            parameters, "subscription", SubscriptionModel, validate_subscription
        )

        serializer = SubscriptionGetSerializer(subscription_list, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=SubscriptionPostSerializer,
        responses={"201": SubscriptionPostResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Create Subscription",
        operation_description="This handles Creating a Subscription and launching a Campaign.",
    )
    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()

        created_response = start_subscription(data=post_data)

        if "errors" in created_response:
            return Response(created_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscriptionPostResponseSerializer(created_response)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubscriptionView(APIView):
    """
    This is the SubscriptionsView APIView.

    This handles the API for the Get a Substription with subscription_uuid.
    """

    @swagger_auto_schema(
        responses={"200": SubscriptionGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get single Subscription",
        operation_description="This handles the API for the Get a Subscription with subscription_uuid.",
    )
    def get(self, request, subscription_uuid):
        """Get method."""
        subscription = get_single(
            subscription_uuid, "subscription", SubscriptionModel, validate_subscription
        )
        if subscription is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        update_phish_results(subscription)
        serializer = SubscriptionGetSerializer(subscription)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=SubscriptionPatchSerializer,
        responses={"202": SubscriptionPatchResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Update and Patch single subscription",
        operation_description="This handles the API for the Update subscription with subscription_uuid.",
    )
    def patch(self, request, subscription_uuid):
        """Patch method."""
        logger.debug("update subscription_uuid {}".format(subscription_uuid))
        put_data = request.data.copy()
        serialized_data = SubscriptionPatchSerializer(put_data)
        updated_response = update_single(
            uuid=subscription_uuid,
            put_data=serialized_data.data,
            collection="subscription",
            model=SubscriptionModel,
            validation_model=validate_subscription,
        )
        if "errors" in updated_response:
            return Response(updated_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscriptionPatchResponseSerializer(updated_response)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        responses={"200": SubscriptionDeleteResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Delete single subscription",
        operation_description="This handles the API for the Delete of a  subscription with subscription_uuid.",
    )
    def delete(self, request, subscription_uuid):
        """Delete method."""
        logger.debug("delete subscription_uuid {}".format(subscription_uuid))

        subscription = get_single(
            uuid=subscription_uuid,
            collection="subscription",
            model=SubscriptionModel,
            validation_model=validate_subscription,
        )
        if subscription["status"] != "stopped":
            try:
                # Stop subscription
                stop_subscription(subscription)
            except Exception as error:
                logger.debug("error stopping subscription: {}".format(error))

        # Delete Subscription
        delete_response = delete_single(
            uuid=subscription_uuid,
            collection="subscription",
            model=SubscriptionModel,
            validation_model=validate_subscription,
        )

        if "errors" in delete_response:
            return Response(delete_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscriptionDeleteResponseSerializer(delete_response)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionsCustomerListView(APIView):
    """
    This is the SubscriptionsCustomerListView APIView.

    This handles the API to get a List of Subscriptions with customer_uuid.
    """

    @swagger_auto_schema(
        responses={"200": SubscriptionGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get list of Subscriptions via customer_uuid",
        operation_description="This handles the API for the Get a Substription with customer_uuid.",
    )
    def get(self, request, customer_uuid):
        """Get method."""
        parameters = {"customer_uuid": customer_uuid, "archived": False}
        subscription_list = get_list(
            parameters, "subscription", SubscriptionModel, validate_subscription
        )
        serializer = SubscriptionGetSerializer(subscription_list, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=SubscriptionPostSerializer,
        responses={"200": SubscriptionGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get list of Subs with customer id and primary contact via customer_uuid",
        operation_description="This handles the API for the Get a Substription with customer_uuid and primary contact.",
    )
    def post(self, request, customer_uuid):
        """Post method."""
        search_data = request.data.copy()
        cust_arch = {"customer_uuid": customer_uuid, "archived": False}
        parameters = {**search_data, **cust_arch}
        subscription_list = get_list(
            parameters, "subscription", SubscriptionModel, validate_subscription
        )
        serializer = SubscriptionGetSerializer(subscription_list, many=True)
        return Response(serializer.data)


class SubscriptionsTemplateListView(APIView):
    """
    This is the SubscriptionsTemplateListView APIView.

    This handles the API to get a list of subscriptions by template_uuid
    """

    @swagger_auto_schema(
        responses={"200": SubscriptionGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get list of subscriptions via template_uuid",
        operation_description="This handles the API fro the get a subscription with template_uuid",
    )
    def get(self, request, template_uuid):
        """Get method."""
        parameters = {"templates_selected_uuid_list": template_uuid, "archived": False}
        subscription_list = get_list(
            parameters, "subscription", SubscriptionModel, validate_subscription
        )
        serializer = SubscriptionGetSerializer(subscription_list, many=True)
        return Response(serializer.data)


class SubscriptionStopView(APIView):
    """
    This is the SubscriptionStopView APIView.
    This handles the API to stop a Subscription using subscription_uuid.
    """

    @swagger_auto_schema(
        responses={"202": SubscriptionPatchResponseSerializer, "400": "Bad Request"},
        operation_id="Endpoint for manually stopping a subscription",
        operation_description="Endpoint for manually stopping a subscription",
    )
    def get(self, request, subscription_uuid):
        """Get method."""
        # get subscription
        subscription = get_single(
            subscription_uuid, "subscription", SubscriptionModel, validate_subscription
        )

        # Stop subscription
        resp = stop_subscription(subscription)

        # Return updated subscriptions
        serializer = SubscriptionPatchResponseSerializer(resp)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class SubscriptionRestartView(APIView):
    """
    This is the SubscriptionRestartView APIView.
    This handles the API to restart a Subscription
    """

    @swagger_auto_schema(
        responses={"201": SubscriptionPatchResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Restart Subscription",
        operation_description="Endpoint for manually restart a subscription",
    )
    def get(self, request, subscription_uuid):
        """
        Get Method for Restart Subscription.
        Args:
            request (object): http request object
            subscription_uuid (string): subscription_uuid string
        Returns:
            object: http Response object.
        """
        created_response = start_subscription(subscription_uuid=subscription_uuid)
        # Return updated subscription
        serializer = SubscriptionPatchResponseSerializer(created_response)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class SubscriptionTargetCacheView(APIView):
    """
    """

    @swagger_auto_schema(
        request_body=SubscriptionPostSerializer,
        responses={"200": SubscriptionGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="update the subscription target cache",
        operation_description="zThis handles the API for the update target cache",
    )
    def post(self, request, subscription_uuid):
        """
        If the campaign is currently running then save the target cache but leave the
        template_target alone.
        else
            copy the target_cache
        """
        logger.debug(
            "update subscription_uuid target cache {}".format(subscription_uuid)
        )
        target_update_data = request.data.copy()

        resp = update_single(
            uuid=subscription_uuid,
            put_data={"target_email_list_cached_copy": target_update_data},
            collection="subscription",
            model=SubscriptionModel,
            validation_model=validate_subscription,
        )

        if "errors" in resp:
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)

        serializer = SubscriptionPatchResponseSerializer(resp)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
