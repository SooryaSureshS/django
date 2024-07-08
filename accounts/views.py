# Create your views here.
from rest_framework import generics
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer
from accounts.models import login_frequency
from accounts import models
from django.db.models import Q


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "Account Created",
                "data":
                    {
                        "user": UserSerializer(user, context=self.get_serializer_context()).data,
                        "token": AuthToken.objects.create(user)[1]
                    },
                }, status=status.HTTP_200_OK)
        else:
            email = request.data.get('email')
            email_exist = models.user.objects.filter(email=email).exists()
            if email_exist:
                return Response({"success": False, "message": "Account Creation Failed",
                                 "data": "This Email address has been registered"},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({"success": False, "message": "Account Creation Failed",
                             "data": str(list(serializer.errors.keys())[0]) + ": " + str(
                                 list(serializer.errors.values())[0][0])},
                            status=status.HTTP_400_BAD_REQUEST)


from accounts.serializers import LoginSerializer


class SignInAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            user_obj = models.user.objects.get(email=user)
            if user_obj.form_id:
                login_frequency.objects.create(user_id=user_obj, form_id=user_obj.form_id)
            tokens = AuthToken.objects.filter(user_id=user_obj.id)
            for i in tokens:
                i.delete()
            return Response({
                "success": True,
                "message": "Successfully Logged In",
                "data":
                    {
                        "user": UserSerializer(user, context=self.get_serializer_context()).data,
                        "token": AuthToken.objects.create(user)[1]
                    },
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Login Failed",
                             "data": str(list(serializer.errors.keys())[0]) + ": " + str(
                                 list(serializer.errors.values())[0][0])},
                            status=status.HTTP_400_BAD_REQUEST)


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import logout


def logout_user(request):
    logout(request)


class Logout(APIView):
    def post(self, request, format=None):
        logout(request)
        return Response(status=status.HTTP_200_OK)


from django.conf import settings
from django.core.mail import send_mail
import random
import uuid


class ResetPasswordApi(APIView):

    def post(self, request, format=None):
        email_id = request.data.get('email_id')
        number = random.randint(1111, 9999)

        if email_id:
            user_id = user.objects.filter(email=request.data.get('email_id')).first()
            if user_id:
                pass_url = uuid.uuid4()
                user_id.password_url = pass_url
                user_id.otp = number
                user_id.save()
                firstname = ""
                if user_id.firstname:
                    firstname = user_id.firstname
                subject = 'Reset Password'
                message = '''<div style="margin: 0px; padding: 0px;">
                        <p style="margin: 0px; padding: 0px; font-size: 13px;">
                            Dear Marshall Cavendish Education User ,
                            <br/><br/>
                            Upon your request for online account login, the following OTP has been generated.
                            <br/>
                             <p><label style="font-weight:600;">One-Time Password ("OTP"): ''' + str(number) +'''</label><br/>
                                <br/>
                            Please do not share this verification code with anyone. The OTP will expire in 10 minutes
                             <br/>upon the sending out of this email. If the password is expired, simply take the same steps to
                              <br/>generate OTP again. Please contact our service hotline at 2945 7201 for any enquiries.
                            <br/>
                            <p>Regards,</p>
                            <p>Marshall Cavendish Education</p>
                            <p>[This is an automatically generated e-mail. Please do not reply to this e-mail address. Thank you for your co-operation.]</p>
                        </p>
                    </div>'''
                if user_id.language == "zh":
                    subject = '重置密碼'

                    message = '''<div style="margin: 0px; padding: 0px;">
                            <p style="margin: 0px; padding: 0px; font-size: 13px;">
                                親愛的名創教育用戶:
                                <br/><br/>
                                已收到　 閣下要求登入網上賬戶，現特為相關程序提供下列一次性密碼
                                <br/>
                                 <p>
                                 <label style="font-weight:600;">一次性密碼 (OTP)： ''' + str(number) +'''</label><br/>
                                    <br/>
                                請勿向任何人士透露此驗證碼。在此電郵發送10分鐘後，一次性密碼便會失效。若此密碼失
                                 <br/>效，你可再次申請一次性密碼。如有任何查詢，歡迎致電2945 7201與客戶服務熱線聯絡
                                <br/>
                                <p>名創教育　謹啟</p>
                                <p>[此乃經自動系統發出之電子郵件，請勿回覆。多謝合作]</p>
                            </p>
                        </div>'''

                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email_id, ]
                send_mail(subject,
                          message,
                          email_from,
                          recipient_list,
                          html_message=message
                          )
                url = "password/token/" + str(user_id.password_url)
                return Response({"success": True, "message": "Reset OTP Sent", "data": {"submit_url": url},
                                 "token": AuthToken.objects.create(user_id)[1]}, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Please enter a registered Email address",
                                 "data": "Sorry Invalid email"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"success": False, "message": "Please enter a registered Email address", "data": "Sorry Invalid email"},
                            status=status.HTTP_400_BAD_REQUEST)


