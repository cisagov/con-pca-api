"""Recommendation Views."""

# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.serializers.recommendations_serializers import RecommendationsQuerySerializer
from api.services import RecommendationService

recommendation_service = RecommendationService()


class RecommendationsListView(APIView):
    """
    This is the Recommendations List API View.

    This handles the API to get a List of Recommendations.
    """

    def get(self, request):
        """Get method."""
        serializer = RecommendationsQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()
        recommendations_list = recommendation_service.get_list(parameters)
        return Response(recommendations_list, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()

        if recommendation_service.exists({"name": post_data["name"]}):
            return Response(
                {"error": "Recommendation with name already exists"},
                status=status.HTTP_409_CONFLICT,
            )
        created_response = recommendation_service.save(post_data)

        return Response(created_response, status=status.HTTP_201_CREATED)


class RecommendationsView(APIView):
    """
    This is the Recommendations API View.

    This handles the API for a Recommendation with recommendations_uuid.
    """

    def get(self, request, recommendations_uuid):
        """Get method."""
        recommendations = recommendation_service.get(recommendations_uuid)
        return Response(recommendations)

    def patch(self, request, recommendations_uuid):
        """Patch method."""
        put_data = request.data.copy()
        updated_response = recommendation_service.update(recommendations_uuid, put_data)
        return Response(updated_response, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, recommendations_uuid):
        """Delete method."""
        delete_response = recommendation_service.delete(recommendations_uuid)
        return Response(delete_response, status=status.HTTP_200_OK)
