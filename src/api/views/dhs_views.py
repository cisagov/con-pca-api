from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.serializers.dhs_serializers import (
    DHSContactPostSerializer,
    DHSContactQuerySerializer,
    DHSContactPatchSerializer,
)
from api.services import DHSContactService

from drf_yasg.utils import swagger_auto_schema

dhs_contact_service = DHSContactService()


class DHSContactListView(APIView):
    """ DHSContactListView """

    @swagger_auto_schema(
        query_serializer=DHSContactQuerySerializer,
        operation_id="List of DHS Contacts",
    )
    def get(self, request):
        """ GET """
        serializer = DHSContactQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()

        contact_list = dhs_contact_service.get_list(parameters)
        return Response(contact_list)

    @swagger_auto_schema(
        request_body=DHSContactPostSerializer,
        operation_id="Create DHS Contact",
    )
    def post(self, request, format=None):
        """ POST """
        post_data = request.data.copy()
        resp = dhs_contact_service.save(post_data)
        return Response(resp, status=status.HTTP_201_CREATED)


class DHSContactView(APIView):
    """ DHSContactView """

    @swagger_auto_schema(operation_id="Get single dhs contact")
    def get(self, request, dhs_contact_uuid):
        """ GET """
        contact = dhs_contact_service.get(dhs_contact_uuid)
        return Response(contact)

    @swagger_auto_schema(
        request_body=DHSContactPatchSerializer,
        operation_id="Update and Patch single dhs contact",
    )
    def patch(self, request, dhs_contact_uuid):
        """ PATCH """
        put_data = request.data.copy()
        serialized_data = DHSContactPatchSerializer(put_data)
        resp = dhs_contact_service.update(dhs_contact_uuid, serialized_data.data)
        return Response(resp, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(operation_id="Delete single dhs contact")
    def delete(self, request, dhs_contact_uuid):
        """ DELETE """
        resp = dhs_contact_service.delete(dhs_contact_uuid)
        return Response(resp, status=status.HTTP_202_ACCEPTED)
