"""SendingProfile Views."""
# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.manager import CampaignManager
from api.serializers.sendingprofile_serializers import (
    SendingProfileDeleteResponseSerializer,
    SendingProfileSerializer,
)

# GoPhish API Manager
campaign_manager = CampaignManager()


class SendingProfilesListView(APIView):
    """SendingProfilesListView."""

    def get(self, request):
        """Get."""
        sending_profiles = campaign_manager.get_sending_profile()
        serializer = SendingProfileSerializer(sending_profiles, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Post."""
        sp = request.data.copy()
        sending_profile = campaign_manager.create_sending_profile(
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
    """SendingProfileView."""

    def get(self, request, id):
        """Get."""
        sending_profile = campaign_manager.get_sending_profile(smtp_id=id)
        serializer = SendingProfileSerializer(sending_profile)
        return Response(serializer.data)

    def patch(self, request, id):
        """Patch."""
        # get the saved record and overlay with whatever was sent
        sp = campaign_manager.get_sending_profile(smtp_id=id)
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
        sending_profile = campaign_manager.get_sending_profile(smtp_id=id)
        serializer = SendingProfileSerializer(sending_profile)
        return Response(serializer.data)

    def delete(self, request, id):
        """Delete."""
        delete_response = campaign_manager.delete_sending_profile(smtp_id=id)
        serializer = SendingProfileDeleteResponseSerializer(delete_response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def __setAttribute(self, orig, d, attrName):
        if attrName in d:
            return d[attrName]
        return orig
