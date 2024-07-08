from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from advertisement import serializers, models
from advertisement.models import Advertisement
import math
from region.pagination import CustomPagination
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from datetime import date

from . serializers import AdvertisementSerializerPut


class AdvertisementAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.AdvertisementSerializers
    queryset = models.Advertisement.objects.all().order_by('-id')

    def get_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return Response({
                "success": True,
                "message": "Success",
                "data": self.queryset.get(pk=pk),
            }, status=status.HTTP_201_CREATED)

        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Advertisement details
            :param request: Advertisement details
            :param kwargs: NA
            :return: Advertisement details
        """
        serializer = self.serializer_class(data=request.data, context={"user": self.get_user()})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        """
        Updates snippets delete
        :param kwargs: snippets id
        :return: message
        """
        pk = request.data.get('id')
        snippets = self.queryset.filter(id=pk)
        if snippets:
            snippets.delete()
            return Response({
                "success": True,
                "message": "Successfully Deleted",
                "data": {},
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, **kwargs):
        """
        Updates snippets delete
        :param kwargs: snippets id
        :return: message
        """
        pk = request.data.get('id')
        snippets = self.get_object(pk)
        serializer = AdvertisementSerializerPut(instance=snippets, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class AdvertisementGetItem(generics.ListCreateAPIView):
    """
        Get One Advertisement
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.AdvertisementSerializers
    queryset = models.Advertisement.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            pk = request.data.get('id')
            snippet = models.Advertisement.objects.get(id=pk)
        except Advertisement.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            serializer = serializers.AdvertisementSerializers(snippet, context={"request": request})
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)


class AdvertisementBulkDeleteAPI(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.AdvertisementSerializers
    queryset = models.Advertisement.objects.all().order_by('-id')

    def delete(self, request, **kwargs):
        """
        Updates snippets delete
        :param kwargs: snippets id
        :return: message
        """
        pk = request.data.get('ids')
        if pk:
            for i in pk:
                snippets = self.queryset.filter(id=i)
                if snippets:
                    snippets.delete()
            return Response({
                "success": True,
                "message": "Successfully Deleted",
                "data": {},
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class AdvertisementGetAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.AdvertisementSerializers
    queryset = models.Advertisement.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
        """
            create MC Bookmark details
            :param request: Bookmark details
            :param kwargs: NA
            :return: Bookmark details
        """

        try:
            import socket
            import re
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            url = request.build_absolute_uri()

            http_layer = request.is_secure() and "https" or "http"
            http_address = request.get_host()
            http_port = request.META['SERVER_PORT']
            urls = str(http_layer + "://" + http_address)

            snippets = models.Advertisement.objects.all()
            if snippets:
                mc_list = []
                for i in snippets:
                    mark_dict = {
                        "id": i.id,
                        "customer_name": i.customer_name if i.customer_name else False,
                        "company_name": i.company_name,
                        "english_title": i.english_title,
                        "chinese_title": i.chinese_title,
                        "advertisement_image": urls + "/media/" + str(i.advertisement_image) or False,
                        "advertisement_link": i.advertisement_link if i.advertisement_link else False,
                        "advertisement_start_date": i.advertisement_start_date if i.advertisement_start_date else False,
                        "advertisement_end_date": i.advertisement_end_date if i.advertisement_end_date else False,
                        "advertisement_price": i.advertisement_price if i.advertisement_price else False,
                        "advertisement_payment_method": i.advertisement_payment_method if i.advertisement_payment_method else False,
                        "advertisement_active": i.advertisement_active if i.advertisement_active else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    mc_list.append(mark_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": mc_list,
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": True,
                    "message": "Not Found",
                    "data": {},
                }, status=status.HTTP_200_OK)
        except Advertisement.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class AdvertisementUpdateAPI(generics.ListCreateAPIView):
    """
        Get One Advertisement
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.AdvertisementSerializers
    queryset = models.Advertisement.objects.all().order_by('-id')

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Advertisement details
            :param request: Advertisement details
            :param kwargs: NA
            :return: Advertisement details
        """
        try:
            pk = request.data.get('id')
            if pk:
                advertisement_obj = models.Advertisement.objects.filter(id=pk)
                serializer = self.serializer_class(data=request.data, context={"user": self.get_user()})
                if serializer.is_valid():
                    for adv in advertisement_obj:
                        if request.data.get('customer_name'):
                            adv.customer_name = request.data.get('customer_name')
                        if request.data.get('company_name'):
                            adv.company_name = request.data.get('company_name')
                        if request.data.get('english_title'):
                            adv.english_title = request.data.get('english_title')
                        if request.data.get('chinese_title'):
                            adv.chinese_title = request.data.get('chinese_title')
                        if request.data.get('advertisement_image'):
                            adv.advertisement_image = request.data.get('advertisement_image')
                        if request.data.get('advertisement_link'):
                            adv.advertisement_link = request.data.get('advertisement_link')
                        if request.data.get('advertisement_start_date'):
                            adv.advertisement_start_date = request.data.get('advertisement_start_date')
                        if request.data.get('advertisement_end_date'):
                            adv.advertisement_end_date = request.data.get('advertisement_end_date')
                        if request.data.get('advertisement_price'):
                            adv.advertisement_price = request.data.get('advertisement_price')
                        if request.data.get('advertisement_payment_method'):
                            adv.advertisement_payment_method = request.data.get('advertisement_payment_method')
                        print("KLKLKL", request.data.get('advertisement_active'))
                        if request.data.get('advertisement_active') == "True" or request.data.get('advertisement_active') =="False":
                            adv.advertisement_active = request.data.get('advertisement_active')
                        adv.save()
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": serializer.data,
                    }, status=status.HTTP_201_CREATED)
                return Response({"success": False, "message": "Failed", "data": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        except Advertisement.DoesNotExist:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class AdvertisementList(generics.ListCreateAPIView):
    """
        Get Student Service List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.AdvertisementSerializers
    queryset = models.Advertisement.objects.all().order_by('id')
    pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        """
            Get all Advertisement
            :param request: Advertisement Records
            :param kwargs: NA
            :return: Advertisement Records
        """

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        page_size = 10
        paginator = CustomPagination()
        paginator.page_size = page_size

        snippets = self.queryset.all()
        advertisement_records = []
        seq = 1
        if snippets:
            for i in snippets:

                if i.advertisement_end_date:
                    if date.today() > i.advertisement_end_date:
                        advertisement_active = False
                    else:
                        advertisement_active = True
                else:
                    advertisement_active = False

                advertisement_vals = {
                    "id": i.id,
                    "customer_name": i.customer_name if i.customer_name else False,
                    "company_name": i.company_name,
                    "english_title": i.english_title,
                    "chinese_title": i.chinese_title,
                    "advertisement_image": urls + "/media/" + str(i.advertisement_image) or False,
                    "advertisement_link": i.advertisement_link if i.advertisement_link else False,
                    "advertisement_start_date": i.advertisement_start_date if i.advertisement_start_date else False,
                    "advertisement_end_date": i.advertisement_end_date if i.advertisement_end_date else False,
                    "advertisement_price": i.advertisement_price if i.advertisement_price else False,
                    "advertisement_payment_method": i.advertisement_payment_method if i.advertisement_payment_method else False,
                    "advertisement_active": advertisement_active,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                advertisement_records.append(advertisement_vals)
                seq = seq + 1

            result_page = paginator.paginate_queryset(advertisement_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(advertisement_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(advertisement_records) / page_size)
            else:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "success": True,
                "message": "Success",
                "data": paginator_data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)
