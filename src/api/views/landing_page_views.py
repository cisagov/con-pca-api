"""
Landing Page Views

This handles the api for all the landing Page URLS
"""
# Third-Party Libraries
from api.manager import CampaignManager
from api.serializers.landing_page_serializers import (
    LandingPagePatchSerializer,
    LandingPagePostSerializer,
    LandingPageQuerySerializer,
    LandingPageStopResponseSerializer,
)
from api.utils.subscription.actions import stop_subscription
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.services import SubscriptionService, LandingPageService

campaign_manager = CampaignManager()

subscription_service = SubscriptionService()
landing_page_service = LandingPageService()


class LandingPagesListView(APIView):
    """LandingPagesListView"""

    @swagger_auto_schema(
        query_serializer=LandingPageQuerySerializer,
        operation_id="List of LandingPages",
    )
    def get(self, request):
        """Get method."""
        serializer = LandingPageQuerySerializer(request.GET.dict())
        parameters = serializer.data

        with_default = False
        if request.query_params:
            if request.query_params["with_default"]:
                with_default = True

        if not parameters:
            parameters = request.data.copy()

        parameters.pop("is_default_template")
        landing_page_list = landing_page_service.get_list(parameters)

        for landing_page in landing_page_list:
            if landing_page["is_default_template"]:
                default_landing_page = landing_page.copy()
                default_landing_page["name"] = (
                    "(System Default)" + default_landing_page["name"]
                )
                default_landing_page["landing_page_uuid"] = 0

                if with_default:
                    landing_page_list.append(default_landing_page)
                break

        return Response(landing_page_list, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=LandingPagePostSerializer,
        operation_id="Create LandingPage",
    )
    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()
        if landing_page_service.exists({"name": post_data["name"]}):
            return Response(
                {"error": "LandingPage with name already exists"},
                status=status.HTTP_409_CONFLICT,
            )

        landing_page = campaign_manager.create_landing_page(
            name=post_data["name"], template=post_data["html"]
        )

        post_data["gophish_template_id"] = landing_page.id

        created_response = landing_page_service.save(post_data)
        if "errors" in created_response:
            return Response(created_response, status=status.HTTP_400_BAD_REQUEST)
        return Response(created_response, status=status.HTTP_201_CREATED)


class LandingPageView(APIView):
    """LandingPageView."""

    @swagger_auto_schema(operation_id="Get single LandingPage")
    def get(self, request, landing_page_uuid):
        """Get method."""
        landing_page = landing_page_service.get(landing_page_uuid)
        return Response(landing_page)

    @swagger_auto_schema(
        request_body=LandingPagePatchSerializer,
        operation_id="Update and Patch single LandingPage",
    )
    def patch(self, request, landing_page_uuid):
        """Patch method."""
        data = request.data.copy()

        landing_page = landing_page_service.get(landing_page_uuid)

        campaign_manager.put_landing_page(
            gp_id=landing_page["gophish_template_id"],
            name=data["name"],
            html=data["html"],
        )

        if data["is_default_template"]:
            landing_page_service.clear_and_set_default(landing_page_uuid)

        # this really seems like there should be a better way.
        update_put_value = {
            "landing_page_uuid": landing_page_uuid,
            "name": data["name"],
            "is_default_template": data["is_default_template"],
            "html": data["html"],
        }
        updated_response = landing_page_service.update(
            landing_page_uuid, update_put_value
        )
        if "errors" in updated_response:
            return Response(updated_response, status=status.HTTP_400_BAD_REQUEST)
        return Response(updated_response, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(operation_id="Delete single LandingPage")
    def delete(self, request, landing_page_uuid):
        """Delete method."""
        delete_response = landing_page_service.delete(landing_page_uuid)
        if "errors" in delete_response:
            return Response(delete_response, status=status.HTTP_400_BAD_REQUEST)
        return Response(delete_response, status=status.HTTP_200_OK)


class LandingPageStopView(APIView):
    """
    This is the LandingPageStopView APIView.

    This handles the API for stopping all campaigns using a landing_page with landing_page_uuid
    """

    @swagger_auto_schema(operation_id="Get single LandingPage")
    def get(self, request, landing_page_uuid):
        """Get method."""
        # get subscriptions
        parameters = {"landing_pages_selected_uuid_list": landing_page_uuid}
        subscriptions = subscription_service.get_list(parameters)

        # Stop subscriptions
        updated_subscriptions = list(map(stop_subscription, subscriptions))

        # Get landing_page
        landing_page = landing_page_service.get(landing_page_uuid)

        # Update landing_page
        landing_page["retired"] = True
        landing_page["retired_description"] = "Manually Stopped"
        updated_landing_page = landing_page_service.update(
            landing_page_uuid, LandingPagePatchSerializer(landing_page).data
        )

        # Generate and return response
        resp = {
            "landing_page": updated_landing_page,
            "subscriptions": updated_subscriptions,
        }
        serializer = LandingPageStopResponseSerializer(resp)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