from accounts.serializers import TokenSerializer
from accounts.models import user
from rest_framework.decorators import api_view


class AccountRegisterVerificationGetOne(generics.ListCreateAPIView):
    """
        Account Register Verification
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = TokenSerializer
    queryset = user.objects.all().order_by('-id')

    @api_view(['POST'])
    def snippet_detail(request, token):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            snippet = user.objects.filter(password_set_url=token).first()
        except user.DoesNotExist:
            return Response({"success": False, "message": "Not Found"},status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            password = request.data.get('password')
            if password:
                snippet.set_password(password)
                pass_url = uuid.uuid4()
                snippet.password_set_url = pass_url
                snippet.save()
                return Response({
                    "success": True,
                    "message": "Password changed",
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "message": "Password reset failed",
                    "data": {

                    },
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": False, "message": "Not Found"},
                        status=status.HTTP_404_NOT_FOUND)


class AccountTokenPasswordVerificationGetOne(generics.ListCreateAPIView):
    """
        Account Token Password Verification
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = TokenSerializer
    queryset = user.objects.all().order_by('-id')

    @api_view(['POST'])
    def snippet_detail(request, token):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            snippet = user.objects.filter(password_url=token).first()
        except user.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            if snippet.otp == request.data.get('otp'):
                pass_url = uuid.uuid4()
                pass_url2 = uuid.uuid4()
                snippet.password_set_url = pass_url
                snippet.otp = pass_url2
                snippet.password_url = pass_url2
                snippet.save()
                url = "password/reset/"+str(snippet.password_set_url)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": {
                        "password_reset_url": url
                    },
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "message": "OTP Verification Failed",
                    "data": {

                    },
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class FormsLoginFrequencyDay(generics.ListCreateAPIView):
    """
        Forms Login Frequency Day
    """


    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            get login frequency details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        import datetime
        from datetime import timedelta

        filter_method = request.data.get('filter')
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        n = 1
        form_data = []
        forms = models.Forms.objects.all()
        for form in forms:
            final_end = today_min
            final_start = today_max
            dataset_value = []
            dataset_label = []
            for x in range(23):
                final_end = final_end + timedelta(hours=n)
                informations = login_frequency.objects.filter(created_date__range=[final_start, final_end], form_id=form.id).count()
                final_start = final_end
                dataset_value.append(informations)
                dataset_label.append(final_end.strftime("%I:%M %p"))
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


class FormsLoginFrequencyWeek(generics.ListCreateAPIView):
    """
        Forms Login Frequency Week
    """

    # permission_classes = (IsAuthenticated,)

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            get login frequency details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        import datetime
        from datetime import timedelta

        filter_method = request.data.get('filter')
        d = datetime.datetime.now()
        dt = d.strftime('%Y-%m-%d')
        datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
        start = datetime_str - timedelta(days=datetime_str.weekday())
        end = start + timedelta(days=6)
        week_min = datetime.datetime.combine(start, datetime.time.min)
        week_max = datetime.datetime.combine(end, datetime.time.max)
        n = 1
        form_data = []
        forms = models.Forms.objects.all()
        for form in forms:
            final_start = week_min
            final_end = week_max
            dataset_value = []
            dataset_label = []
            for x in range(7):
                final_end = final_end + timedelta(hours=24)
                informations = login_frequency.objects.filter(created_date__range=[final_start, final_end], form_id=form.id).count()
                dataset_value.append(informations)
                dataset_label.append(final_start.strftime("%Y:%m %d"))
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

