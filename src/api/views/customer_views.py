"""
Customer Views.

This handles the api for all the Template urls.
"""
# Third-Party Libraries
from api.models.customer_models import CustomerModel, validate_customer
from api.serializers.customer_serializers import (
    CustomerDeleteResponseSerializer,
    CustomerGetSerializer,
    CustomerPatchResponseSerializer,
    CustomerPatchSerializer,
    CustomerPostResponseSerializer,
    CustomerPostSerializer,
    CustomerQuerySerializer,
    SectorGetSerializer,
)
from api.utils import db_utils as db
from api.utils.sector_industry_utils import get_sectors_industries
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class CustomerListView(APIView):
    """
    This is the CustomerListView APIView.

    This handles the API to get a List of Templates.
    """

    @swagger_auto_schema(
        query_serializer=CustomerQuerySerializer,
        responses={"200": CustomerGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="List of Customers",
        operation_description="This handles the API to get a List of Customers.",
    )
    def get(self, request):
        """Get method."""
        serializer = CustomerQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()

        customer_list = db.get_list(
            parameters, "customer", CustomerModel, validate_customer
        )
        serializer = CustomerGetSerializer(customer_list, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=CustomerPostSerializer,
        responses={"201": CustomerPostResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Create Customer",
        operation_description="This handles Creating a Customers.",
    )
    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()

        # Check for existing customer with the same name and identifier pair
        customer_filter = {
            "identifier": post_data["identifier"],
            "name": post_data["name"],
        }
        existing_customer = db.get_list(
            customer_filter, "customer", CustomerModel, validate_customer
        )
        if existing_customer:
            return Response(
                "User with that identifier already exists",
                status=status.HTTP_202_ACCEPTED,
            )

        created_response = db.save_single(
            post_data, "customer", CustomerModel, validate_customer
        )
        if "errors" in created_response:
            return Response(created_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = CustomerPostResponseSerializer(created_response)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomerView(APIView):
    """
    This is the CustomerView APIView.

    This handles the API for the Get a Customer with customer_uuid.
    """

    @swagger_auto_schema(
        responses={"200": CustomerGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get single Customer",
        operation_description="This handles the API for the Get a Customer with customer_uuid.",
    )
    def get(self, request, customer_uuid):
        """Get method."""
        customer = db.get_single(
            customer_uuid, "customer", CustomerModel, validate_customer
        )
        serializer = CustomerGetSerializer(customer)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=CustomerPatchSerializer,
        responses={"202": CustomerPatchResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Update and Patch single Customer",
        operation_description="This handles the API for the Update Customer with customer_uuid.",
    )
    def patch(self, request, customer_uuid):
        """Patch method."""
        put_data = request.data.copy()
        serialized_data = CustomerPatchSerializer(put_data)
        updated_response = db.update_single(
            uuid=customer_uuid,
            put_data=serialized_data.data,
            collection="customer",
            model=CustomerModel,
            validation_model=validate_customer,
        )
        if "errors" in updated_response:
            return Response(updated_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = CustomerPatchResponseSerializer(updated_response)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        responses={"200": CustomerDeleteResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Delete single Customer",
        operation_description="This handles the API for the Update Customer with customer_uuid.",
    )
    def delete(self, request, customer_uuid):
        """Delete method."""
        delete_response = db.delete_single(
            customer_uuid, "customer", CustomerModel, validate_customer
        )
        if "errors" in delete_response:
            return Response(delete_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = CustomerDeleteResponseSerializer(delete_response)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SectorIndustryView(APIView):
    """
    This is the SectorIndustryView APIView.

    This handles the API for Secotr and Industry elements.
    """

    @swagger_auto_schema(
        responses={"200": SectorGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get all Sectors",
        operation_description="This handles the API for the Get sectors and their associated industries",
    )
    def get(self, request):
        """Get method."""
        # While usng hard coded sector/industry data, use below
        sectors_industries = get_sectors_industries()

        serializer = SectorGetSerializer(sectors_industries, many=True)
        return Response(serializer.data)
