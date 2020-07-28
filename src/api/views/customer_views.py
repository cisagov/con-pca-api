"""
Customer Views.

This handles the api for all the Template urls.
"""
# Standard Python Libraries
import logging

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
from api.utils.db_utils import (
    delete_single,
    get_list,
    get_single,
    save_single,
    update_single,
)
from api.utils.sector_industry_utils import get_sectors_industries
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


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

        customer_list = get_list(
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
        existing_customer = get_list(
            customer_filter, "customer", CustomerModel, validate_customer
        )
        if existing_customer:
            return Response(
                "User with that identifier already exists",
                status=status.HTTP_202_ACCEPTED,
            )

        created_response = save_single(
            post_data, "customer", CustomerModel, validate_customer
        )
        logging.info("created response {}".format(created_response))
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
        logger.debug("get customer_uuid {}".format(customer_uuid))
        customer = get_single(
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
        logger.debug("get customer_uuid {}".format(customer_uuid))
        put_data = request.data.copy()
        serialized_data = CustomerPatchSerializer(put_data)
        updated_response = update_single(
            uuid=customer_uuid,
            put_data=serialized_data.data,
            collection="customer",
            model=CustomerModel,
            validation_model=validate_customer,
        )
        logging.info("created response {}".format(updated_response))
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
        logger.debug("delete customer_uuid {}".format(customer_uuid))
        delete_response = delete_single(
            customer_uuid, "customer", CustomerModel, validate_customer
        )
        logging.info("delete response {}".format(delete_response))
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
        logger.debug("get industry/sector list")

        # If added to database, pull data through
        # sectors_industries = get_list(
        #     parameters, "sectors", CREATESECTORMODEL, CREATESECTORVALIDATION
        # )

        # While usng hard coded sector/industry data, use below
        sectors_industries = get_sectors_industries()

        serializer = SectorGetSerializer(sectors_industries, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=CustomerPatchSerializer,
        responses={"202": "Industry Patched", "400": "Bad Request"},
        security=[],
        operation_id="Update and Patch single Industry",
        operation_description="This handles the API for the update industry and associated sectors",
    )
    def patch(self, request, sector_id):
        """Patch method."""
        logger.debug(f"patch sector_id {sector_id}")
        # Patch logic here

    @swagger_auto_schema(
        responses={"200": "IndustryDelete", "400": "Bad Request"},
        security=[],
        operation_id="Delete single Secotor Industry",
        operation_description="This handles the API for the delete of industry and associated sectors.",
    )
    def delete(self, request, sector_id):
        """Delete method."""
        logger.debug(f"delete sector_id {sector_id}")
        # Delete logic here