class FormsLoginFrequencyMonth(generics.ListCreateAPIView):
    """
        Forms Login Frequency Month
    """

    # permission_classes = (IsAuthenticated,)

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            get login frequency details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        import datetime
        from datetime import timedelta

        d = datetime.datetime.now()
        dt = d.strftime('%Y-%m-%d')
        datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
        start = datetime_str - timedelta(days=datetime_str.weekday())
        end = start + timedelta(days=6)
        first_date = datetime.datetime(d.year, d.month, 1)
        if d.month == 12:
            last_date = datetime.datetime(d.year + 1, 1, 1) + timedelta(days=-1)
        else:
            last_date = datetime.datetime(d.year, d.month + 1, 1) + timedelta(days=-1)
        delta = last_date - first_date
        form_data = []
        forms = models.Forms.objects.all()
        for form in forms:
            final_start = first_date
            final_end = first_date
            dataset_value = []
            dataset_label = []
            for x in range(delta.days):
                final_end = final_end + timedelta(days=1)
                informations = login_frequency.objects.filter(created_date__range=[final_start, final_end],
                                                              form_id=form.id).count()
                dataset_value.append(informations)
                dataset_label.append(final_start.strftime("%Y:%m %d"))
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

from theme.models import MC
from theme.models import Cards
from advertisement.models import Advertisement
from theme.models import ShortQuestion
from PurchaseOrder.models import PurchaseOrder
from region.models import Forms


