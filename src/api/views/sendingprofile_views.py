"""SendingProfile Views."""
# Standard Python Libraries
import copy

# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.manager import CampaignManager
from api.serializers.campaign_serializers import GoPhishSmtpSerializer
from api.serializers.sendingprofile_serializers import (
    SendingProfileDeleteResponseSerializer,
    SendingProfileSerializer,
)
from api.services import CampaignService, SubscriptionService, TemplateService
from api.utils.subscription.campaigns import get_campaign_smtp

# GoPhish API Manager
campaign_manager = CampaignManager()
campaign_service = CampaignService()
template_service = TemplateService()
subscription_service = SubscriptionService()


class SendingProfilesListView(APIView):
    """SendingProfilesListView."""

    def get(self, request):
        """Get."""
        sending_profiles = campaign_manager.get_sending_profile()
        serializer = SendingProfileSerializer(sending_profiles, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Post."""
        sp = request.data
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
        patch_data = request.data

        sp.name = patch_data["name"]
        sp.interface_type = patch_data["interface_type"]
        sp.host = patch_data["host"]
        sp.username = patch_data["username"]
        sp.password = patch_data["password"]
        sp.ignore_cert_errors = patch_data["ignore_cert_errors"]
        sp.from_address = patch_data["from_address"]
        sp.headers = patch_data["headers"]

        campaign_manager.put_sending_profile(sp)

        sending_profile = campaign_manager.get_sending_profile(smtp_id=id)

        # Update any campaigns utilizing the sending profile
        campaigns = campaign_service.get_list(
            parameters={"smtp.parent_sending_profile_id": sending_profile.id}
        )
        for campaign in campaigns:
            smtp = copy.copy(sending_profile)
            smtp = get_campaign_smtp(
                smtp,
                campaign["subscription_uuid"],
                campaign["smtp"]["from_address"],
            )
            smtp.id = campaign["smtp"]["id"]
            smtp.name = campaign["smtp"]["name"]
            smtp.parent_sending_profile_id = sending_profile.id
            campaign_manager.put_sending_profile(smtp)
            campaign_service.update(
                campaign["campaign_uuid"], {"smtp": GoPhishSmtpSerializer(smtp).data}
            )

        return Response(SendingProfileSerializer(sending_profile).data)

    def delete(self, request, id):
        """Delete."""
        sending_profile = campaign_manager.get_sending_profile(id)

        if template_service.exists(parameters={"sending_profile_id": int(id)}):
            return Response(
                {"error": "Templates are currently utilizing this sending profile."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if subscription_service.exists(
            parameters={"sending_profile_name": sending_profile.name}
        ):
            subs_using = subscription_service.get_list(
                parameters={"sending_profile_name": sending_profile.name},
                fields=["name"],
            )
            return Response(
                {
                    "error": "Subscriptions are currently utilizing this sending profile.",
                    "fields": subs_using,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        delete_response = campaign_manager.delete_sending_profile(smtp_id=id)
        serializer = SendingProfileDeleteResponseSerializer(delete_response)
        return Response(serializer.data, status=status.HTTP_200_OK)
