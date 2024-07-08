from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
import random
import uuid
from knox.models import AuthToken
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegionSerializers
from .serializers import DistrictSerializers
from .serializers import DistrictSerializersPost
from .serializers import SchoolSerializersPost
from .serializers import SchoolSerializers
from .serializers import AccountSerializers
from .serializers import FormsSerializers
from .serializers import FormsSerializersPost
from .models import Region
from .models import District
from .models import School
from accounts.models import user, RegisterEmailVerify
from .models import Forms
from .models import User_profile
from .models import Address
from PurchaseOrder.models import PurchaseOrder
import logging
from region .pagination import CustomPagination
import math
from deleted_users.models import DeletedUsers
from accounts.models import login_frequency
from Test.models import TestDetails, TestAttendedQuestions
from PurchaseOrder.models import PurchaseOrder
from theme.models import ThemeUsage, UserLearningCardData
from bookmarks.models import MCBookmarks, SQBookmarks, CardsBookmarks
from discounts.models import DiscountUsage

logger = logging.getLogger(__name__)


class regionList(APIView):

    def get(self, request):
        region1 = Region.objects.all()
        serializer = RegionSerializers(region1, many=True)
        return Response(
            {"success": True, "message": "Region Details", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self):
        pass


class distcitList(APIView):

    def get(self, request):
        district1 = District.objects.all()
        serializer = DistrictSerializers(district1, many=True)
        return Response({"success": True, "message": "District Details", "data": serializer.data},
                        status=status.HTTP_200_OK)

    def post(self,request, format=None):
        serializer1 = DistrictSerializersPost(data=request.data)
        if serializer1.is_valid(raise_exception=True):
            district1 = District.objects.filter(region_id=request.data.get('region_id'))
            serializer = DistrictSerializers(district1, many=True)
            return Response({"success": True, "message": "District Details", "data": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Invalid Details", "data": serializer1.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class schoolList(APIView):

    def get(self, request):
        School1 = School.objects.all()
        serializer = SchoolSerializers(School1, many=True)
        return Response({"success": True, "message": "School Details", "data": serializer.data},
                        status=status.HTTP_200_OK)

    def post(self,request, format=None):
        serializer1 = SchoolSerializersPost(data=request.data)
        if serializer1.is_valid():
            school1 = School.objects.filter(region_id=request.data.get('region_id'))
            serializer = SchoolSerializers(school1, many=True)
            return Response({"success": True, "message": "School Details", "data": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Invalid Details", "data": serializer1.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class accountList(APIView):

    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get(self, request):
        try:
            page_size = 10
            account1 = user.objects.all().order_by('id')
            paginator = CustomPagination()
            paginator.page_size = page_size
            result_page = paginator.paginate_queryset(account1, request)
            serializer = AccountSerializers(result_page, many=True)
            paginator_data = paginator.get_paginated_response(serializer.data).data
            if len(account1) > 0:
                paginator_data['total_pages'] = math.ceil(len(account1) / page_size)
            else:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"success": True, "message": "Account Details",
                 "data": paginator_data},
                status=status.HTTP_200_OK)
        except:
            return Response({"success": False, "message": "Something Went Wrong"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        try:
            account1 = user.objects.filter(id=request.data.get('user'))
            serializer = AccountSerializers(account1, many=True)
            import socket
            import re
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            url = request.build_absolute_uri()

            http_layer = request.is_secure() and "https" or "http"
            http_address = request.get_host()
            http_port = request.META['SERVER_PORT']
            urls = str(http_layer + "://" + http_address)
            purchased_data = PurchaseOrder.objects.filter(partner_id=request.data.get('user'))
            is_purchased = False
            if purchased_data:
                is_purchased = True
            dict = {}
            for i in account1:
                dict = {
                    "id": i.id,
                    "password": i.password,
                    "last_login": i.last_login,
                    "is_superuser": i.is_superuser,
                    "email": i.email,
                    "contact": i.contact,
                    "phone": i.phone,
                    "profile_picture": urls + "/media/" + str(i.profile_picture) or False,
                    "firstname": i.firstname,
                    "lastname": i.lastname,
                    "registration_date": i.registration_date,
                    "registration_time": i.registration_time,
                    "created_date": i.created_date,
                    "updated_date": i.updated_date,
                    "role": i.role,
                    "is_purchased": i.is_purchased,
                    "is_active": i.is_active,
                    "is_staff": i.is_staff,
                    "is_admin": i.is_admin,
                    "is_student": i.is_student,
                    "is_teacher": i.is_teacher,
                    "otp": i.otp,
                    "password_url": i.password_url,
                    "password_set_url": i.password_set_url,
                    "district_id": i.district_id.id if i.district_id else False,
                    "district_english_name": i.district_id.english_name if i.district_id else "",
                    "district_chinese_name": i.district_id.chinese_name if i.district_id else "",
                    "region_id": i.region_id.id if i.region_id else False,
                    "school_id": i.school_id.id if i.school_id else False,
                    "school_english_name": i.school_id.school_name if i.school_id else "",
                    "school_chinese_name": i.school_id.school_chinese_name if i.school_id else "",
                    "role_id": i.role_id.id if i.role_id else False,
                    "form_id": i.form_id.id if i.form_id else False,
                    "form_english_name": i.form_id.name if i.form_id else "",
                    "form_chinese_name": i.form_id.chinese_name if i.form_id else "",
                    "address": i.address.id if i.address else False,
                    "profile": i.profile.id if i.profile else False,
                    "groups": [],
                    "user_permissions": []
                }

            return Response({"success": True, "message": "Account Details", "data": dict},
                            status=status.HTTP_200_OK)
        except:
            return Response({"success": False, "message": "Please provide User id"}, status=status.HTTP_400_BAD_REQUEST)


class accountListEdit(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        try:
            success = False
            account1 = user.objects.get(id=request.data.get('user'))

            new_password = False
            if request.data.get('new_password'):
                if request.data.get('password'):
                    success = account1.check_password(request.data.get('password'))
                    if not success:
                        return Response({"success": False, "message": "Incorrect Password"},
                                        status=status.HTTP_400_BAD_REQUEST)
                    else:
                        new_password = True
                else:
                    return Response({"success": False, "message": " Incorrect Password"},
                                    status=status.HTTP_400_BAD_REQUEST)

            district = None
            if request.data.get('district_id'):
                account1.district_id = District.objects.get(id=request.data.get('district_id'))

            region = None
            if request.data.get('region_id'):
                account1.region_id = Region.objects.get(id=request.data.get('region_id'))

            school = None
            if request.data.get('school_id'):
                account1.school_id = School.objects.get(id=request.data.get('school_id'))

            profile = None
            if request.data.get('profile'):
                account1.profile = User_profile.objects.get(id=request.data.get('profile'))

            address = None
            if request.data.get('address'):
                account1.address = Address.objects.get(id=request.data.get('address'))

            form_id = None
            if request.data.get('form_id'):
                account1.form_id = Forms.objects.get(id=request.data.get('form_id'))

            phone = None
            if request.data.get('phone'):
                account1.phone = request.data.get('phone')

            firstname = None
            if request.data.get('firstname'):
                account1.firstname = request.data.get('firstname')

            lastname = None
            if request.data.get('lastname'):
                account1.lastname = request.data.get('lastname')

            if new_password and request.data.get('new_password'):
                account1.set_password(request.data.get('new_password'))

            account1.save()
            return Response({"success": True, "message": "Profile Updated"}, status=status.HTTP_200_OK)
        except:
            return Response({"success": False, "message": "Sorry something went wrong"},
                            status=status.HTTP_400_BAD_REQUEST)


class AccountUpdateEmail(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        try:
            success = False
            account1 = user.objects.get(id=request.data.get('user'))
            number = random.randint(1111, 9999)

            email = None
            if request.data.get('email'):
                current_account = user.objects.exclude(id=request.data.get('user'))
                email_exist = current_account.filter(email=request.data.get('email')).exists()
                if email_exist:
                    return Response({"success": False, "message": "Email Already Registered"},
                                    status=status.HTTP_200_OK)
                else:
                    if account1:
                        pass_url = uuid.uuid4()
                        account1.email_url = pass_url
                        account1.email_otp = number
                        account1.reset_email = request.data.get('email')
                        account1.save()
                        subject = 'Email Address Update'
                        message = '''<div style="margin: 0px; padding: 0px;">
                                <p style="margin: 0px; padding: 0px; font-size: 13px;">
                                    Dear Marshall Cavendish Education User ,
                                    <br/><br/>
                                    Upon your request for online account login, the following OTP has been generated.
                                    <br/>
                                     <p><label style="font-weight:600;">One-Time Password ("OTP"): ''' + str(number) + '''</label><br/>
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

                        if account1.language == "zh":
                            subject = '更新電郵地址'
                            message = '''<div style="margin: 0px; padding: 0px;">
                                    <p style="margin: 0px; padding: 0px; font-size: 13px;">
                                        親愛的名創教育用戶:
                                        <br/><br/>
                                        已收到　 閣下要求登入網上賬戶，現特為相關程序提供下列一次性密碼
                                        <br/>
                                         <p>
                                         <label style="font-weight:600;">一次性密碼 (OTP)： ''' + str(number) + '''</label><br/>
                                            <br/>
                                        請勿向任何人士透露此驗證碼。在此電郵發送10分鐘後，一次性密碼便會失效。若此密碼失
                                         <br/>效，你可再次申請一次性密碼。如有任何查詢，歡迎致電2945 7201與客戶服務熱線聯絡
                                        <br/>
                                        <p>名創教育　謹啟</p>
                                        <p>[此乃經自動系統發出之電子郵件，請勿回覆。多謝合作]</p>
                                    </p>
                                </div>'''

                        firstname = ""
                        if account1.firstname:
                            firstname = account1.firstname
                        message = f'Hi {firstname}, Use the following OTP for update the email address. OTP: {number}'
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [request.data.get('email'), ]
                        send_mail(subject,
                                  message,
                                  email_from,
                                  recipient_list,
                                  html_message=message)
                        url = "account/update/email/" + str(account1.email_url)
                        return Response({"success": True, "message": "Email Reset OTP Sent", "data": {"submit_url": url},
                                         "token": AuthToken.objects.create(account1)[1]},
                                        status=status.HTTP_200_OK)
                    else:
                        return Response(
                            {"success": False, "message": "Fail to Send OTP", "data": "Sorry Invalid email"},
                            status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": True, "message": "Invalid Email"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"success": False, "message": "Sorry something went wrong"},
                            status=status.HTTP_400_BAD_REQUEST)


class EmailResetTokenVerification(APIView):

    permission_classes = (IsAuthenticated,)
    queryset = user.objects.all().order_by('-id')

    @api_view(['POST'])
    def snippet_detail(request, token):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            snippet = user.objects.filter(email_url=token).first()
        except User.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            if str(snippet.email_otp) == str(request.data.get('otp')):
                pass_url = uuid.uuid4()
                pass_url2 = uuid.uuid4()
                snippet.email_url = pass_url
                snippet.email_otp = pass_url2
                snippet.email_url = pass_url2
                snippet.email = request.data.get('email')
                snippet.save()

                return Response({
                    "success": True,
                    "message": "Success",
                    "data": "Profile Updated",
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "message": "OTP Verification Failed",
                    "data": {

                    },
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class RegisterVerifyEmail(APIView):

    # permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        # try:
            success = False
            number = random.randint(1111, 9999)

            email = None
            if request.data.get('email'):
                email_exist = user.objects.filter(email=request.data.get('email')).exists()
                if email_exist:
                    return Response({"success": False, "message": "Email Already Registered"},
                                    status=status.HTTP_200_OK)
                else:
                    if request.data.get('email'):
                        pass_url = uuid.uuid4()

                        email_verify = RegisterEmailVerify.objects.create(email=request.data.get('email'), reset_email=request.data.get('email'),
                                                                          email_otp=number, email_url=pass_url)
                        email_verify.save()
                        subject = 'Email Address Update'
                        message = f'Hi, Use the following OTP for update the email address. OTP: {number}'
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [request.data.get('email'), ]
                        send_mail(subject, message, email_from, recipient_list)
                        url = "account/verify/email/" + str(email_verify.email_url)
                        return Response(
                            {"success": True, "message": "Email Reset OTP Sent", "data": {"submit_url": url},
                             },
                            status=status.HTTP_200_OK)
                    else:
                        return Response(
                            {"success": False, "message": "Fail to Send OTP", "data": "Sorry Invalid email"},
                            status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": True, "message": "Invalid Email"}, status=status.HTTP_400_BAD_REQUEST)
        # except:
        #     return Response({"success": False, "message": "Sorry something went wrong"},
        #                     status=status.HTTP_400_BAD_REQUEST)


class RegisterEmailTokenVerification(APIView):

    # permission_classes = (IsAuthenticated,)
    queryset = user.objects.all().order_by('-id')

    @api_view(['POST'])
    def snippet_detail(request, token):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            snippet = RegisterEmailVerify.objects.filter(email_url=token).first()
        except User.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            if str(snippet.email_otp) == str(request.data.get('otp')):
                pass_url = uuid.uuid4()
                pass_url2 = uuid.uuid4()
                snippet.email_url = pass_url
                snippet.email_otp = pass_url2
                snippet.email_url = pass_url2
                snippet.email = request.data.get('email')
                snippet.save()

                return Response({
                    "success": True,
                    "message": "Success",
                    "data": {"submit_url": request.data.get('email')},
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "message": "OTP Verification Failed",
                    "data": {
                    },
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class accountListEditAdmin(APIView):

    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, format=None):
        try:
            account1 = user.objects.get(id=request.data.get('user'))

            district = None
            if request.data.get('district_id'):
                account1.district_id = District.objects.get(id=request.data.get('district_id'))
            region = None
            if request.data.get('region_id'):
                account1.region_id = Region.objects.get(id=request.data.get('region_id'))
            school = None
            if request.data.get('school_id'):
                account1.school_id = School.objects.get(id=request.data.get('school_id'))
            profile = None
            if request.data.get('profile'):
                account1.profile = User_profile.objects.get(id=request.data.get('profile'))
            address = None
            if request.data.get('address'):
                account1.address = Address.objects.get(id=request.data.get('address'))
            phone = None
            if request.data.get('phone'):
                account1.phone = request.data.get('phone')
            form = None
            if request.data.get('form_id'):
                account1.form_id = Forms.objects.get(id=request.data.get('form_id'))
            email = None
            if request.data.get('email'):
                current_account = user.objects.exclude(id=request.data.get('user'))
                email_exist = current_account.filter(email=request.data.get('email')).exists()
                if email_exist:
                    return Response({"success": False, "message": "Email Already Registered"},
                                    status=status.HTTP_200_OK)
                account1.email = request.data.get('email')
            firstname = None
            if request.data.get('firstname'):
                account1.firstname = request.data.get('firstname')
            lastname = None
            if request.data.get('lastname'):
                account1.lastname = request.data.get('lastname')
            form_id = None
            if request.data.get('form_id'):
                account1.form_id = Forms.objects.get(id=request.data.get('form_id'))
            account1.save()
            return Response({"success": True, "message": "Profile Updated"}, status=status.HTTP_200_OK)
        except:
            return Response({"success": False, "message": "Sorry something went wrong"},
                            status=status.HTTP_400_BAD_REQUEST)


class FormList(APIView):

    def get(self, request):
        form1 = Forms.objects.all()
        serializer = FormsSerializers(form1, many=True)
        return Response({"success": True, "message": "Form Details", "data": serializer.data},
                        status=status.HTTP_200_OK)

    def post(self,request, format=None):
        serializer1 = FormsSerializersPost(data=request.data)
        if serializer1.is_valid():
            form1 = Forms.objects.filter(id=request.data.get('form_id'))
            serializer = FormsSerializers(form1, many=True)
            return Response({"success": True, "message": "Form Details", "data": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Invalid Details", "data": serializer1.errors},
                            status=status.HTTP_400_BAD_REQUEST)


from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
import random


class DeleteUserViewApi(APIView):

    def post(self, request, format=None):
        try:
            if user.objects.filter(id=request.data.get('user')):
                user_id = user.objects.get(id=request.data.get('user'))
                if user_id:

                    login_frequency_data = login_frequency.objects.filter(user_id=user_id)
                    test_details_data = TestDetails.objects.filter(partner_id=user_id)
                    test_attended_questions_data = TestAttendedQuestions.objects.filter(partner_id=user_id)
                    purchase_order_data = PurchaseOrder.objects.filter(partner_id=user_id)
                    theme_usage_data = ThemeUsage.objects.filter(user_id=user_id)
                    user_learning_card_data = UserLearningCardData.objects.filter(partner_id=user_id)
                    mc_bookmarks_data = MCBookmarks.objects.filter(partner_id=user_id)
                    sq_bookmarks_data = SQBookmarks.objects.filter(partner_id=user_id)
                    cards_bookmarks_data = CardsBookmarks.objects.filter(partner_id=user_id)
                    discount_usage_data = DiscountUsage.objects.filter(user=user_id)
                    user_email = user_id.email
                    print("user_id_srt", user_email)
                    deleted_user_data = DeletedUsers.objects.create(email=user_id.email,
                                                contact=user_id.contact,
                                                phone=user_id.phone,
                                                profile_picture=user_id.profile_picture,
                                                firstname=user_id.firstname,
                                                lastname=user_id.lastname,
                                                registration_date=user_id.registration_date,
                                                registration_time=user_id.registration_time,
                                                created_date=user_id.created_date,
                                                updated_date=user_id.updated_date,
                                                is_purchased=user_id.is_purchased,
                                                is_staff=user_id.is_staff,
                                                is_admin=user_id.is_admin,
                                                is_student=user_id.is_student,
                                                is_teacher=user_id.is_teacher,
                                                district_id=user_id.district_id,
                                                region_id=user_id.region_id,
                                                school_id=user_id.school_id,
                                                role_id=user_id.role_id,
                                                form_id=user_id.form_id,
                                                language=user_id.language,
                                                user_id=user_id.id).save()
                    print("user_id_srt", user_email)
                    deleted_user_value = DeletedUsers.objects.get(email=user_email)
                    print("asdsad", deleted_user_value)
                    if login_frequency_data:
                        for i in login_frequency_data:
                            i.deleted_user_id = deleted_user_value
                            i.save()
                    if test_details_data:
                        for i in test_details_data:
                            i.deleted_user_id = deleted_user_value
                            i.save()
                    if test_attended_questions_data:
                        for i in test_attended_questions_data:
                            i.deleted_user_id = deleted_user_value
                            i.save()
                    if purchase_order_data:
                        for i in purchase_order_data:
                            i.deleted_user_id = deleted_user_value
                            i.save()
                    if theme_usage_data:
                        for i in theme_usage_data:
                            i.deleted_user_id = deleted_user_value
                            i.save()
                    if user_learning_card_data:
                        for i in user_learning_card_data:
                            i.deleted_user_id = deleted_user_value
                            i.save()
                    if mc_bookmarks_data:
                        for i in mc_bookmarks_data:
                            i.deleted_user_id = deleted_user_value
                            i.save()
                    if sq_bookmarks_data:
                        for i in sq_bookmarks_data:
                            i.deleted_user_id = deleted_user_value
                            i.save()
                    if cards_bookmarks_data:
                        for i in cards_bookmarks_data:
                            i.deleted_user_id = deleted_user_value
                            i.save()
                    if discount_usage_data:
                        for i in discount_usage_data:
                            i.deleted_user_id = deleted_user_value
                            i.save()
                    user_id.delete()
                    return Response({"success": True, "message": 'User Deleted'}, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": 'User not found in the system'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, "message": 'User not found in the system'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"success": False, "message": 'Sorry something went wrong'},
                            status=status.HTTP_400_BAD_REQUEST)


class RecoverUserViewApi(APIView):
    """
    Api for recovering deleted user.
    """
    def post(self, request, formate=None):
        try:
            print(request.data.get('email'))
            if DeletedUsers.objects.filter(email=request.data.get('email')):
                del_user_id = DeletedUsers.objects.get(email=request.data.get('email'))
                if del_user_id:
                    print("deleted user ============> ", del_user_id)
                    login_frequency_data = login_frequency.objects.filter(deleted_user_id=del_user_id)
                    test_details_data = TestDetails.objects.filter(deleted_user_id=del_user_id)
                    test_attended_questions_data = TestAttendedQuestions.objects.filter(deleted_user_id=del_user_id)
                    purchase_order_data = PurchaseOrder.objects.filter(deleted_user_id=del_user_id)
                    theme_usage_data = ThemeUsage.objects.filter(deleted_user_id=del_user_id)
                    user_learning_card_data = UserLearningCardData.objects.filter(deleted_user_id=del_user_id)
                    mc_bookmarks_data = MCBookmarks.objects.filter(deleted_user_id=del_user_id)
                    sq_bookmarks_data = SQBookmarks.objects.filter(deleted_user_id=del_user_id)
                    cards_bookmarks_data = CardsBookmarks.objects.filter(deleted_user_id=del_user_id)
                    discount_usage_data = DiscountUsage.objects.filter(deleted_user_id=del_user_id)
                    user_email = del_user_id.email
                    print("del_user_id_srt", user_email)
                    restored_user_data = user.objects.create(email=del_user_id.email,
                                                             contact=del_user_id.contact,
                                                             phone=del_user_id.phone,
                                                             profile_picture=del_user_id.profile_picture,
                                                             firstname=del_user_id.firstname,
                                                             lastname=del_user_id.lastname,
                                                             registration_date=del_user_id.registration_date,
                                                             registration_time=del_user_id.registration_time,
                                                             created_date=del_user_id.created_date,
                                                             updated_date=del_user_id.updated_date,
                                                             is_purchased=del_user_id.is_purchased,
                                                             is_staff=del_user_id.is_staff,
                                                             is_admin=del_user_id.is_admin,
                                                             is_student=del_user_id.is_student,
                                                             is_teacher=del_user_id.is_teacher,
                                                             district_id=del_user_id.district_id,
                                                             region_id=del_user_id.region_id,
                                                             school_id=del_user_id.school_id,
                                                             role_id=del_user_id.role_id,
                                                             form_id=del_user_id.form_id,
                                                             language=del_user_id.language)
                    restored_user_data.save()
                    restored_user_value = user.objects.get(email=user_email)
                    print("restored_user_value", restored_user_value)
                    if login_frequency_data:
                        for i in login_frequency_data:
                            i.user_id = restored_user_value
                            i.save()
                    if test_details_data:
                        for i in test_details_data:
                            i.partner_id = restored_user_value
                            i.save()
                    if test_attended_questions_data:
                        for i in test_attended_questions_data:
                            i.partner_id = restored_user_value
                            i.save()
                    if purchase_order_data:
                        for i in purchase_order_data:
                            i.partner_id = restored_user_value
                            i.save()
                    if theme_usage_data:
                        for i in theme_usage_data:
                            i.user_id = restored_user_value
                            i.save()
                    if user_learning_card_data:
                        for i in user_learning_card_data:
                            i.partner_id = restored_user_value
                            i.save()
                    if mc_bookmarks_data:
                        for i in mc_bookmarks_data:
                            i.partner_id = restored_user_value
                            i.save()
                    if sq_bookmarks_data:
                        for i in sq_bookmarks_data:
                            i.partner_id = restored_user_value
                            i.save()
                    if cards_bookmarks_data:
                        for i in cards_bookmarks_data:
                            i.partner_id = restored_user_value
                            i.save()
                    if discount_usage_data:
                        for i in discount_usage_data:
                            i.user = restored_user_value
                            i.save()
                    del_user_id.delete()
                    return Response({"success": True, "message": 'User Restored Successfully',
                                     "user_id": user.objects.get(email=request.data.get('email')).id
                                     },
                                     status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": 'User not found in the system'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, "message": 'User not found in the system'},
                                status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"success": False, "message": 'Sorry something went wrong'},
                            status=status.HTTP_400_BAD_REQUEST)


class DeleteMultiUserViewApi(APIView):

    def post(self, request, format=None):
        try:
            if request.data.get('users'):
                for user_list in request.data.get('users'):
                    if user.objects.filter(id=user_list):
                        user_id = user.objects.get(id=user_list)
                        if user_id:
                            user_id.delete()
                        else:
                            return Response({"success": False, "message": 'Some of the users not found in the system'},
                                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"success": False, "message": 'Some of the users not found in the system'},
                                        status=status.HTTP_400_BAD_REQUEST)
                return Response({"success": True, "message": 'User Deleted'}, status=status.HTTP_200_OK)
        except:
            return Response({"success": False, "message": 'Sorry something went wrong'},
                            status=status.HTTP_400_BAD_REQUEST)


class SchoolRegionList(generics.ListCreateAPIView):
    """
        List and Create cardtitle / card
    """

    permission_classes = (IsAuthenticated,)

    @api_view(['GET'])
    def snippet_detail(request):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            import math
            page_size = 10
            paginator = CustomPagination()
            paginator.page_size = page_size

            region_list = []
            region_data = Region.objects.all()
            school_seq = 1
            for region in region_data.iterator():
                district_list = []
                districts_data = District.objects.filter(region_id=region.id)
                for district in districts_data:
                    school_list = []
                    school_data = School.objects.filter(region_id=region.id, district_id=district.id)
                    for school in school_data:
                        school_dict = {
                            "id": school.id,
                            "school_name": school.school_name if school.school_name else False,
                            "school_chinese_name": school.school_chinese_name if school.school_chinese_name else False,
                            "region_id": school.region_id.id if school.region_id else False,
                            "region_name": school.region_id.english_name if school.region_id else False,
                            "district_id": school.district_id.id if school.district_id else False,
                            "district_name": school.district_id.english_name if school.district_id else False,
                            "created_date": str(school.created_date),
                            "updated_date": str(school.updated_date),
                            "school_seq": school_seq
                        }
                        school_list.append(school_dict)
                        school_seq = school_seq + 1
                    district_dict = {
                        "id": district.id,
                        "chinese_name": district.chinese_name,
                        "english_name": district.english_name,
                        "region_id": district.region_id.id,
                        "region_name": district.region_id.english_name if district.region_id else False,
                        "created_date": str(district.created_date),
                        "updated_date": str(district.updated_date),
                        "schools": school_list if school_list else False
                    }
                    if school_list:
                        district_list.append(district_dict)
                region_dict = {
                    "id": region.id,
                    "chinese_name": region.chinese_name,
                    "english_name": region.english_name,
                    "created_date": str(region.created_date),
                    "updated_date": str(region.updated_date),
                    "districts": district_list if district_list else False
                }
                if district_list:
                    region_list.append(region_dict)

            result_page = paginator.paginate_queryset(region_list, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(region_list) > 0:
                paginator_data['total_pages'] = math.ceil(len(region_list) / page_size)
            else:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "success": True,
                "message": "Success",
                "data": paginator_data,
            }, status=status.HTTP_200_OK)
        except Region.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class SchoolRegionCreate(generics.ListCreateAPIView):
    """
        List and Create cardtitle / card
    """

    permission_classes = (IsAuthenticated,)
    queryset = School.objects.all().order_by('-id')

    def get_user(self):
        return self.request.user

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

    def post(self, request, *args, **kwargs):
        """
            create Theme details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        serializer = SchoolSerializers(data=request.data, context={"user": self.get_user()})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        """
        Updates snippets delete
        :param kwargs: snippets id
        :return: message
        """
        pk = request.data.get('id')
        snippets = self.get_object(pk)
        serializer = SchoolSerializers(instance=snippets, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

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
        return Response({"success": False, "message": "Not Found"},
                        status=status.HTTP_404_NOT_FOUND)


class SchoolRegionForm(APIView):
    """
        List and Create cardtitle / card
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            school_id = request.data.get('id')
            school_list = []
            school_data = School.objects.filter(id=school_id)
            for school in school_data:
                school_dict = {
                    "id": school.id,
                    "school_name": school.school_name if school.school_name else False,
                    "school_chinese_name": school.school_chinese_name if school.school_chinese_name else False,
                    "region_id": school.region_id.id if school.region_id else False,
                    "region_name": school.region_id.english_name if school.region_id else False,
                    "district_id": school.district_id.id if school.district_id else False,
                    "district_name": school.district_id.english_name if school.district_id else False,
                    "created_date": str(school.created_date),
                    "updated_date": str(school.updated_date)
                }
                school_list.append(school_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": school_list,
            }, status=status.HTTP_200_OK)
        except Region.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

