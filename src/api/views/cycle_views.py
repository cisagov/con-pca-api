"""Cycle View."""
from api.serializers.cycle_serializers import CycleEmailReportedListSerializer
from api.services import SubscriptionService
from api.utils.subscription.cycles import (
    delete_reported_emails,
    get_reported_emails,
    override_total_reported,
    update_reported_emails,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

subscription_service = SubscriptionService()


class CycleReportedView(APIView):
    """
    This is the Cycle Email reported View.

    This handles the list of emails reported in each cycle.
    """

    def get(self, request, subscription_uuid):
        """Get Method."""
        subscription = subscription_service.get(subscription_uuid)
        emails_reported_list = get_reported_emails(subscription)

        serializer = CycleEmailReportedListSerializer(emails_reported_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        subscription_service.update(subscription_uuid, data)

        serializer = CycleEmailReportedListSerializer(emails_reported_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
