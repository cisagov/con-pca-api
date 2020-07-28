"""
Sending Profile Views.
This handles the api for all the Sending Profile urls.
"""
# Standard Python Libraries
import logging

# Third-Party Libraries
# Local
from api.manager import CampaignManager
from api.serializers.sendingprofile_serializers import (
    SendingProfileDeleteResponseSerializer,
    SendingProfileDeleteSerializer,
    SendingProfilePatchResponseSerializer,
    SendingProfilePatchSerializer,
    SendingProfileSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)
# GoPhish API Manager
campaign_manager = CampaignManager()


class SendingProfilesListView(APIView):
    """
    This is the SendingProfilesListView APIView.
    This handles the API to get a List of Sending Profiles.
    """

    @swagger_auto_schema(
        responses={"200": SendingProfileSerializer, "400": "Bad Request"},
        security=[],
        operation_id="List of Sending Profiles",
        operation_description="This handles the API to get a List of Sending Profiles.",
    )
    def get(self, request):
        """Get method."""
        sending_profiles = campaign_manager.get("sending_profile")
        serializer = SendingProfileSerializer(sending_profiles, many=True)
        return Response(serializer.data)

    """
    This is the SendingProfileView APIView.
    This handles the API for creating a new Sending Profile.
    https://localhost:3333/api/smtp/:id
    """

    @swagger_auto_schema(
        request_body=SendingProfilePatchSerializer,
        responses={"202": SendingProfilePatchResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Create Sending Profile",
        operation_description="This handles the API for the Update Sending Profile with uuid.",
    )
    def post(self, request):
        sp = request.data.copy()
        sending_profile = campaign_manager.create(
            "sending_profile",
            name=sp.get("name"),
            username=sp.get("username"),
            password=sp.get("password"),
            host=sp.get("host"),
            interface_type=sp.get("interface_type"),
            from_address=sp.get("from_address"),
            ignore_cert_errors=sp.get("ignore_cert_errors"),
            headers=sp.get("headers"),
        )
        serializer = SendingProfileSerializer(sending_profile)
        return Response(serializer.data)


class SendingProfileView(APIView):
    """
    This is the SendingProfileView APIView.
    This handles the API for the Get a Sending Profile with id.
    """

    @swagger_auto_schema(
        responses={"200": SendingProfileSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get single Sending Profile",
        operation_description="This handles the API for the Get a Sending Profile with id.",
    )
    def get(self, request, id):
        sending_profile = campaign_manager.get("sending_profile", smtp_id=id)
        serializer = SendingProfileSerializer(sending_profile)
        return Response(serializer.data)

    """
    This is the SendingProfileView APIView.
    This handles the API for PATCHing a Sending Profile with id.
    https://localhost:3333/api/smtp/:id
    """

    @swagger_auto_schema(
        request_body=SendingProfilePatchSerializer,
        responses={"202": SendingProfilePatchResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Update and Patch single Sending Profile",
        operation_description="This handles the API for the Update Sending Profile with uuid.",
    )
    def patch(self, request, id):
        # get the saved record and overlay with whatever was sent
        sp = campaign_manager.get("sending_profile", smtp_id=id)
        patch_data = request.data.copy()

        sp.name = self.__setAttribute(sp.name, patch_data, "name")
        sp.interface_type = self.__setAttribute(
            sp.interface_type, patch_data, "interface_type"
        )
        sp.host = self.__setAttribute(sp.host, patch_data, "host")
        sp.username = self.__setAttribute(sp.username, patch_data, "username")
        sp.password = self.__setAttribute(sp.password, patch_data, "password")
        sp.ignore_cert_errors = self.__setAttribute(
            sp.ignore_cert_errors, patch_data, "ignore_cert_errors"
        )
        sp.from_address = self.__setAttribute(
            sp.from_address, patch_data, "from_address"
        )
        sp.headers = self.__setAttribute(sp.headers, patch_data, "headers")

        campaign_manager.put_sending_profile(sp)

        # get the new version from gophish to make sure we return the latest
        sending_profile = campaign_manager.get("sending_profile", smtp_id=id)
        serializer = SendingProfileSerializer(sending_profile)
        return Response(serializer.data)

    """
    This is the SendingProfileView APIView.
    This handles the API for PATCHing a Sending Profile with id.
    https://localhost:3333/api/smtp/:id
    """

    @swagger_auto_schema(
        request_body=SendingProfileDeleteSerializer,
        responses={"202": SendingProfileDeleteResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Delete single Sending Profile",
        operation_description="This handles the API for the Delete Sending Profile with uuid.",
    )
    def delete(self, request, id):
        delete_response = campaign_manager.delete("sending_profile", smtp_id=id)
        serializer = SendingProfileDeleteResponseSerializer(delete_response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def __setAttribute(self, orig, d, attrName):
        if attrName in d:
            return d[attrName]
        return orig
