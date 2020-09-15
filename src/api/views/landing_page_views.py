"""
Landing Page Views

This handles the api for all the landing Page URLS
"""
# Standard Python Libraries
import logging

# Third-Party Libraries
from api.manager import CampaignManager
from api.models.subscription_models import SubscriptionModel, validate_subscription
from api.models.landing_page_models import LandingPageModel, validate_landing_page
from api.serializers.landing_page_serializers import (
    LandingPageDeleteResponseSerializer,
    LandingPageGetSerializer,
    LandingPagePatchResponseSerializer,
    LandingPagePatchSerializer,
    LandingPagePostResponseSerializer,
    LandingPagePostSerializer,
    LandingPageQuerySerializer,
    LandingPageStopResponseSerializer,
)
from api.utils.db_utils import (
    delete_single,
    exists,
    get_list,
    get_single,
    save_single,
    update_single,
)
from api.utils.landing_pages import clear_and_set_default
from api.utils.subscription.actions import stop_subscription
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

campaign_manager = CampaignManager()


class LandingPagesListView(APIView):
    """
    This is the LandingPagesListView APIView.

    This handles the API to get a List of LandingPages.
    """

    @swagger_auto_schema(
        query_serializer=LandingPageQuerySerializer,
        responses={"200": LandingPageGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="List of LandingPages",
        operation_description="This handles the API to get a List of LandingPages.",
        tags=["LandingPage"],
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
        landing_page_list = get_list(
            parameters, "landing_page", LandingPageModel, validate_landing_page
        )
        default_landing_page = LandingPageModel()
        for landing_page in landing_page_list:
            if landing_page["is_default_template"]:
                default_landing_page = landing_page.copy()
                break

        default_landing_page["name"] = "(System Default)" + default_landing_page["name"]
        default_landing_page["landing_page_uuid"] = 0
        if with_default:
            landing_page_list.append(default_landing_page)
        serializer = LandingPageGetSerializer(landing_page_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=LandingPagePostSerializer,
        responses={
            "201": LandingPagePostResponseSerializer,
            "400": "Bad Request",
            "409": "CONFLICT",
        },
        security=[],
        operation_id="Create LandingPage",
        operation_description="This handles Creating a LandingPages.",
        tags=["LandingPage"],
    )
    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()

        if exists(
            {"name": post_data["name"]},
            "landing_page",
            LandingPageModel,
            validate_landing_page,
        ):
            return Response(
                {"error": "LandingPage with name already exists"},
                status=status.HTTP_409_CONFLICT,
            )

        landing_page = campaign_manager.create(
            "landing_page", name=post_data["name"], template=post_data["html"]
        )

        post_data["gophish_template_id"] = landing_page.id

        created_response = save_single(
            post_data, "landing_page", LandingPageModel, validate_landing_page
        )
        logger.info("created response {}".format(created_response))
        if "errors" in created_response:
            return Response(created_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = LandingPagePostResponseSerializer(created_response)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LandingPageView(APIView):
    """
    This is the LandingPageView APIView.

    This handles the API for the Get a LandingPage with landing_page_uuid.
    """

    @swagger_auto_schema(
        responses={"200": LandingPageGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get single LandingPage",
        operation_description="This handles the API for the Get a LandingPage with landing_page_uuid.",
        tags=["LandingPage"],
    )
    def get(self, request, landing_page_uuid):
        """Get method."""
        logger.debug("get landing_page_uuid {}".format(landing_page_uuid))
        print("get landing_page_uuid {}".format(landing_page_uuid))
        landing_page = get_single(
            landing_page_uuid, "landing_page", LandingPageModel, validate_landing_page
        )
        serializer = LandingPageGetSerializer(landing_page)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=LandingPagePatchSerializer,
        responses={"202": LandingPagePatchResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Update and Patch single LandingPage",
        operation_description="This handles the API for the Update LandingPage with landing_page_uuid.",
        tags=["LandingPage"],
    )
    def patch(self, request, landing_page_uuid):
        """Patch method."""
        logger.debug("patch landing_page_uuid {}".format(landing_page_uuid))
        put_data = request.data.copy()

        data = LandingPagePatchSerializer(put_data).data

        landing_page = get_single(
            landing_page_uuid, "landing_page", LandingPageModel, validate_landing_page
        )

        campaign_manager.put(
            "landing_page",
            gp_id=landing_page["gophish_template_id"],
            name=data["name"],
            html=data["html"],
        )

        if data["is_default_template"]:
            self.set_default_template(landing_page_uuid)

        # this really seems like there should be a better way.
        update_put_value = {
            "landing_page_uuid": landing_page_uuid,
            "name": data["name"],
            "is_default_template": data["is_default_template"],
            "retired": data["retired"],
            "retired_description": data["retired_description"],
            "html": data["html"],
        }
        updated_response = update_single(
            uuid=landing_page_uuid,
            put_data=update_put_value,
            collection="landing_page",
            model=LandingPageModel,
            validation_model=validate_landing_page,
        )
        logger.info("created response {}".format(updated_response))
        if "errors" in updated_response:
            return Response(updated_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = LandingPagePatchResponseSerializer(updated_response)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        responses={"200": LandingPageDeleteResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Delete single LandingPage",
        operation_description="This handles the API for the Delete of a  LandingPage with landing_page_uuid.",
        tags=["LandingPage"],
    )
    def delete(self, request, landing_page_uuid):
        """Delete method."""
        logger.debug("delete landing_page_uuid {}".format(landing_page_uuid))
        delete_response = delete_single(
            landing_page_uuid, "landing_page", LandingPageModel, validate_landing_page
        )
        logger.info("delete response {}".format(delete_response))
        if "errors" in delete_response:
            return Response(delete_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = LandingPageDeleteResponseSerializer(delete_response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def set_default_template(self, landing_page_uuid):
        clear_and_set_default(landing_page_uuid)


class LandingPageStopView(APIView):
    """
    This is the LandingPageStopView APIView.

    This handles the API for stopping all campaigns using a landing_page with landing_page_uuid
    """

    @swagger_auto_schema(
        responses={"202": LandingPageStopResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get single LandingPage",
        operation_description="This handles the API for the Get a LandingPage with landing_page_uuid.",
        tags=["LandingPage"],
    )
    def get(self, request, landing_page_uuid):
        """Get method."""
        # get subscriptions
        parameters = {"landing_pages_selected_uuid_list": landing_page_uuid}
        subscriptions = get_list(
            parameters, "subscription", SubscriptionModel, validate_subscription
        )

        # Stop subscriptions
        updated_subscriptions = list(map(stop_subscription, subscriptions))

        # Get landing_page
        landing_page = get_single(
            landing_page_uuid, "landing_page", LandingPageModel, validate_landing_page
        )

        # Update landing_page
        landing_page["retired"] = True
        landing_page["retired_description"] = "Manually Stopped"
        updated_landing_page = update_single(
            uuid=landing_page_uuid,
            put_data=LandingPagePatchSerializer(landing_page).data,
            collection="landing_page",
            model=LandingPageModel,
            validation_model=validate_landing_page,
        )

        # Generate and return response
        resp = {
            "landing_page": updated_landing_page,
            "subscriptions": updated_subscriptions,
        }
        serializer = LandingPageStopResponseSerializer(resp)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
