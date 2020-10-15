"""
Customer Views.

This handles the api for all the Template urls.
"""
from api.serializers.customer_serializers import (
    CustomerPatchSerializer,
    CustomerPostSerializer,
    CustomerQuerySerializer,
    SectorGetSerializer,
)
from api.utils.sector_industry_utils import get_sectors_industries
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.services import CustomerService

customer_service = CustomerService()


class CustomerListView(APIView):
    """ CustomerListView """

    @swagger_auto_schema(
        query_serializer=CustomerQuerySerializer,
        operation_id="List of Customers",
    )
    def get(self, request):
        """Get method."""
        serializer = CustomerQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()

        customer_list = customer_service.get_list(parameters)
        return Response(customer_list)

    @swagger_auto_schema(
        request_body=CustomerPostSerializer,
        operation_id="Create Customer",
    )
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
    """ CustomerView """

    @swagger_auto_schema(operation_id="Get single Customer")
    def get(self, request, customer_uuid):
        """ GET """
        customer = customer_service.get(customer_uuid)
        return Response(customer)

    @swagger_auto_schema(
        request_body=CustomerPatchSerializer,
        operation_id="Update and Patch single Customer",
    )
    def patch(self, request, customer_uuid):
        """ PATCH """
        put_data = request.data.copy()
        updated_response = customer_service.update(customer_uuid, put_data)
        return Response(updated_response, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(operation_id="Delete single Customer")
    def delete(self, request, customer_uuid):
        """ DELETE """
        delete_response = customer_service.delete(customer_uuid)
        return Response(delete_response, status=status.HTTP_200_OK)


class SectorIndustryView(APIView):
    """ SectoryIndustryView """

    @swagger_auto_schema(
        responses={"200": SectorGetSerializer, "400": "Bad Request"},
        operation_id="Get all Sectors",
    )
    def get(self, request):
        """ GET """
        sectors_industries = get_sectors_industries()
        serializer = SectorGetSerializer(sectors_industries, many=True)
        return Response(serializer.data)
