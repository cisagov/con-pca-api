"""
Template Views.

This handles the api for all the Template urls.
"""
# Standard Python Libraries
import logging

# Third-Party Libraries
from api.manager import CampaignManager
from api.models.subscription_models import SubscriptionModel, validate_subscription
from api.models.template_models import (
    TagModel,
    TemplateModel,
    validate_tag,
    validate_template,
)
from api.serializers.template_serializers import (
    TagDeleteSerializer,
    TagGetSerializer,
    TagPatchSerializer,
    TagPostSerializer,
    TagQuerySerializer,
    TagResponseSerializer,
    TemplateDeleteResponseSerializer,
    TemplateGetSerializer,
    TemplatePatchResponseSerializer,
    TemplatePatchSerializer,
    TemplatePostResponseSerializer,
    TemplatePostSerializer,
    TemplateQuerySerializer,
    TemplateStopResponseSerializer,
)
from api.utils.db_utils import (
    delete_single,
    exists,
    get_list,
    get_single,
    save_single,
    update_single,
)
from api.utils.subscription.actions import stop_subscription
from api.utils.tag.tags import check_tag_format
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

campaign_manager = CampaignManager()


class TemplatesListView(APIView):
    """
    This is the TemplatesListView APIView.

    This handles the API to get a List of Templates.
    """

    @swagger_auto_schema(
        query_serializer=TemplateQuerySerializer,
        responses={"200": TemplateGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="List of Templates",
        operation_description="This handles the API to get a List of Templates.",
        tags=["Template"],
    )
    def get(self, request):
        """Get method."""
        serializer = TemplateQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()
        template_list = get_list(
            parameters, "template", TemplateModel, validate_template
        )
        serializer = TemplateGetSerializer(template_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=TemplatePostSerializer,
        responses={
            "201": TemplatePostResponseSerializer,
            "400": "Bad Request",
            "409": "CONFLICT",
        },
        security=[],
        operation_id="Create Template",
        operation_description="This handles Creating a Templates.",
        tags=["Template"],
    )
    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()

        if exists(
            {"name": post_data["name"]}, "template", TemplateModel, validate_template
        ):
            return Response(
                {"error": "Template with name already exists"},
                status=status.HTTP_409_CONFLICT,
            )

        created_response = save_single(
            post_data, "template", TemplateModel, validate_template
        )
        logger.info("created response {}".format(created_response))
        if "errors" in created_response:
            return Response(created_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = TemplatePostResponseSerializer(created_response)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TemplateView(APIView):
    """
    This is the TemplateView APIView.

    This handles the API for the Get a Template with template_uuid.
    """

    @swagger_auto_schema(
        responses={"200": TemplateGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get single Template",
        operation_description="This handles the API for the Get a Template with template_uuid.",
        tags=["Template"],
    )
    def get(self, request, template_uuid):
        """Get method."""
        logger.debug("get template_uuid {}".format(template_uuid))
        print("get template_uuid {}".format(template_uuid))
        template = get_single(
            template_uuid, "template", TemplateModel, validate_template
        )
        serializer = TemplateGetSerializer(template)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=TemplatePatchSerializer,
        responses={"202": TemplatePatchResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Update and Patch single Template",
        operation_description="This handles the API for the Update Template with template_uuid.",
        tags=["Template"],
    )
    def patch(self, request, template_uuid):
        """Patch method."""
        logger.debug("patch template_uuid {}".format(template_uuid))
        put_data = request.data.copy()
        if put_data["landing_page_uuid"] == "0" or not put_data["landing_page_uuid"]:
            put_data["landing_page_uuid"] = None
        serialized_data = TemplatePatchSerializer(put_data)
        updated_response = update_single(
            uuid=template_uuid,
            put_data=serialized_data.data,
            collection="template",
            model=TemplateModel,
            validation_model=validate_template,
        )
        logger.info("created response {}".format(updated_response))
        if "errors" in updated_response:
            return Response(updated_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = TemplatePatchResponseSerializer(updated_response)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        responses={"200": TemplateDeleteResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Delete single Template",
        operation_description="This handles the API for the Delete of a  Template with template_uuid.",
        tags=["Template"],
    )
    def delete(self, request, template_uuid):
        """Delete method."""
        logger.debug("delete template_uuid {}".format(template_uuid))
        delete_response = delete_single(
            template_uuid, "template", TemplateModel, validate_template
        )
        logger.info("delete response {}".format(delete_response))
        if "errors" in delete_response:
            return Response(delete_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = TemplateDeleteResponseSerializer(delete_response)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TemplateStopView(APIView):
    """
    This is the TemplateStopView APIView.

    This handles the API for stopping all campaigns using a template with template_uuid
    """

    @swagger_auto_schema(
        responses={"202": TemplateStopResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get single Template",
        operation_description="This handles the API for the Get a Template with template_uuid.",
        tags=["Template"],
    )
    def get(self, request, template_uuid):
        """Get method."""
        # get subscriptions
        parameters = {"templates_selected_uuid_list": template_uuid}
        subscriptions = get_list(
            parameters, "subscription", SubscriptionModel, validate_subscription
        )

        # Stop subscriptions
        updated_subscriptions = list(map(stop_subscription, subscriptions))

        # Get template
        template = get_single(
            template_uuid, "template", TemplateModel, validate_template
        )

        # Update template
        template["retired"] = True
        template["retired_description"] = "Manually Stopped"
        updated_template = update_single(
            uuid=template_uuid,
            put_data=TemplatePatchSerializer(template).data,
            collection="template",
            model=TemplateModel,
            validation_model=validate_template,
        )

        # Generate and return response
        resp = {"template": updated_template, "subscriptions": updated_subscriptions}
        serializer = TemplateStopResponseSerializer(resp)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class TagsView(APIView):
    """
    This is the Tags View APIView.

    This returns all Tags or POST to create a tag.
    """

    @swagger_auto_schema(
        query_serializer=TagQuerySerializer,
        responses={"200": TagResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get all template tags",
        operation_description="Returns a list of all template tags",
        tags=["Tag"],
    )
    def get(self, request):
        """Get method."""
        serializer = TagQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()
        tag_list = get_list(parameters, "tag_definition", TagModel, validate_tag)
        serializer = TagGetSerializer(tag_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=TagPostSerializer,
        responses={
            "201": TagResponseSerializer,
            "400": "Bad Request",
            "409": "CONFLICT",
        },
        security=[],
        operation_id="Create Tag",
        operation_description="This handles Creating a Tags.",
        tags=["Tag"],
    )
    def post(self, request):
        """Post Method.

        Args:
            request (Django request object): Django request object

        Returns:
            Response: HTTP Response object with serializzed data and HTTP reponce.
        """
        post_data = request.data.copy()

        if not check_tag_format(post_data["tag"]):
            return Response(
                {"error": "incorrect tag format"}, status=status.HTTP_400_BAD_REQUEST,
            )

        if exists({"tag": post_data["tag"]}, "tag_definition", TagModel, validate_tag):
            return Response(
                {"error": "Tag already exists"}, status=status.HTTP_409_CONFLICT,
            )

        created_response = save_single(
            post_data, "tag_definition", TagModel, validate_tag
        )
        logger.info("created response {}".format(created_response))
        if "errors" in created_response:
            return Response(created_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = TagResponseSerializer(created_response)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagView(APIView):
    """
    This is the Tag View APIView.

    This handles the API for getting a single Tag, udpating a Tag or Deleting a Tag.
    """

    @swagger_auto_schema(
        responses={"200": TagGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get single Tag",
        operation_description="This handles the API for the Get a Tag with tag_uuid.",
        tags=["Tag"],
    )
    def get(self, request, tag_uuid):
        """Get method."""
        logger.debug("get tag_uuid {}".format(tag_uuid))

        tag = get_single(tag_uuid, "tag_definition", TagModel, validate_tag)
        serializer = TagGetSerializer(tag)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=TagPatchSerializer,
        responses={"202": TagResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Update and Patch single Tag",
        operation_description="This handles the API for the Update Tag with tag_uuid.",
        tags=["Tag"],
    )
    def patch(self, request, tag_uuid):
        """Patch method."""
        logger.debug("patch tag_uuid {}".format(tag_uuid))
        put_data = request.data.copy()
        serialized_data = TagPatchSerializer(put_data)
        updated_response = update_single(
            uuid=tag_uuid,
            put_data=serialized_data.data,
            collection="tag_definition",
            model=TagModel,
            validation_model=validate_tag,
        )
        logger.info("created response {}".format(updated_response))
        if "errors" in updated_response:
            return Response(updated_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = TagResponseSerializer(updated_response)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        responses={"200": TagDeleteSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Delete single Template",
        operation_description="This handles the API for the Delete of a  Template with template_uuid.",
        tags=["Tag"],
    )
    def delete(self, request, tag_uuid):
        """Delete method."""
        logger.debug("delete tag_uuid {}".format(tag_uuid))
        delete_response = delete_single(
            tag_uuid, "tag_definition", TagModel, validate_tag
        )
        logger.info("delete response {}".format(delete_response))
        if "errors" in delete_response:
            return Response(delete_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = TagDeleteSerializer(delete_response)
        return Response(serializer.data, status=status.HTTP_200_OK)