class HomeOverviewGraphInfo(generics.ListCreateAPIView):
    """
        Home Overview Graph Info
    """

    # permission_classes = (IsAuthenticated,)

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
        type = request.data.get('type')
        user_count = 0;
        mcs_count = 0;
        short_question_count = 0;
        cards_count = 0;
        ads_count = 0;
        if type == "count":
            user_count = models.user.objects.count()
            mcs_count = MC.objects.count()
            short_question_count = ShortQuestion.objects.count()
            cards_count = Cards.objects.count()
            ads_count = Advertisement.objects.count()
            dict={
                'user_count': user_count,
                'mcs_count': mcs_count,
                'short_question_count': short_question_count,
                'cards_count': cards_count,
                'ads_count': ads_count,
            }
            return Response({
                "success": True,
                "message": "Success",
                "data": dict,
            }, status=status.HTTP_201_CREATED)

        if type == 'download':
            filter_method = request.data.get('filter')
            if filter_method == 'all':
                today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
                today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
                n = 1
                form_data = []
                final_end = today_min
                final_start = today_max
                final_end1 = today_min
                final_start1 = today_max
                dataset_value = []
                dataset_label = []
                for x in range(23):
                    final_end1 = final_end1 + timedelta(hours=n)
                    dataset_label.append(final_end.strftime("%I:%M %p"))

                for x in range(23):
                    final_end = final_end + timedelta(hours=n)
                    informations = PurchaseOrder.objects.filter(created_date__range=[final_start, final_end]).count()
                    final_start = final_end
                    dataset_value.append(informations)
                    dataset_label.append(final_end.strftime("%I:%M %p"))
                form_dict = {
                    'label': dataset_label,
                    'data': dataset_value

                }
                form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                    "label": dataset_label
                }, status=status.HTTP_201_CREATED)

            if filter_method == 'week':
                d = datetime.datetime.now()
                dt = d.strftime('%Y-%m-%d')
                datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
                start = datetime_str - timedelta(days=datetime_str.weekday())
                end = start + timedelta(days=6)
                week_min = datetime.datetime.combine(start, datetime.time.min)
                week_max = datetime.datetime.combine(end, datetime.time.max)
                n = 1
                form_data = []

                final_start = week_min
                final_end = week_min
                dataset_value = []
                dataset_label = []

                final_start1 = week_min
                final_end1 = week_min
                for x in range(7):
                    final_end1 = final_end1 + timedelta(hours=24)
                    dataset_label.append(final_start1.strftime("%a"))
                    final_start1 = final_end1

                for x in range(7):
                    final_end = final_end + timedelta(hours=24)
                    informations = PurchaseOrder.objects.filter(created_date__range=[final_start, final_end]).count()
                    dataset_value.append(informations)
                    dataset_label.append(final_start.strftime("%a"))
                    final_start = final_end
                form_dict = {
                    'label': dataset_label,
                    'data': dataset_value

                }
                form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                    "label": dataset_label
                }, status=status.HTTP_201_CREATED)

            if filter_method == 'month':
                d = datetime.datetime.now()
                dt = d.strftime('%Y-%m-%d')
                datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
                start = datetime_str - timedelta(days=datetime_str.weekday())
                end = start + timedelta(days=6)
                first_date = datetime.datetime(d.year, d.month, 1)
                if d.month == 12:
                    last_date = datetime.datetime(d.year + 1, 1, 1) + timedelta(days=-1)
                else:
                    last_date = datetime.datetime(d.year, d.month + 1, 1) + timedelta(days=-1)

                delta = last_date - first_date
                form_data = []
                final_start = first_date
                final_end = first_date
                dataset_value = []
                dataset_label = []

                final_start1 = first_date
                final_end1 = first_date

                for x in range(delta.days):
                    final_end1 = final_end1 + timedelta(days=1)
                    dataset_label.append(final_start1.strftime("%Y:%m %d"))
                    final_start1 = final_end1

                for x in range(delta.days):
                    final_end = final_end + timedelta(days=1)
                    informations = PurchaseOrder.objects.filter(created_date__range=[final_start, final_end]).count()
                    dataset_value.append(informations)
                    dataset_label.append(final_start.strftime("%Y:%m %d"))
                    final_start = final_end
                form_dict = {
                    'label': dataset_label,
                    'data': dataset_value
                }
                form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                    "label": dataset_label
                }, status=status.HTTP_201_CREATED)

            if filter_method == 'year':
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

                for x in range(12):
                    final_end = final_end + relativedelta(months=1)
                    informations = PurchaseOrder.objects.filter(created_date__range=[final_start, final_end]).count()
                    dataset_value.append(informations)
                    dataset_label.append(final_start.strftime("%b"))
                    final_start = final_end
                form_dict = {
                    'label': dataset_label,
                    'data': dataset_value
                }
                form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                    "label": dataset_label
                }, status=status.HTTP_201_CREATED)

        if type == 'register':

            filter_method = request.data.get('filter')
            if filter_method == 'all':
                today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
                today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
                n = 1
                form_data = []
                forms = Forms.objects.all()

                final_end1 = today_min
                final_start1 = today_max
                dataset_label1 = []
                for x in range(23):
                    final_end1 = final_end1 + timedelta(hours=n)
                    final_start1 = final_end1
                    dataset_label1.append(final_end1.strftime("%I:%M %p"))

                for form in forms:
                    final_end = today_min
                    final_start = today_max
                    dataset_value = []
                    dataset_label = []
                    for x in range(23):
                        final_end = final_end + timedelta(hours=n)
                        informations = models.user.objects.filter(created_date__range=[final_start, final_end],
                                                                        form_id=form.id).count()
                        final_start = final_end
                        dataset_value.append(informations)
                        dataset_label.append(final_end.strftime("%I:%M %p"))
                    form_dict = {
                        'id': form.id,
                        'name': form.name,
                        'label': dataset_label,
                        'data': dataset_value
                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                    "label": dataset_label1
                }, status=status.HTTP_201_CREATED)

            if filter_method == 'week':
                d = datetime.datetime.now()
                dt = d.strftime('%Y-%m-%d')
                datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
                start = datetime_str - timedelta(days=datetime_str.weekday())
                end = start + timedelta(days=6)
                week_min = datetime.datetime.combine(start, datetime.time.min)
                week_max = datetime.datetime.combine(end, datetime.time.max)
                n = 1
                form_data = []
                forms = Forms.objects.all()

                final_start1 = week_min
                final_end1 = week_min
                dataset_label1 = []
                for x in range(7):
                    final_end1 = final_end1 + timedelta(hours=24)
                    dataset_label1.append(final_start1.strftime("%a"))
                    final_start1 = final_end1

                for form in forms:
                    final_start = week_min
                    final_end = week_min
                    dataset_value = []
                    dataset_label = []
                    for x in range(7):
                        final_end = final_end + timedelta(hours=24)
                        informations = models.user.objects.filter(created_date__range=[final_start, final_end],
                                                                        form_id=form.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%a"))
                        final_start = final_end
                    form_dict = {
                        'id': form.id,
                        'name': form.name,
                        'label': dataset_label,
                        'data': dataset_value

                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                    "label": dataset_label1
                }, status=status.HTTP_201_CREATED)

            if filter_method == 'month':
                d = datetime.datetime.now()
                dt = d.strftime('%Y-%m-%d')
                datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
                start = datetime_str - timedelta(days=datetime_str.weekday())
                end = start + timedelta(days=6)
                first_date = datetime.datetime(d.year, d.month, 1)
                if d.month == 12:
                    last_date = datetime.datetime(d.year + 1, 1, 1) + timedelta(days=-1)
                else:
                    last_date = datetime.datetime(d.year, d.month + 1, 1) + timedelta(days=-1)

                delta = last_date - first_date
                form_data = []
                forms = Forms.objects.all()

                final_start1 = first_date
                final_end1 = first_date
                dataset_label1 = []
                for x in range(delta.days):
                    final_end1 = final_end1 + timedelta(days=1)
                    dataset_label1.append(final_start1.strftime("%Y:%m %d"))
                    final_start1 = final_end1

                for form in forms:
                    final_start = first_date
                    final_end = first_date
                    dataset_value = []
                    dataset_label = []
                    for x in range(delta.days):
                        final_end = final_end + timedelta(days=1)
                        informations = models.user.objects.filter(created_date__range=[final_start, final_end],
                                                                        form_id=form.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%Y:%m %d"))
                        final_start = final_end
                    form_dict = {
                        'id': form.id,
                        'name': form.name,
                        'label': dataset_label,
                        'data': dataset_value

                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                    "label": dataset_label1
                }, status=status.HTTP_201_CREATED)

            if filter_method == 'year':
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

                final_start1 = first_date
                final_end1 = first_date
                dataset_label1 = []
                for x in range(12):
                    final_end1 = final_end1 + relativedelta(months=1)
                    dataset_label1.append(final_start1.strftime("%b"))
                    final_start1 = final_end1
                for form in forms:
                    final_start = first_date
                    final_end = first_date
                    dataset_value = []
                    dataset_label = []
                    for x in range(12):
                        final_end = final_end + relativedelta(months=1)
                        informations = models.user.objects.filter(created_date__range=[final_start, final_end],
                                                                        form_id=form.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%b"))
                        final_start = final_end
                    form_dict = {
                        'id': form.id,
                        'name': form.name,
                        'label': dataset_label,
                        'data': dataset_value

                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                    "label": dataset_label1
                }, status=status.HTTP_201_CREATED)


