from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from discounts import serializers, models
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from region .pagination import CustomPagination
import math


class DiscountCreate(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.DiscountSerializer
    queryset = models.Discount.objects.all().order_by('-id')

    def get_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
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
        serializer = self.serializer_class(instance=snippets, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class DiscountGetItem(generics.ListCreateAPIView):
    """
        Get One Advertisement
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.DiscountSerializer
    queryset = models.Discount.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            pk = request.data.get('id')
            snippet = models.Discount.objects.get(id=pk)
        except models.Discount.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            serializer = serializers.DiscountSerializer(snippet)
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)


class DiscountGraph(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.DiscountUsageSerializer
    queryset = models.DiscountUsage.objects.all().order_by('-id')

    def get_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        import datetime
        from datetime import timedelta

        discount_code = request.data.get('discount_code')
        school_id = request.data.get('school_id')

        from dateutil.relativedelta import relativedelta
        d = datetime.datetime.now()
        dt = d.strftime('%Y-%m-%d')
        datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
        start = datetime_str - timedelta(days=datetime_str.weekday())
        end = start + timedelta(days=6)
        first_date = datetime.datetime(d.year, 1, 1)
        last_date = datetime.datetime(d.year+1, 1, 1)
        delta = last_date - first_date
        form_data = []
        final_start = first_date
        final_end = first_date
        dataset_value = []
        dataset_label = []

        final_start1 = first_date
        final_end1 = first_date
        for x in range(12):
            final_end1 = final_end1 + relativedelta(months=1)
            dataset_label.append(final_start1.strftime("%b"))
            final_start1 = final_end1
        discount_code_value = False
        try:
            if discount_code:
                discount_code_obj = models.Discount.objects.get(promotion_name=discount_code)
                if discount_code_obj:
                    discount_code_value = discount_code_obj.id
        except:
            discount_code_value = False
        filters = None
        for x in range(12):
            final_end = final_end + relativedelta(months=1)
            informations = []
            if discount_code and school_id:
                filters == str(discount_code) + str(school_id)
                informations = models.DiscountUsage.objects.filter(created_date__range=[final_start, final_end],discount_code=discount_code_value,school_id=school_id).count()
            if discount_code and not school_id:
                filters == str(discount_code)
                informations = models.DiscountUsage.objects.filter(created_date__range=[final_start, final_end],discount_code=discount_code_value).count()
            if school_id and not discount_code:
                filters == str(discount_code) + str(school_id)
                informations = models.DiscountUsage.objects.filter(created_date__range=[final_start, final_end],school_id=school_id).count()
            if not school_id and not discount_code:
                informations = models.DiscountUsage.objects.filter(created_date__range=[final_start, final_end],).count()

            dataset_value.append(informations)

            final_start = final_end
        form_dict = {
            'label': dataset_label,
            'data': dataset_value,
            'filter_applied': filters
        }
        form_data.append(form_dict)
        return Response({
            "success": True,
            "message": "Success",
            "data": form_data,
            "label": dataset_label
        }, status=status.HTTP_201_CREATED)


class DiscountUsageCreate(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    permission_classes = (IsAuthenticated,)
    # parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.DiscountUsageSerializer
    queryset = models.DiscountUsage.objects.all().order_by('-id')

    def get_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def get(self, request):
        try:
            themes = models.DiscountUsage.objects.all()
            serializer = serializers.DiscountUsageSerializer(themes, many=True)
            if len(themes) < 1:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"success": True, "message": "Discount Details",
                 "data": serializer.data},
                status=status.HTTP_200_OK)
        except:
            return Response({"success": False, "message": "Something Went Wrong"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        """
            create Theme details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        serializer = self.serializer_class(data=request.data, context={"user": self.get_user(),'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Discount Created",
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
        serializer = serializers.DiscountUsageSerializer(instance=snippets, data=request.data,context= {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Invalid or Expired Code"}, status=status.HTTP_404_NOT_FOUND)


class DiscountVerify(generics.ListCreateAPIView):
    """
        Get One Advertisement
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.DiscountSerializer
    queryset = models.Discount.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            import datetime
            from datetime import timedelta
            d = datetime.datetime.now()
            dt = d.strftime('%Y-%m-%d')
            datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
            discount_code = request.data.get('discount_code')
            discount = models.Discount.objects.filter(discount_status=True, discount_code=discount_code,
                                                      discount_start_date__lte=datetime_str,
                                                      discount_end_date__gte=datetime_str).order_by('-id')[:10]
            if discount:
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": discount[0].discount_code,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Invalid or Expired Code"}, status=status.HTTP_404_NOT_FOUND)
        except models.Discount.DoesNotExist:
            return Response({"success": False, "message": "Invalid or Expired Code"}, status=status.HTTP_404_NOT_FOUND)


class DiscountAmount(generics.ListCreateAPIView):
    """
        Get One Advertisement
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.DiscountSerializer
    queryset = models.Discount.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            import datetime
            from datetime import timedelta
            d = datetime.datetime.now()
            dt = d.strftime('%Y-%m-%d')
            datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
            discount_code = request.data.get('discount_code')
            price = request.data.get('price')
            discount = models.Discount.objects.filter(discount_status=True, discount_code=discount_code,
                                                      discount_start_date__lte=datetime_str,
                                                      discount_end_date__gte=datetime_str).order_by('-id')[:10]
            if discount:
                if price and discount:
                    if discount[0].discount_percentage:
                        quotient = float(discount[0].discount_percentage_value) / float(price)
                        percent = price * (float(discount[0].discount_percentage_value)/100)
                        return Response({
                            "success": True,
                            "message": "Success",
                            "data": {
                                'discount_id': discount[0].id,
                                'discount_code': discount[0].discount_code,
                                'price': price,
                                'discount_amount': percent,
                                'discount_included_price': round(price - percent, 2),
                                'mode': 'percentage',
                                'discount_percentage_value': discount[0].discount_percentage_value
                            },
                        }, status=status.HTTP_200_OK)
                    if discount[0].discount_reduce_amount:
                        return Response({
                            "success": True,
                            "message": "Success",
                            "data": {
                                'discount_id': discount[0].id,
                                'discount_code': discount[0].discount_code,
                                'price': price,
                                'discount_amount': discount[0].discount_reduce_amount_value,
                                'discount_included_price': round(float(price) - float(discount[0].discount_reduce_amount_value), 2),
                                'mode': 'fixed',
                                'discount_reduce_amount_value': discount[0].discount_reduce_amount_value
                            },
                        }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Invalid code"}, status=status.HTTP_404_NOT_FOUND)
        except models.Discount.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class DiscountBulkDeleteAPI(generics.ListCreateAPIView):
    """
        List and Create Theme
    """

    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.DiscountSerializer
    queryset = models.Discount.objects.all().order_by('-id')

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


class DiscountList(generics.ListCreateAPIView):
    """
        Get Student Service List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.DiscountSerializer
    queryset = models.Discount.objects.all().order_by('id')
    pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        """
            Get all Discounts
            :param request: Discounts Records
            :param kwargs: NA
            :return: Discounts Records
        """

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        page_size = 10
        paginator = CustomPagination()
        paginator.page_size = page_size

        snippets = self.queryset.all()
        discount_records = []
        seq = 1
        if snippets:
            for i in snippets:
                discount_vals = {
                    "id": i.id,
                    "promotion_name": i.promotion_name if i.promotion_name else "",
                    "discount_code": i.discount_code if i.discount_code else "",
                    "discount_percentage": i.discount_percentage if i.discount_percentage else "",
                    "discount_percentage_value": i.discount_percentage_value if i.discount_percentage_value else "",
                    "discount_reduce_amount": i.discount_reduce_amount if i.discount_reduce_amount else "",
                    "discount_reduce_amount_value": i.discount_reduce_amount_value if i.discount_reduce_amount_value else "",
                    "discount_start_date": i.discount_start_date if i.discount_start_date else "",
                    "discount_end_date": i.discount_end_date if i.discount_end_date else "",
                    "discount_status": i.discount_status,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                discount_records.append(discount_vals)
                seq = seq + 1

            result_page = paginator.paginate_queryset(discount_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(discount_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(discount_records) / page_size)
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
