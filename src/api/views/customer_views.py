"""Customer Views."""
# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.serializers.customer_serializers import (
    CustomerQuerySerializer,
    SectorGetSerializer,
)
from api.services import CustomerService
from api.utils.sector_industry_utils import get_sectors_industries

customer_service = CustomerService()


class CustomerListView(APIView):
    """CustomerListView."""

    def get(self, request):
        """Get method."""
        serializer = CustomerQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()

        customer_list = customer_service.get_list(parameters)
        return Response(customer_list)

    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()
        # Check for existing customer with the same name and identifier pair
        customer_filter = {
            "identifier": post_data["identifier"],
            "name": post_data["name"],
        }
        if customer_service.exists(customer_filter):
            return Response(
                "User with that identifier already exists",
                status=status.HTTP_202_ACCEPTED,
            )
        created_response = customer_service.save(post_data)
        return Response(created_response, status=status.HTTP_201_CREATED)


class CustomerView(APIView):
    """CustomerView."""

    def get(self, request, customer_uuid):
        """Get."""
        customer = customer_service.get(customer_uuid)
        return Response(customer)

    def patch(self, request, customer_uuid):
        """Patch."""
        put_data = request.data.copy()
        updated_response = customer_service.update(customer_uuid, put_data)
        return Response(updated_response, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, customer_uuid):
        """Delete."""
        delete_response = customer_service.delete(customer_uuid)
        return Response(delete_response, status=status.HTTP_200_OK)


class SectorIndustryView(APIView):
    """SectorIndustryView."""

    def get(self, request):
        """Get."""
        sectors_industries = get_sectors_industries()
        serializer = SectorGetSerializer(sectors_industries, many=True)
        return Response(serializer.data)
