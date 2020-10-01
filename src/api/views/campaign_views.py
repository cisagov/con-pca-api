"""Campaign View."""
# Third-Party Libraries
from api.manager import CampaignManager
from api.serializers import campaign_serializers
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

manager = CampaignManager()


class CampaignListView(APIView):
    """
    This is the a Campaign list API View.

    This handles the API to get a List of GoPhish Campaigns.
    """

    @swagger_auto_schema(
        responses={
            "200": campaign_serializers.CampaignSerializer,
            "400": "Bad Request",
        },
        security=[],
        operation_id="Get List of Campaigns ",
        operation_description=" This handles the API to get a List of GoPhish Campaigns.",
    )
    def get(self, request):
        """Get method."""
        campaigns = manager.get_campaign()
        serializer = campaign_serializers.CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)


class CampaignDetailView(APIView):
    """
    This is the Campaign Detail APIView.

    This handles the API to get Campaign details with campaign_id from GoPhish.
    """

    @swagger_auto_schema(
        responses={
            "200": campaign_serializers.CampaignSerializer,
            "400": "Bad Request",
        },
        security=[],
        operation_id="Get single Campaign ",
        operation_description=" This handles the API to get a List of GoPhish Campaigns.",
    )
    def get(self, request, campaign_id):
        """Get method."""
        campaign = manager.get_campaign(campaign_id=campaign_id)
        serializer = campaign_serializers.CampaignSerializer(campaign)
        return Response(serializer.data)
