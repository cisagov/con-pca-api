"""
Template Views.

This handles the api for all the Template urls.
"""
from api.manager import CampaignManager
from api.serializers.template_serializers import (
    TemplateQuerySerializer,
    TemplateStopResponseSerializer,
)
from api.services import TemplateService, SubscriptionService
from api.utils.subscription.actions import stop_subscription
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

campaign_manager = CampaignManager()

template_service = TemplateService()
subscription_service = SubscriptionService()


class TemplatesListView(APIView):
    """This is the TemplatesListView."""

    def get(self, request):
        """Get method."""
        serializer = TemplateQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()
        template_list = template_service.get_list(parameters)
        return Response(template_list, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()
        if template_service.exists({"name": post_data["name"]}):
            return Response(
                {"error": "Template with name already exists"},
                status=status.HTTP_409_CONFLICT,
            )

        created_response = template_service.save(post_data)
        return Response(created_response, status=status.HTTP_201_CREATED)


class TemplateView(APIView):
    """TemplateView."""

    def get(self, request, template_uuid):
        """Get method."""
        template = template_service.get(template_uuid)
        return Response(template)

    def patch(self, request, template_uuid):
        """Patch method."""
        put_data = request.data.copy()
        if put_data["landing_page_uuid"] == "0" or not put_data["landing_page_uuid"]:
            put_data["landing_page_uuid"] = None
        updated_response = template_service.update(template_uuid, put_data)
        return Response(updated_response, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, template_uuid):
        """Delete method."""
        delete_response = template_service.delete(template_uuid)
        return Response(delete_response, status=status.HTTP_200_OK)


class TemplateStopView(APIView):
    """TemplateStopView."""

    def get(self, request, template_uuid):
        """Get method."""
        # get subscriptions
        parameters = {"templates_selected_uuid_list": template_uuid}
        subscriptions = subscription_service.get_list(parameters)

        # Stop subscriptions
        updated_subscriptions = list(map(stop_subscription, subscriptions))

        # Get template
        template = template_service.get(template_uuid)

        # Update template
        template["retired"] = True
        template["retired_description"] = "Manually Stopped"
        template_service.update(template_uuid, template)

        # Generate and return response
        resp = {"template": template, "subscriptions": updated_subscriptions}
        serializer = TemplateStopResponseSerializer(resp)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
