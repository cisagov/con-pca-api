from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.serializers.dhs_serializers import DHSContactQuerySerializer
from api.services import DHSContactService

dhs_contact_service = DHSContactService()


class DHSContactListView(APIView):
    """ DHSContactListView """

    def get(self, request):
        """ GET """
        serializer = DHSContactQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()

        contact_list = dhs_contact_service.get_list(parameters)
        return Response(contact_list)

    def post(self, request, format=None):
        """ POST """
        post_data = request.data.copy()
        resp = dhs_contact_service.save(post_data)
        return Response(resp, status=status.HTTP_201_CREATED)


class DHSContactView(APIView):
    """ DHSContactView """

    def get(self, request, dhs_contact_uuid):
        """ GET """
        contact = dhs_contact_service.get(dhs_contact_uuid)
        return Response(contact)

    def patch(self, request, dhs_contact_uuid):
        """ PATCH """
        resp = dhs_contact_service.update(dhs_contact_uuid, request.data.copy())
        return Response(resp, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, dhs_contact_uuid):
        """ DELETE """
        resp = dhs_contact_service.delete(dhs_contact_uuid)
        return Response(resp, status=status.HTTP_202_ACCEPTED)
