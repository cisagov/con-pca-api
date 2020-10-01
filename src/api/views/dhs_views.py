from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.serializers.dhs_serializers import (
    DHSContactGetSerializer,
    DHSContactPostSerializer,
    DHSContactPostResponseSerializer,
    DHSContactQuerySerializer,
    DHSContactDeleteResponseSerializer,
    DHSContactPatchSerializer,
)
from api.models.dhs_models import DHSContactModel, validate_dhs_contact
from api.utils import db_utils as db

from drf_yasg.utils import swagger_auto_schema


class DHSContactListView(APIView):
    @swagger_auto_schema(
        query_serializer=DHSContactQuerySerializer,
        responses={"200": DHSContactGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="List of DHS Contacts",
        operation_description="This handles the API to get a list of dhs contacts",
    )
    def get(self, request):
        serializer = DHSContactQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()

        contact_list = db.get_list(
            parameters, "dhs_contact", DHSContactModel, validate_dhs_contact
        )
        serializer = DHSContactGetSerializer(contact_list, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=DHSContactPostSerializer,
        responses={"201": DHSContactPostResponseSerializer},
        security=[],
        operation_id="Create DHS Contact",
        operation_description="This handles creating a DHS Contact",
    )
    def post(self, request, format=None):
        post_data = request.data.copy()
        resp = db.save_single(
            post_data, "dhs_contact", DHSContactModel, validate_dhs_contact
        )
        serializer = DHSContactPostResponseSerializer(resp)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DHSContactView(APIView):
    @swagger_auto_schema(
        responses={"200": DHSContactGetSerializer},
        security=[],
        operation_id="Get single dhs contact",
        operation_description="This handles the API for the Get a dhs contact with dhs_contact_uuid.",
    )
    def get(self, request, dhs_contact_uuid):
        contact = db.get_single(
            dhs_contact_uuid, "dhs_contact", DHSContactModel, validate_dhs_contact
        )
        serializer = DHSContactGetSerializer(contact)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=DHSContactPatchSerializer,
        responses={"202": DHSContactGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Update and Patch single dhs contact",
        operation_description="This handles the API for the Update dhs contact with dhs_contact_uuid.",
    )
    def patch(self, request, dhs_contact_uuid):
        put_data = request.data.copy()
        serialized_data = DHSContactPatchSerializer(put_data)
        resp = db.update_single(
            uuid=dhs_contact_uuid,
            put_data=serialized_data.data,
            collection="dhs_contact",
            model=DHSContactModel,
            validation_model=validate_dhs_contact,
        )
        serializer = DHSContactGetSerializer(resp)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        responses={"202": DHSContactDeleteResponseSerializer},
        security=[],
        operation_id="Delete single dhs contact",
        operation_description="API for deleting a single dhs contact",
    )
    def delete(self, request, dhs_contact_uuid):
        resp = db.delete_single(
            dhs_contact_uuid, "dhs_contact", DHSContactModel, validate_dhs_contact
        )
        serializer = DHSContactDeleteResponseSerializer(resp)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
