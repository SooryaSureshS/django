from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from PurchaseOrder import serializer, models
from PurchaseOrder.models import PurchaseOrder
from PurchaseOrder.models import PaymentAcquirerStripe
from region.models import Forms
from accounts.models import user
import stripe
from rest_framework.decorators import api_view


class PurchaseUsageViews(generics.ListCreateAPIView):
    """
        List and Create SQ / Mark
    """

    # permission_classes = (IsAuthenticated,)
    serializer_class = serializer.PurchaseOrderSerializers
    queryset = models.PurchaseOrder.objects.all().order_by('-id')

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
            create WSQ details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        import datetime
        from datetime import timedelta

        filter_method = request.data.get('filter')
        from dateutil.relativedelta import relativedelta
        d = datetime.datetime.now()
        dt = d.strftime('%Y-%m-%d')
        datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
        start = datetime_str - timedelta(days=datetime_str.weekday())
        end = start + timedelta(days=6)
        first_date = datetime.datetime(d.year, 1, 1)
        last_date = datetime.datetime(d.year + 1, 1, 1)
        delta = last_date - first_date
        form_data = []
        forms = Forms.objects.all()
        for form in forms:
            final_start = first_date
            final_end = first_date
            dataset_value = []
            dataset_label = []
            for x in range(12):
                final_end = final_end + relativedelta(months=1)
                informations = PurchaseOrder.objects.filter(created_date__range=[final_start, final_end],
                                                            form_id=form.id).count()
                dataset_value.append(informations)
                dataset_label.append(final_start.strftime("%b"))
                final_start = final_end
            form_dict = {
                'form': form.id,
                'name': form.name,
                'label': dataset_label,
                'data': dataset_value

            }
            form_data.append(form_dict)
        return Response({
            "success": True,
            "message": "Success",
            "data": form_data,
        }, status=status.HTTP_201_CREATED)


class PurchaseCreate(generics.ListCreateAPIView):
    """
        List and Create PurchaseOrder
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializer.PurchaseOrderSerializers
    queryset = models.PurchaseOrder.objects.all().order_by('-id')

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
            partner_id = request.data.get('partner_id')
            user_obj = user.objects.filter(id=partner_id)
            for users in user_obj:
                users.is_purchased = True
                users.save()
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
        purchase_obj = models.PurchaseOrder.objects.filter(id=pk)

        if snippets:
            for purchases in snippets:
                partner_id = purchases.partner_id.id
                user_obj = user.objects.filter(id=partner_id)
                for users in user_obj:
                    users.is_purchased = False
                    users.save()
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


import json
from django.core import serializers


class PurchaseOrderByUser(generics.ListCreateAPIView):
    """
        List  PurchaseOrder
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializer.PurchaseOrderSerializers
    queryset = models.PurchaseOrder.objects.all().order_by('-id')

    def getObject(self, id):
        obj = models.PurchaseOrder.objects.get(pk=id)
        data = serializers.serialize('json', [obj, ])
        struct = json.loads(data)
        data = json.dumps(struct[0])
        return data

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
        purchase_orders = []
        try:
            purchase_order = models.PurchaseOrder.objects.filter(partner_id=request.data.get('partner_id'))
            if purchase_order:
                for i in purchase_order:
                    dict = {
                        'id': i.id,
                        'partner_id': i.partner_id.id if i.partner_id else False,
                        'form_id': i.form_id.id if i.form_id else False,
                        'price': str(i.price),
                        'tax': str(i.tax),
                        'discount': str(i.discount),
                        'created_date': i.created_date,
                        'updated_date': i.updated_date
                    }
                    purchase_orders.append(dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": purchase_orders,
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({"success": False, "message": "Failed", "data": "not found"},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"success": False, "message": "Failed", "data": "Not valid"},
                            status=status.HTTP_400_BAD_REQUEST)


class CreateCheckoutSessionView(generics.ListCreateAPIView):
    """
        Stripe Create Payment Intent Server Side for mobile app
        :return: PaymentIntent
    """

    def post(self, request, *args, **kwargs):
        try:
            amount = (request.data.get('amount'))
            if amount >= 4:
                stripe_vals = PaymentAcquirerStripe.objects.order_by('created_date').first()
                if stripe_vals:
                    stripe.api_key = stripe_vals.stripe_secret_key
                    val = stripe.PaymentIntent.create(
                        amount=amount,
                        currency='hkd',
                        payment_method_types=['card'],
                    )
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": val,
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({"success": False, "message": "Stripe not configured", "data": {}},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, "message": "Amount must be at least $4.00 hkd", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"success": False, "message": "Failed", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class PurchaseKeys(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        results = {"fixed_price": "Fixed_Price",
                   "purchase_keys": ["DIS_008", "DIS_015", "DIS_023", "DIS_028",
                                     "DIS_038", "DIS_048", "DIS_053", "DIS_058",
                                     "D_068", "D_078", "D_083", "D_088", "DIS_098",
                                     "D_108", "DIS_118"
                                     ],
                   "playstore_keys": ["fixed_price", "dis_008", "dis_015", "dis_023", "dis_028",
                                      "dis_038", "dis_048", "dis_053", "dis_058",
                                      "d_068", "d_078", "d_083", "d_088", "dis_098",
                                      "d_108", "dis_118"
                                      ]
                   }
        return Response({"success": True, "message": "List of Purchase Keys", "results": results},
                        status=status.HTTP_200_OK)