from region .pagination import CustomPagination


class AccountFilterInfo(generics.ListCreateAPIView):
    """
        Account Filter Info
    """

    # permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

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
        purchase_filter = request.data.get('purchased_filter')
        year_filter = request.data.get('year')
        month_filter = request.data.get('month')
        school_id = request.data.get('school_id')
        discount_id = request.data.get('discount_id')
        search = request.data.get('search')
        page_size = request.data.get('show_entries')
        user_list = user.objects.all().values_list('id', flat=True)
        date_user = []
        school_list = []
        discount_list = []
        search_list = []
        selected_users = []

        date_enable = False
        school_enable = False
        discount_enable = False
        search_enable = False

        if year_filter or month_filter:
            try:
                date_enable = True
                if year_filter and not month_filter:
                    date_user1 = user.objects.filter(created_date__year=year_filter).values_list('id', flat=True)
                if month_filter and not year_filter:
                    date_user1 = user.objects.filter(created_date__month=month_filter).values_list('id', flat=True)
                if month_filter and year_filter:

                    from dateutil.relativedelta import relativedelta
                    start_date = str(year_filter) + '-' + str(month_filter) + '-' + '01'
                    last_date = datetime.datetime(year_filter, month_filter + 1, 1) + timedelta(days=-1)
                    start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')
                    date_user1 = user.objects.filter(created_date__range=[start_date, last_date]).values_list('id',
                                                                                                              flat=True)
                date_user = list(date_user1)
            except Exception:
                pass
        if school_id:
            school_enable =True
            try:
                school_list1 = user.objects.filter(school_id=school_id).values_list('id', flat=True)
                school_list = list(school_list1)
            except Exception:
                pass
        if discount_id:
            discount_enable = True
            from discounts.models import DiscountUsage
            try:
                discount_list1 = DiscountUsage.objects.filter(id=discount_id).values_list('user', flat=True)
                discount_list = list(discount_list1)
            except Exception:
                pass
        if search:
            search_enable =True
            try:
                search_list1 = user.objects.filter(Q(firstname__icontains=search) | Q(email__icontains=search) | Q(
                    phone__icontains=search)).values_list('id', flat=True)
                search_list = list(search_list1)
            except Exception:
                pass
        from PurchaseOrder.models import PurchaseOrder
        pre_list = []
        if date_enable:
            pre_list.append(date_user)
        if search_enable:
            pre_list.append(search_list)
        if discount_enable:
            pre_list.append(discount_list)
        if school_enable:
            pre_list.append(school_list)
        result = []
        if not date_enable and not search_enable and not discount_enable and not school_enable:
            if len(pre_list) == 0:
                result.append(list(user_list))
        else:
            result1 = list(set.intersection(*map(set, pre_list)))
            result.append(result1)

        if purchase_filter == "all":
            user_list2 = user.objects.all().values_list('id', flat=True)
            result.append(list(user_list2))
            result = list(set.intersection(*map(set, result)))
            for u in result:
                selected_users.append(u)
        if purchase_filter == "purchased":
            purchase_list1 = PurchaseOrder.objects.all().values_list('partner_id', flat=True)
            result.append(list(purchase_list1))
            result = list(set.intersection(*map(set, result)))
            for p in result:
                selected_users.append(p)
        if purchase_filter == "not_purchased":
            purchase_list1 = PurchaseOrder.objects.all().values_list('partner_id', flat=True)
            result.append(list(purchase_list1))
            result = list(set.difference(*map(set, result)))
            for p in result:
                selected_users.append(p)
        try:
            import math
            if not page_size:
                page_size = 10
            account1 = user.objects.filter(pk__in=selected_users)
            paginator = CustomPagination()
            paginator.page_size = page_size
            account_list = []
            for user_info in account1:
                purchase_date = False
                price = False
                discount_code = False
                try:
                    purchase_date1 = PurchaseOrder.objects.filter(partner_id=user_info.id).order_by('-id')[:10]
                    purchase_date = purchase_date1[0].created_date
                    price = str(purchase_date1[0].price)
                except Exception:
                    pass
                try:
                    purchase_date1 = PurchaseOrder.objects.filter(partner_id=user_info.id).order_by('-id')[:10]
                    discount_code = purchase_date1[0].discount_id.discount_code
                except Exception:
                    pass
                dict = {
                    'id': user_info.id,
                    'firstname': user_info.firstname or False,
                    'lastname': user_info.lastname or False,
                    'email': user_info.email or False,
                    'phone': user_info.phone or False,
                    'registration_date': user_info.registration_date or False,
                    'registration_time': user_info.registration_time or False,
                    'district_name': user_info.district_id.english_name if user_info.district_id else False,
                    'district_id': user_info.district_id.id if user_info.district_id else False,
                    'school_id': user_info.school_id.id if user_info.school_id else False,
                    'school_name': user_info.school_id.school_name if user_info.school_id else False,
                    'school_chinese_name': user_info.school_id.school_chinese_name if user_info.school_id else False,
                    'form_id': user_info.form_id.id if user_info.form_id else False,
                    'form_name': user_info.form_id.name if user_info.form_id else False,
                    'purchase_date': purchase_date,
                    'price': price,
                    'discount_code': discount_code,
                }
                account_list.append(dict)

            result_page = paginator.paginate_queryset(account_list, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(account_list) > 0:
                paginator_data['total_pages'] = math.ceil(len(account_list) / page_size)
            else:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"success": True, "message": "Account Details",
                 "data": paginator_data},
                status=status.HTTP_200_OK)
        except:
            return Response({"success": False, "message": "Something Went Wrong"}, status=status.HTTP_400_BAD_REQUEST)
