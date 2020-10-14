"""Cycle View."""
from api.serializers.cycle_serializers import (
    CycleEmailReportedListPostSerializer,
    CycleEmailReportedListSerializer,
)
from api.services import SubscriptionService
from api.utils.subscription.cycles import (
    delete_reported_emails,
    get_reported_emails,
    override_total_reported,
    update_reported_emails,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

subscription_service = SubscriptionService()


class CycleReportedView(APIView):
    """
    This is the Cycle Email reported View.

    This handles the list of emails reported in each cycle.
    """

    @swagger_auto_schema(
        responses={"200": CycleEmailReportedListSerializer, "400": "Bad Request"},
        operation_id="Get Reported Emails",
        operation_description="This handles the API for the Get a list of all email reported in a Subscription cycle with subscription_uuid.",
        tags=["CycleEmailReports"],
    )
    def get(self, request, subscription_uuid):
        """Get Method.

        Args:
            request (object): request object
            subscription_uuid (string): subscription_uuid

        Returns:
            object: Django Responce object
        """
        subscription = subscription_service.get(subscription_uuid)
        emails_reported_list = get_reported_emails(subscription)

        serializer = CycleEmailReportedListSerializer(emails_reported_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=CycleEmailReportedListPostSerializer,
        responses={
            "200": CycleEmailReportedListSerializer,
            "400": "Bad Request",
        },
        security=[],
        operation_id="Incoming WebHook from gophish ",
        operation_description=" This handles incoming webhooks from GoPhish Campaigns.",
        tags=["CycleEmailReports"],
    )
    def post(self, request, subscription_uuid):
        """Post method."""
        subscription = subscription_service.get(subscription_uuid)

        data = request.data.copy()
        if "override_total_reported" in data and (
            data["override_total_reported"] is not None
            and data["override_total_reported"] > -1
        ):
            override_total_reported(subscription, data)
        else:
            override_total_reported(subscription, data)
            delete_reported_emails(subscription, data)
            update_reported_emails(subscription, data)

        emails_reported_list = get_reported_emails(subscription)
        updated_response = subscription_service.update(subscription_uuid, data)

        if "errors" in updated_response:
            return Response(updated_response, status=status.HTTP_400_BAD_REQUEST)

        serializer = CycleEmailReportedListSerializer(emails_reported_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
