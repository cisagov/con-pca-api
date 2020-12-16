"""Cycle View."""
# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.serializers.cycle_serializers import CycleEmailReportedListSerializer
from api.services import SubscriptionService
from api.utils.subscription.cycles import (
    delete_reported_emails,
    get_reported_emails,
    override_total_reported,
    update_reported_emails,
)

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

        if int(data.get("override_total_reported", -1)) > -1:
            override_total_reported(subscription, data)
        else:
            override_total_reported(subscription, data)
            delete_reported_emails(subscription, data)
            update_reported_emails(subscription, data)

        emails_reported_list = get_reported_emails(subscription)
        serializer = CycleEmailReportedListSerializer(emails_reported_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
