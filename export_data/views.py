from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts import serializers, models
import datetime
from PurchaseOrder.models import PurchaseOrder
from accounts.models import user
from deleted_users.models import DeletedUsers
from discounts.models import DiscountUsage
from theme.models import UserLearningCardData, ThemeUsage
from Test.models import TestAttendedQuestions, TestDetails
from collections import defaultdict
from bs4 import BeautifulSoup
import time


class StudentDataExport(generics.ListCreateAPIView):
    """
        Student Data Export
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    queryset = models.user.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Export to Excel
        """
        try:
            deleted_users = DeletedUsers.objects.all()
            users = models.user.objects.all()
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            if start_date and end_date:
                users = models.user.objects.filter(registration_date__range=[start_date, end_date])
                deleted_users = DeletedUsers.objects.filter(registration_date__range=[start_date, end_date])
            elif start_date:
                users = models.user.objects.filter(registration_date__range=[start_date, datetime.date.today()])
                deleted_users = DeletedUsers.objects.filter(registration_date__range=[start_date, datetime.date.today()])
            elif end_date:
                default_start_date = datetime.datetime.strptime('2014-12-04', '%Y-%m-%d').date()
                users = models.user.objects.filter(registration_date__range=[default_start_date, end_date])
                deleted_users = DeletedUsers.objects.filter(registration_date__range=[default_start_date, end_date])
            student_id_list = [["Student ID (#)", "Student Name", "Email", "Phone",
                                "District", "School", "Form", "Registration Date",
                                "Purchase Date", "Price", "Discount Code"]]
            if users:
                for i in users:
                    purchase_date = ""
                    purchase_price = ""
                    discount_code = ""
                    purchase_order = PurchaseOrder.objects.filter(partner_id=i.id).order_by('id').first()
                    if purchase_order:
                        purchase_date = purchase_order.created_date
                        purchase_price = purchase_order.price if purchase_order.price else ""
                        discount_code = purchase_order.discount_id.discount_code if purchase_order.discount_id else ""
                    student_id_list.append([
                        i.id if i.id else "",
                        i.firstname if i.firstname else "",
                        i.email if i.email else "",
                        i.phone if i.phone else "",
                        i.district_id.english_name if i.district_id else "",
                        i.school_id.school_name if i.school_id else "",
                        i.form_id.name if i.form_id else "",
                        str(i.registration_date) if i.registration_date else "",
                        str(purchase_date) if purchase_date else "",
                        str(purchase_price) if purchase_price else "",
                        discount_code if discount_code else ""
                    ])
            if deleted_users:
                for i in deleted_users:
                    purchase_date = ""
                    purchase_price = ""
                    discount_code = ""
                    purchase_order = PurchaseOrder.objects.filter(deleted_user_id=i).first()
                    if purchase_order:
                        purchase_date = purchase_order.created_date
                        purchase_price = purchase_order.price if purchase_order.price else ""
                        discount_code = purchase_order.discount_id.discount_code if purchase_order.discount_id else ""
                    student_id_list.append([
                        i.user_id if i.user_id else "",
                        i.firstname if i.firstname else "",
                        i.email if i.email else "",
                        i.phone if i.phone else "",
                        i.district_id.english_name if i.district_id else "",
                        i.school_id.school_name if i.school_id else "",
                        i.form_id.name if i.form_id else "",
                        str(i.registration_date) if i.registration_date else "",
                        str(purchase_date) if purchase_date else "",
                        str(purchase_price) if purchase_price else "",
                        discount_code if discount_code else ""
                    ])
            if users or deleted_users:
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": student_id_list,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found"},
                                status=status.HTTP_404_NOT_FOUND)
        except models.user.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class UserDataExport(generics.ListCreateAPIView):
    """
        Student Data Export
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    queryset = models.user.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Export to Excel
        """
        import datetime
        from datetime import timedelta
        purchase_filter = request.data.get('purchased_filter')
        year_filter = request.data.get('year')
        month_filter = request.data.get('month')
        school_id = request.data.get('school_id')
        discount_id = request.data.get('discount_id')
        search = request.data.get('search')
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
            school_enable = True
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
            search_enable = True
            try:
                search_list1 = user.objects.filter(firstname__icontains=search).values_list('id', flat=True)
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
            page_size = 10
            account1 = user.objects.filter(pk__in=selected_users)

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



            student_id_list = [["Student ID (#)", "Student Name", "Email", "Phone",
                                "District", "School", "Form", "Registration Date",
                                "Purchase Date", "Price", "Discount Code"]]
            if account_list:
                for i in account_list:
                    purchase_date = ""
                    purchase_price = ""
                    discount_code = ""
                    purchase_order = PurchaseOrder.objects.filter(partner_id=i.get("id")).order_by('id').first()
                    if purchase_order:
                        purchase_date = purchase_order.created_date
                        purchase_price = purchase_order.price if purchase_order.price else ""
                        discount_code = purchase_order.discount_id.discount_code if purchase_order.discount_id else ""
                    student_id_list.append([
                        i.get("id") if i.get("id") else "",
                        i.get("firstname") if i.get("firstname") else "",
                        i.get("email") if i.get("email") else "",
                        i.get("phone") if i.get("phone") else "",
                        i.get("district_name") if i.get("district_id") else "",
                        i.get("school_name") if i.get("school_id") else "",
                        i.get("form_id") if i.get("form_id") else "",
                        str(i.get("registration_date")) if i.get("registration_date") else "",
                        str(purchase_date) if purchase_date else "",
                        str(purchase_price) if purchase_price else "",
                        discount_code if discount_code else ""
                    ])

            if account_list:
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": student_id_list,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found"},
                                status=status.HTTP_404_NOT_FOUND)
        except models.user.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class LearningCardDataExport(generics.ListCreateAPIView):
    """
        Learning Card Data Export
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    queryset = models.user.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Export to Excel
        """
        try:
            users = models.user.objects.all()
            student_id_list = [[
                "Student ID (#)", "Student Name", "Email", "Phone", "District", "School", "Form",
                "Theme (Chinese)", "Theme (English)", "Topic (Chinese)", "Topic (English)",
                "Title (Chinese)", "Title (English)", "Subtitle (Chinese)", "Subtitle (English)",
                "Card Number", "Summary Title (Chinese)", "Summary Title (English)",
                "Summary (Chinese)", "Summary (English)", "Attempt",
            ]]

            students = []
            partner_id_list = []
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')

            learning_card_data = UserLearningCardData.objects.order_by('partner_id')

            if start_date and end_date:
                learning_card_data = UserLearningCardData.objects.filter(created_date__range=[start_date, end_date])
            elif start_date:
                learning_card_data = UserLearningCardData.objects.filter(created_date__range=[start_date,
                                                                                              datetime.date.today()])
            elif end_date:
                default_start_date = datetime.datetime.strptime('2014-12-04', '%Y-%m-%d').date()
                learning_card_data = UserLearningCardData.objects.filter(created_date__range=[default_start_date,
                                                                                              end_date])

            for result in learning_card_data:
                students.append(result)
            if students:
                for i in students:
                    card_chinese_summary = ""
                    card_english_summary = ""
                    if i.card_id.card_chinese_summary:
                        card_chinese_summary = BeautifulSoup(i.card_id.card_chinese_summary, "lxml")
                    if i.card_id.card_english_summary:
                        card_english_summary = BeautifulSoup(i.card_id.card_english_summary, "lxml")
                    if i.partner_id:
                        student_id_list.append([
                            i.partner_id.id if i.partner_id else "",
                            i.partner_id.firstname if i.partner_id else "",
                            i.partner_id.email if i.partner_id else "",
                            i.partner_id.phone if i.partner_id else "",
                            i.partner_id.district_id.english_name if i.partner_id.district_id else "",
                            i.partner_id.school_id.school_name if i.partner_id.school_id else "",
                            i.partner_id.form_id.name if i.partner_id.form_id else "",
                            i.card_id.card_title_id.theme_id.theme_chinese_name if i.card_id.card_title_id.theme_id else "",
                            i.card_id.card_title_id.theme_id.theme_english_name if i.card_id.card_title_id.theme_id else "",
                            i.card_id.card_title_id.topic_id.topic_chinese_name if i.card_id.card_title_id.topic_id else "",
                            i.card_id.card_title_id.topic_id.topic_english_name if i.card_id.card_title_id.topic_id else "",
                            i.card_id.card_title_id.card_chinese_title if i.card_id.card_title_id else "",
                            i.card_id.card_title_id.card_english_title if i.card_id.card_title_id else "",
                            i.card_id.card_title_id.card_chinese_subtitle if i.card_id.card_title_id else "",
                            i.card_id.card_title_id.card_english_subtitle if i.card_id.card_title_id else "",
                            i.card_id.id if i.card_id else "",
                            i.card_id.card_chinese_summary_title if i.card_id else "",
                            i.card_id.card_english_summary_title if i.card_id else "",
                            card_chinese_summary.get_text(),
                            card_english_summary.get_text(),
                            "10" if i.card_id else "",
                        ])
                    elif i.deleted_user_id:
                        student_id_list.append([
                            i.deleted_user_id.user_id if i.deleted_user_id else "",
                            i.deleted_user_id.firstname if i.deleted_user_id else "",
                            i.deleted_user_id.email if i.deleted_user_id else "",
                            i.deleted_user_id.phone if i.deleted_user_id else "",
                            i.deleted_user_id.district_id.english_name if i.deleted_user_id.district_id else "",
                            i.deleted_user_id.school_id.school_name if i.deleted_user_id.school_id else "",
                            i.deleted_user_id.form_id.name if i.deleted_user_id.form_id else "",
                            i.card_id.card_title_id.theme_id.theme_chinese_name if i.card_id.card_title_id.theme_id else "",
                            i.card_id.card_title_id.theme_id.theme_english_name if i.card_id.card_title_id.theme_id else "",
                            i.card_id.card_title_id.topic_id.topic_chinese_name if i.card_id.card_title_id.topic_id else "",
                            i.card_id.card_title_id.topic_id.topic_english_name if i.card_id.card_title_id.topic_id else "",
                            i.card_id.card_title_id.card_chinese_title if i.card_id.card_title_id else "",
                            i.card_id.card_title_id.card_english_title if i.card_id.card_title_id else "",
                            i.card_id.card_title_id.card_chinese_subtitle if i.card_id.card_title_id else "",
                            i.card_id.card_title_id.card_english_subtitle if i.card_id.card_title_id else "",
                            i.card_id.id if i.card_id else "",
                            i.card_id.card_chinese_summary_title if i.card_id else "",
                            i.card_id.card_english_summary_title if i.card_id else "",
                            card_chinese_summary.get_text(),
                            card_english_summary.get_text(),
                            "10" if i.card_id else "",
                        ])
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": student_id_list,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except models.user.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class QuestionsDataExport(generics.ListCreateAPIView):
    """
        Questions Data Export
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    queryset = models.user.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Export to Excel
        """
        try:
            users = models.user.objects.all()
            student_id_list = [[
                "Student ID (#)", "Student Name", "Email", "Phone", "District", "School", "Form",
                "Theme (Chinese)", "Theme (English)", "Topic (Chinese)", "Topic (English)",
                "Learning Focus (Chinese)", "Learning Focus (English)", "Question Type (MC/SQ)", "Question (Chinese)",
                "Question (English)", "Source Reference", "Answer",
                "Correct Answer (Chinese)", "Correct Answer (English)", 'Score', "Attempt",
            ]]

            students = []

            test_data = TestAttendedQuestions.objects.order_by('partner_id')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')

            if start_date and end_date:
                test_data = TestAttendedQuestions.objects.filter(created_date__range=[start_date, end_date])
            elif start_date:
                test_data = TestAttendedQuestions.objects.filter(created_date__range=[start_date,
                                                                                      datetime.date.today()])
            elif end_date:
                default_start_date = datetime.datetime.strptime('2014-12-04', '%Y-%m-%d').date()
                test_data = TestAttendedQuestions.objects.filter(created_date__range=[default_start_date,
                                                                                      end_date])
            for result in test_data:
                students.append(result)
            if students:
                for i in students:
                    if i.is_mc:
                        mc_chinese_question = ""
                        mc_english_question = ""
                        if i.mc_id.mc_chinese_question:
                            mc_chinese_question = BeautifulSoup(i.mc_id.mc_chinese_question, "lxml")
                        if i.mc_id.mc_english_question:
                            mc_english_question = BeautifulSoup(i.mc_id.mc_english_question, "lxml")
                        if i.partner_id:
                            student_id_list.append([
                                i.partner_id.id if i.partner_id else "",
                                i.partner_id.firstname if i.partner_id else "",
                                i.partner_id.email if i.partner_id else "",
                                i.partner_id.phone if i.partner_id else "",
                                i.partner_id.district_id.english_name if i.partner_id.district_id else "",
                                i.partner_id.school_id.school_name if i.partner_id.school_id else "",
                                i.partner_id.form_id.name if i.partner_id.form_id else "",
                                i.mc_id.theme_id.theme_chinese_name if i.mc_id.theme_id else "",
                                i.mc_id.theme_id.theme_english_name if i.mc_id.theme_id else "",
                                i.mc_id.topic_id.topic_chinese_name if i.mc_id.topic_id else "",
                                i.mc_id.topic_id.topic_english_name if i.mc_id.topic_id else "",
                                i.mc_id.learning_focus_id.english if i.mc_id.learning_focus_id else "",
                                i.mc_id.learning_focus_id.chinese if i.mc_id.learning_focus_id else "",
                                "MC",
                                mc_chinese_question.get_text(),
                                mc_english_question.get_text(),
                                i.mc_id.mc_english_source_ref if i.mc_id else "",
                                i.answer if i.answer else "",
                                i.mc_id.answer if i.mc_id else "",
                                i.mc_id.answer if i.mc_id else "",
                                i.mc_id.total_mark if i.mc_id else "",
                                "1" if i.mc_id else "",
                            ])
                        elif i.deleted_user_id:
                            student_id_list.append([
                                i.deleted_user_id.user_id if i.deleted_user_id else "",
                                i.deleted_user_id.firstname if i.deleted_user_id else "",
                                i.deleted_user_id.email if i.deleted_user_id else "",
                                i.deleted_user_id.phone if i.deleted_user_id else "",
                                i.deleted_user_id.district_id.english_name if i.deleted_user_id.district_id else "",
                                i.deleted_user_id.school_id.school_name if i.deleted_user_id.school_id else "",
                                i.deleted_user_id.form_id.name if i.deleted_user_id.form_id else "",
                                i.mc_id.theme_id.theme_chinese_name if i.mc_id.theme_id else "",
                                i.mc_id.theme_id.theme_english_name if i.mc_id.theme_id else "",
                                i.mc_id.topic_id.topic_chinese_name if i.mc_id.topic_id else "",
                                i.mc_id.topic_id.topic_english_name if i.mc_id.topic_id else "",
                                i.mc_id.learning_focus_id.english if i.mc_id.learning_focus_id else "",
                                i.mc_id.learning_focus_id.chinese if i.mc_id.learning_focus_id else "",
                                "MC",
                                mc_chinese_question.get_text(),
                                mc_english_question.get_text(),
                                i.mc_id.mc_english_source_ref if i.mc_id else "",
                                i.answer if i.answer else "",
                                i.mc_id.answer if i.mc_id else "",
                                i.mc_id.answer if i.mc_id else "",
                                i.mc_id.total_mark if i.mc_id else "",
                                "1" if i.mc_id else "",
                            ])
                    elif i.is_sq:
                        sq_chinese_question = ""
                        sq_english_question = ""
                        sq_chinese_suggested_answer = ""
                        sq_english_suggested_answer = ""
                        if i.sq_id.sq_chinese_question:
                            sq_chinese_question = BeautifulSoup(i.sq_id.sq_chinese_question, "lxml")
                        if i.sq_id.sq_english_question:
                            sq_english_question = BeautifulSoup(i.sq_id.sq_english_question, "lxml")
                        if i.sq_id.sq_chinese_suggested_answer:
                            sq_chinese_suggested_answer = BeautifulSoup(i.sq_id.sq_chinese_suggested_answer,
                                                                        "lxml")
                        if i.sq_id.sq_english_suggested_answer:
                            sq_english_suggested_answer = BeautifulSoup(i.sq_id.sq_english_suggested_answer,
                                                                        "lxml")
                        if i.partner_id:
                            student_id_list.append([
                                i.partner_id.id if i.partner_id else "",
                                i.partner_id.firstname if i.partner_id else "",
                                i.partner_id.email if i.partner_id else "",
                                i.partner_id.phone if i.partner_id else "",
                                i.partner_id.district_id.english_name if i.partner_id.district_id else "",
                                i.partner_id.school_id.school_name if i.partner_id.school_id else "",
                                i.partner_id.form_id.name if i.partner_id.form_id else "",
                                i.sq_id.theme_id.theme_chinese_name if i.sq_id.theme_id else "",
                                i.sq_id.theme_id.theme_english_name if i.sq_id.theme_id else "",
                                i.sq_id.topic_id.topic_chinese_name if i.sq_id.topic_id else "",
                                i.sq_id.topic_id.topic_english_name if i.sq_id.topic_id else "",
                                i.sq_id.learning_focus_id.english if i.sq_id.learning_focus_id else "",
                                i.sq_id.learning_focus_id.chinese if i.sq_id.learning_focus_id else "",
                                "SQ",
                                sq_chinese_question.get_text(),
                                sq_english_question.get_text(),
                                i.sq_id.sq_english_source_ref if i.sq_id else "",
                                i.answer if i.answer else "",
                                sq_chinese_suggested_answer.get_text(),
                                sq_english_suggested_answer.get_text(),
                                i.sq_id.sq_total_mark if i.sq_id else "",
                                "1" if i.sq_id else "",
                            ])
                        elif i.deleted_user_id:
                            student_id_list.append([
                                i.deleted_user_id.user_id if i.deleted_user_id else "",
                                i.deleted_user_id.firstname if i.deleted_user_id else "",
                                i.deleted_user_id.email if i.deleted_user_id else "",
                                i.deleted_user_id.phone if i.deleted_user_id else "",
                                i.deleted_user_id.district_id.english_name if i.deleted_user_id.district_id else "",
                                i.deleted_user_id.school_id.school_name if i.deleted_user_id.school_id else "",
                                i.deleted_user_id.form_id.name if i.deleted_user_id.form_id else "",
                                i.sq_id.theme_id.theme_chinese_name if i.sq_id.theme_id else "",
                                i.sq_id.theme_id.theme_english_name if i.sq_id.theme_id else "",
                                i.sq_id.topic_id.topic_chinese_name if i.sq_id.topic_id else "",
                                i.sq_id.topic_id.topic_english_name if i.sq_id.topic_id else "",
                                i.sq_id.learning_focus_id.english if i.sq_id.learning_focus_id else "",
                                i.sq_id.learning_focus_id.chinese if i.sq_id.learning_focus_id else "",
                                "SQ",
                                sq_chinese_question.get_text(),
                                sq_english_question.get_text(),
                                i.sq_id.sq_english_source_ref if i.sq_id else "",
                                i.answer if i.answer else "",
                                sq_chinese_suggested_answer.get_text(),
                                sq_english_suggested_answer.get_text(),
                                i.sq_id.sq_total_mark if i.sq_id else "",
                                "1" if i.sq_id else "",
                            ])
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": student_id_list,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except models.user.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class LoginStatistics(generics.ListCreateAPIView):
    """
        Login Statistics
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    queryset = models.user.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Export to Excel
        """
        try:
            filter_method = request.data.get('filter')
            if filter_method == "day":
                login_frequency = models.login_frequency.objects.all().order_by('created_date')
                today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
                today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

                if today_min and today_max:
                    login_frequency = models.login_frequency.objects.filter(Q(created_date__range=[today_min, today_max]) & Q(user_id__is_student=True)).order_by('created_date')
                student_id_list = [["Student ID (#)", "Student Name", "Email", "Phone",
                                    "District", "School", "Form", "Login Date", "Login Time"]]
                if login_frequency:
                    for i in login_frequency:
                        if i.user_id.is_student:
                            login_time = i.login_time
                            login_time_val = login_time.strftime("%H:%M")
                            if i.user_id:
                                student_id_list.append([
                                    i.user_id.id if i.user_id else "",
                                    i.user_id.firstname if i.user_id else "",
                                    i.user_id.email if i.user_id else "",
                                    i.user_id.phone if i.user_id else "",
                                    i.user_id.district_id.english_name if i.user_id.district_id else "",
                                    i.user_id.school_id.school_name if i.user_id.school_id else "",
                                    i.user_id.form_id.name if i.user_id.form_id else "",
                                    i.login_date if i.login_date else "",
                                    login_time_val if login_time_val else "",
                                ])
                            elif i.deleted_user_id:
                                student_id_list.append([
                                    i.deleted_user_id.user_id if i.deleted_user_id else "",
                                    i.deleted_user_id.firstname if i.deleted_user_id else "",
                                    i.deleted_user_id.email if i.deleted_user_id else "",
                                    i.deleted_user_id.phone if i.deleted_user_id else "",
                                    i.deleted_user_id.district_id.english_name if i.deleted_user_id.district_id else "",
                                    i.deleted_user_id.school_id.school_name if i.deleted_user_id.school_id else "",
                                    i.deleted_user_id.form_id.name if i.deleted_user_id.form_id else "",
                                    i.login_date if i.login_date else "",
                                    login_time_val if login_time_val else "",
                                ])
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": student_id_list,
                        "count": len(student_id_list),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found"},
                                    status=status.HTTP_404_NOT_FOUND)
            elif filter_method == "week":
                login_frequency = models.login_frequency.objects.all().order_by('created_date')
                d = datetime.datetime.now()
                dt = d.strftime('%Y-%m-%d')
                datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
                start = datetime_str - datetime.timedelta(days=datetime_str.weekday())
                end = start + datetime.timedelta(days=6)
                week_min = datetime.datetime.combine(start, datetime.time.min)
                week_max = datetime.datetime.combine(end, datetime.time.max)
                final_start = week_min
                final_end = week_max
                final_end = final_end + datetime.timedelta(hours=24)
                if final_start and final_end:
                    login_frequency = models.login_frequency.objects.filter(Q(created_date__range=[final_start, final_end]) & Q(user_id__is_student=True)).order_by('created_date')
                student_id_list = [["Student ID (#)", "Student Name", "Email", "Phone",
                                    "District", "School", "Form", "Login Date", "Login Time"]]
                if login_frequency:
                    for i in login_frequency:
                        if i.user_id.is_student:
                            login_time = i.login_time
                            login_time_val = login_time.strftime("%H:%M")
                            if i.user_id:
                                student_id_list.append([
                                    i.user_id.id if i.user_id else "",
                                    i.user_id.firstname if i.user_id else "",
                                    i.user_id.email if i.user_id else "",
                                    i.user_id.phone if i.user_id else "",
                                    i.user_id.district_id.english_name if i.user_id.district_id else "",
                                    i.user_id.school_id.school_name if i.user_id.school_id else "",
                                    i.user_id.form_id.name if i.user_id.form_id else "",
                                    i.login_date if i.login_date else "",
                                    login_time_val if login_time_val else "",
                                ])
                            elif i.deleted_user_id:
                                student_id_list.append([
                                    i.deleted_user_id.user_id if i.deleted_user_id else "",
                                    i.deleted_user_id.firstname if i.deleted_user_id else "",
                                    i.deleted_user_id.email if i.deleted_user_id else "",
                                    i.deleted_user_id.phone if i.deleted_user_id else "",
                                    i.deleted_user_id.district_id.english_name if i.deleted_user_id.district_id else "",
                                    i.deleted_user_id.school_id.school_name if i.deleted_user_id.school_id else "",
                                    i.deleted_user_id.form_id.name if i.deleted_user_id.form_id else "",
                                    i.login_date if i.login_date else "",
                                    login_time_val if login_time_val else "",
                                ])
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": student_id_list,
                        "count": len(student_id_list),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found"},
                                    status=status.HTTP_404_NOT_FOUND)
            elif filter_method == "month":
                login_frequency = models.login_frequency.objects.all().order_by('created_date')
                d = datetime.datetime.now()
                dt = d.strftime('%Y-%m-%d')
                datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
                end_date = d
                start_date = datetime_str - datetime.timedelta(days=30)
                if start_date and end_date:
                    login_frequency = models.login_frequency.objects.filter(Q(created_date__range=[start_date,
                                                                            end_date]) & Q(user_id__is_student=True))\
                                                                            .order_by('created_date')
                student_id_list = [["Student ID (#)", "Student Name", "Email", "Phone",
                                    "District", "School", "Form", "Login Date", "Login Time"]]
                if login_frequency:
                    for i in login_frequency:
                        if i.user_id.is_student:
                            login_time = i.login_time
                            login_time_val = login_time.strftime("%H:%M")
                            if i.user_id:
                                student_id_list.append([
                                    i.user_id.id if i.user_id else "",
                                    i.user_id.firstname if i.user_id else "",
                                    i.user_id.email if i.user_id else "",
                                    i.user_id.phone if i.user_id else "",
                                    i.user_id.district_id.english_name if i.user_id.district_id else "",
                                    i.user_id.school_id.school_name if i.user_id.school_id else "",
                                    i.user_id.form_id.name if i.user_id.form_id else "",
                                    i.login_date if i.login_date else "",
                                    login_time_val if login_time_val else "",
                                ])
                            if i.deleted_user_id:
                                student_id_list.append([
                                    i.deleted_user_id.user_id if i.deleted_user_id else "",
                                    i.deleted_user_id.firstname if i.deleted_user_id else "",
                                    i.deleted_user_id.email if i.deleted_user_id else "",
                                    i.deleted_user_id.phone if i.deleted_user_id else "",
                                    i.deleted_user_id.district_id.english_name if i.deleted_user_id.district_id else "",
                                    i.deleted_user_id.school_id.school_name if i.deleted_user_id.school_id else "",
                                    i.deleted_user_id.form_id.name if i.deleted_user_id.form_id else "",
                                    i.login_date if i.login_date else "",
                                    login_time_val if login_time_val else "",
                                ])
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": student_id_list,
                        "count": len(student_id_list),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found"},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                login_frequency = models.login_frequency.objects.filter(user_id__is_student=True).order_by('created_date')
                student_id_list = [["Student ID (#)", "Student Name", "Email", "Phone",
                                    "District", "School", "Form", "Login Date", "Login Time"]]
                if login_frequency:
                    for i in login_frequency:
                        if i.user_id.is_student:
                            login_time = i.login_time
                            login_time_val = login_time.strftime("%H:%M")
                            if i.user_id:
                                student_id_list.append([
                                    i.user_id.id if i.user_id else "",
                                    i.user_id.firstname if i.user_id else "",
                                    i.user_id.email if i.user_id else "",
                                    i.user_id.phone if i.user_id else "",
                                    i.user_id.district_id.english_name if i.user_id.district_id else "",
                                    i.user_id.school_id.school_name if i.user_id.school_id else "",
                                    i.user_id.form_id.name if i.user_id.form_id else "",
                                    i.login_date if i.login_date else "",
                                    login_time_val if login_time_val else "",
                                ])

                            if i.deleted_user_id:
                                student_id_list.append([
                                    i.deleted_user_id.user_id if i.deleted_user_id else "",
                                    i.deleted_user_id.firstname if i.deleted_user_id else "",
                                    i.deleted_user_id.email if i.deleted_user_id else "",
                                    i.deleted_user_id.phone if i.deleted_user_id else "",
                                    i.deleted_user_id.district_id.english_name if i.deleted_user_id.district_id else "",
                                    i.deleted_user_id.school_id.school_name if i.deleted_user_id.school_id else "",
                                    i.deleted_user_id.form_id.name if i.deleted_user_id.form_id else "",
                                    i.login_date if i.login_date else "",
                                    login_time_val if login_time_val else "",
                                ])

                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": student_id_list,
                        "count": len(student_id_list),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found"},
                                    status=status.HTTP_404_NOT_FOUND)

        except models.login_frequency.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class RegistrationUnit(generics.ListCreateAPIView):
    """
        Registration Unit
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    queryset = models.user.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Export to Excel
        """
        try:
            filter_method = request.data.get('filter')
            if filter_method == "day":
                users = models.user.objects.all().order_by('registration_date')
                deleted_users = DeletedUsers.objects.all().order_by('registration_date')
                today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
                today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
                if today_min and today_max:
                    users = models.user.objects.filter(registration_date__range=[today_min, today_max]).order_by('registration_date')
                    deleted_users = DeletedUsers.objects.filter(registration_date__range=[today_min, today_max]).order_by('registration_date')
                student_id_list = [["Student ID (#)", "Student Name", "Email", "Phone",
                                    "District", "School", "Form", "Registration Date",
                                    "Registration Time"]]
                if users:
                    for i in users:
                        if i.is_student:
                            registration_time = i.registration_time
                            registration_time_val = registration_time.strftime("%H:%M")
                            student_id_list.append([
                                i.id if i.id else "",
                                i.firstname if i.firstname else "",
                                i.email if i.email else "",
                                i.phone if i.phone else "",
                                i.district_id.english_name if i.district_id else "",
                                i.school_id.school_name if i.school_id else "",
                                i.form_id.name if i.form_id else "",
                                i.registration_date if i.registration_date else "",
                                registration_time_val if registration_time_val else "",
                            ])
                if deleted_users:
                    for i in deleted_users:
                        if i.is_student:
                            registration_time = i.registration_time
                            registration_time_val = registration_time.strftime("%H:%M")
                            student_id_list.append([
                                i.id if i.id else "",
                                i.firstname if i.firstname else "",
                                i.email if i.email else "",
                                i.phone if i.phone else "",
                                i.district_id.english_name if i.district_id else "",
                                i.school_id.school_name if i.school_id else "",
                                i.form_id.name if i.form_id else "",
                                i.registration_date if i.registration_date else "",
                                registration_time_val if registration_time_val else "",
                            ])
                if student_id_list:
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": student_id_list,
                        "count": len(student_id_list),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found"},
                                    status=status.HTTP_404_NOT_FOUND)
            elif filter_method == "week":
                users = models.user.objects.all().order_by('registration_date')
                deleted_users = DeletedUsers.objects.all().order_by('registration_date')
                d = datetime.datetime.now()
                dt = d.strftime('%Y-%m-%d')
                datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
                start = datetime_str - datetime.timedelta(days=datetime_str.weekday())
                end = start + datetime.timedelta(days=6)
                week_min = datetime.datetime.combine(start, datetime.time.min)
                week_max = datetime.datetime.combine(end, datetime.time.max)
                final_start = week_min
                final_end = week_max
                final_end = final_end + datetime.timedelta(hours=24)
                if final_start and final_end:
                    users = models.user.objects.filter(registration_date__range=[final_start, final_end]).order_by('registration_date')
                    deleted_users = DeletedUsers.objects.filter(registration_date__range=[final_start, final_end]).order_by('registration_date')
                student_id_list = [["Student ID (#)", "Student Name", "Email", "Phone",
                                    "District", "School", "Form", "Registration Date",
                                    "Registration Time"]]
                if users:
                    for i in users:
                        if i.is_student:
                            registration_time = i.registration_time
                            registration_time_val = registration_time.strftime("%H:%M")
                            student_id_list.append([
                                i.id if i.id else "",
                                i.firstname if i.firstname else "",
                                i.email if i.email else "",
                                i.phone if i.phone else "",
                                i.district_id.english_name if i.district_id else "",
                                i.school_id.school_name if i.school_id else "",
                                i.form_id.name if i.form_id else "",
                                i.registration_date if i.registration_date else "",
                                registration_time_val if registration_time_val else "",
                            ])
                if deleted_users:
                    for i in deleted_users:
                        if i.is_student:
                            registration_time = i.registration_time
                            registration_time_val = registration_time.strftime("%H:%M")
                            student_id_list.append([
                                i.id if i.id else "",
                                i.firstname if i.firstname else "",
                                i.email if i.email else "",
                                i.phone if i.phone else "",
                                i.district_id.english_name if i.district_id else "",
                                i.school_id.school_name if i.school_id else "",
                                i.form_id.name if i.form_id else "",
                                i.registration_date if i.registration_date else "",
                                registration_time_val if registration_time_val else "",
                            ])
                if student_id_list:
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": student_id_list,
                        "count": len(student_id_list),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found"},
                                    status=status.HTTP_404_NOT_FOUND)
            elif filter_method == "month":
                users = models.user.objects.all().order_by('registration_date')
                deleted_users = DeletedUsers.objects.all().order_by('registration_date')
                d = datetime.datetime.now()
                dt = d.strftime('%Y-%m-%d')
                datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
                end_date = d
                start_date = datetime_str - datetime.timedelta(days=30)
                if start_date and end_date:
                    users = models.user.objects.filter(registration_date__range=[start_date, end_date]).order_by('registration_date')
                    deleted_users = DeletedUsers.objects.filter(registration_date__range=[start_date, end_date]).order_by('registration_date')
                student_id_list = [["Student ID (#)", "Student Name", "Email", "Phone",
                                    "District", "School", "Form", "Registration Date",
                                    "Registration Time"]]
                if users:
                    for i in users:
                        if i.is_student:
                            registration_time = i.registration_time
                            registration_time_val = registration_time.strftime("%H:%M")
                            student_id_list.append([
                                i.id if i.id else "",
                                i.firstname if i.firstname else "",
                                i.email if i.email else "",
                                i.phone if i.phone else "",
                                i.district_id.english_name if i.district_id else "",
                                i.school_id.school_name if i.school_id else "",
                                i.form_id.name if i.form_id else "",
                                i.registration_date if i.registration_date else "",
                                registration_time_val if registration_time_val else "",
                            ])
                if deleted_users:
                    for i in deleted_users:
                        if i.is_student:
                            registration_time = i.registration_time
                            registration_time_val = registration_time.strftime("%H:%M")
                            student_id_list.append([
                                i.id if i.id else "",
                                i.firstname if i.firstname else "",
                                i.email if i.email else "",
                                i.phone if i.phone else "",
                                i.district_id.english_name if i.district_id else "",
                                i.school_id.school_name if i.school_id else "",
                                i.form_id.name if i.form_id else "",
                                i.registration_date if i.registration_date else "",
                                registration_time_val if registration_time_val else "",
                            ])
                if student_id_list:
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": student_id_list,
                        "count": len(student_id_list),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found"},
                                    status=status.HTTP_404_NOT_FOUND)
            elif filter_method == "year":
                users = models.user.objects.all().order_by('registration_date')
                deleted_users = DeletedUsers.objects.all().order_by('registration_date')
                d = datetime.datetime.now()
                dt = d.strftime('%Y-%m-%d')
                datetime_str = datetime.datetime.strptime(str(dt), '%Y-%m-%d')
                end_date = d
                start_date = datetime_str - datetime.timedelta(days=365)
                if start_date and end_date:
                    users = models.user.objects.filter(registration_date__range=[start_date, end_date]).order_by('registration_date')
                    deleted_users = DeletedUsers.objects.filter(registration_date__range=[start_date, end_date]).order_by('registration_date')
                student_id_list = [["Student ID (#)", "Student Name", "Email", "Phone",
                                    "District", "School", "Form", "Registration Date",
                                    "Registration Time"]]
                if users:
                    for i in users:
                        if i.is_student:
                            registration_time = i.registration_time
                            registration_time_val = registration_time.strftime("%H:%M")
                            student_id_list.append([
                                i.id if i.id else "",
                                i.firstname if i.firstname else "",
                                i.email if i.email else "",
                                i.phone if i.phone else "",
                                i.district_id.english_name if i.district_id else "",
                                i.school_id.school_name if i.school_id else "",
                                i.form_id.name if i.form_id else "",
                                i.registration_date if i.registration_date else "",
                                registration_time_val if registration_time_val else "",
                            ])
                if deleted_users:
                    for i in deleted_users:
                        if i.is_student:
                            registration_time = i.registration_time
                            registration_time_val = registration_time.strftime("%H:%M")
                            student_id_list.append([
                                i.id if i.id else "",
                                i.firstname if i.firstname else "",
                                i.email if i.email else "",
                                i.phone if i.phone else "",
                                i.district_id.english_name if i.district_id else "",
                                i.school_id.school_name if i.school_id else "",
                                i.form_id.name if i.form_id else "",
                                i.registration_date if i.registration_date else "",
                                registration_time_val if registration_time_val else "",
                            ])
                if student_id_list:
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": student_id_list,
                        "count": len(student_id_list),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found"},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                users = models.user.objects.all().order_by('registration_date')
                deleted_users = DeletedUsers.objects.all().order_by('registration_date')

                student_id_list = [["Student ID (#)", "Student Name", "Email", "Phone",
                                    "District", "School", "Form", "Registration Date",
                                    "Registration Time"]]
                if users:
                    for i in users:
                        if i.is_student:
                            registration_time = i.registration_time
                            registration_time_val = registration_time.strftime("%H:%M")
                            student_id_list.append([
                                i.id if i.id else "",
                                i.firstname if i.firstname else "",
                                i.email if i.email else "",
                                i.phone if i.phone else "",
                                i.district_id.english_name if i.district_id else "",
                                i.school_id.school_name if i.school_id else "",
                                i.form_id.name if i.form_id else "",
                                i.registration_date if i.registration_date else "",
                                registration_time_val if registration_time_val else "",
                            ])
                if deleted_users:
                    for i in deleted_users:
                        if i.is_student:
                            registration_time = i.registration_time
                            registration_time_val = registration_time.strftime("%H:%M")
                            student_id_list.append([
                                i.id if i.id else "",
                                i.firstname if i.firstname else "",
                                i.email if i.email else "",
                                i.phone if i.phone else "",
                                i.district_id.english_name if i.district_id else "",
                                i.school_id.school_name if i.school_id else "",
                                i.form_id.name if i.form_id else "",
                                i.registration_date if i.registration_date else "",
                                registration_time_val if registration_time_val else "",
                            ])
                if student_id_list:
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": student_id_list,
                        "count": len(student_id_list),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found"},
                                    status=status.HTTP_404_NOT_FOUND)
        except models.user.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class TestStatistics(generics.ListCreateAPIView):
    """
        Test Statistics
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    queryset = models.user.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Export to Excel
        """
        try:
            test_data = TestDetails.objects.all().order_by('created_date')
            student_id_list = [["Student ID (#)", "Student Name", "Theme (Chinese)", "Theme (English)",
                                "Topic (Chinese)", "Topic (English)", "Type of Question (MC/SQ)",
                                "Duration of the test (Minutes)", "Test Date"]]
            if test_data:
                for i in test_data:
                    if i.partner_id and i.partner_id.is_student:
                        create_date = i.created_date.date()
                        question_data = ""
                        theme_chinese_name = ""
                        theme_english_name = ""
                        topic_chinese_name = ""
                        topic_english_name = ""
                        question_data_1 = TestAttendedQuestions.objects.filter(unique_string=i.unique_string).order_by('created_date').first()

                        if i.is_mc:
                            if question_data_1:
                                question_data = question_data_1
                                theme_chinese_name = question_data.mc_id.theme_id.theme_chinese_name
                                theme_english_name = question_data.mc_id.theme_id.theme_english_name
                                topic_chinese_name = question_data.mc_id.topic_id.topic_chinese_name
                                topic_english_name = question_data.mc_id.topic_id.topic_english_name
                            if i.partner_id:
                                student_id_list.append([
                                    i.partner_id.id if i.partner_id else "",
                                    i.partner_id.firstname if i.partner_id else "",
                                    theme_chinese_name if theme_chinese_name else "",
                                    theme_english_name if theme_english_name else "",
                                    topic_chinese_name if topic_chinese_name else "",
                                    topic_english_name if topic_english_name else "",
                                    "MC",
                                    i.duration if i.duration else "0",
                                    create_date if create_date else "",
                                ])
                            elif i.deleted_user_id:
                                student_id_list.append([
                                    i.deleted_user_id.user_id if i.deleted_user_id else "",
                                    i.deleted_user_id.firstname if i.deleted_user_id else "",
                                    theme_chinese_name if theme_chinese_name else "",
                                    theme_english_name if theme_english_name else "",
                                    topic_chinese_name if topic_chinese_name else "",
                                    topic_english_name if topic_english_name else "",
                                    "MC",
                                    i.duration if i.duration else "0",
                                    create_date if create_date else "",
                                ])
                        if i.is_sq:
                            if question_data_1:
                                question_data = question_data_1
                                theme_chinese_name = question_data.sq_id.theme_id.theme_chinese_name
                                theme_english_name = question_data.sq_id.theme_id.theme_english_name
                                topic_chinese_name = question_data.sq_id.topic_id.topic_chinese_name
                                topic_english_name = question_data.sq_id.topic_id.topic_english_name
                            if i.partner_id:
                                student_id_list.append([
                                    i.partner_id.id if i.partner_id else "",
                                    i.partner_id.firstname if i.partner_id else "",
                                    theme_chinese_name if theme_chinese_name else "",
                                    theme_english_name if theme_english_name else "",
                                    topic_chinese_name if topic_chinese_name else "",
                                    topic_english_name if topic_english_name else "",
                                    "SQ",
                                    i.duration if i.duration else "0",
                                    create_date if create_date else "",
                                ])
                            elif i.deleted_user_id:
                                student_id_list.append([
                                    i.deleted_user_id.user_id if i.deleted_user_id else "",
                                    i.deleted_user_id.firstname if i.deleted_user_id else "",
                                    theme_chinese_name if theme_chinese_name else "",
                                    theme_english_name if theme_english_name else "",
                                    topic_chinese_name if topic_chinese_name else "",
                                    topic_english_name if topic_english_name else "",
                                    "SQ",
                                    i.duration if i.duration else "0",
                                    create_date if create_date else "",
                                ])
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": student_id_list,
                    "count": len(student_id_list),
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found"},
                                status=status.HTTP_404_NOT_FOUND)
        except TestDetails.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class PopularStatistics(generics.ListCreateAPIView):
    """
        Popular Statistics
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    queryset = models.user.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Export to Excel
        """
        try:
            theme_usage_data = ThemeUsage.objects.all().order_by('created_date')
            student_id_list = [[
                "Student ID (#)", "Student Name", "Email",
                "Phone", "District", "School", "Form",
                "View Date", "View Time",
                "Theme (Chinese)", "Theme (English)",
                "Topic (Chinese)", "Topic (English)",
            ]]
            if theme_usage_data:
                for i in theme_usage_data:
                    view_date = i.created_date.date()
                    view_time_sec = i.created_date.time()
                    view_time = view_time_sec.strftime("%H:%M")
                    if i.user_id:
                        student_id_list.append([
                            i.id if i.id else "",
                            i.user_id.firstname if i.user_id else "",
                            i.user_id.email if i.user_id else "",
                            i.user_id.phone if i.user_id else "",
                            i.user_id.district_id.english_name if i.user_id.district_id else "",
                            i.user_id.school_id.school_name if i.user_id.school_id else "",
                            i.user_id.form_id.name if i.user_id.form_id else "",
                            view_date if view_date else "",
                            view_time if view_time else "",
                            i.theme_id.theme_chinese_name if i.theme_id else "",
                            i.theme_id.theme_english_name if i.theme_id else "",
                            i.topic_id.topic_chinese_name if i.topic_id else "",
                            i.topic_id.topic_english_name if i.topic_id else "",
                        ])
                    elif i.deleted_user_id:
                        student_id_list.append([
                            i.id if i.id else "",
                            i.deleted_user_id.firstname if i.deleted_user_id else "",
                            i.deleted_user_id.email if i.deleted_user_id else "",
                            i.deleted_user_id.phone if i.deleted_user_id else "",
                            i.deleted_user_id.district_id.english_name if i.deleted_user_id.district_id else "",
                            i.deleted_user_id.school_id.school_name if i.deleted_user_id.school_id else "",
                            i.deleted_user_id.form_id.name if i.deleted_user_id.form_id else "",
                            view_date if view_date else "",
                            view_time if view_time else "",
                            i.theme_id.theme_chinese_name if i.theme_id else "",
                            i.theme_id.theme_english_name if i.theme_id else "",
                            i.topic_id.topic_chinese_name if i.topic_id else "",
                            i.topic_id.topic_english_name if i.topic_id else "",
                        ])
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": student_id_list,
                    "count": len(student_id_list),
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found"},
                                status=status.HTTP_404_NOT_FOUND)
        except ThemeUsage.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class SpecificDiscount(generics.ListCreateAPIView):
    """
        Specific Discount
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    queryset = models.user.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Export to Excel
        """
        try:
            discount_usage_data = DiscountUsage.objects.all().order_by('created_date')
            student_id_list = [[
                "Discount Code", "Promotion Name", "Discount (Percent / Reduce)",
                "Discount Percent", "Reduce amount", "Start Date",
                "Expiring Date", "Student ID (#)", "Student Name",
                "Email", "Phone", "District", "School", "Form",
            ]]
            if discount_usage_data:
                for i in discount_usage_data:
                    if i.discount_code.discount_percentage:
                        if i.user:
                            student_id_list.append([
                                i.discount_code.discount_code if i.discount_code else "",
                                i.discount_code.promotion_name if i.discount_code else "",
                                "Percent",
                                i.discount_code.discount_percentage_value if i.discount_code else "",
                                "",
                                i.discount_code.discount_start_date if i.discount_code else "",
                                i.discount_code.discount_end_date if i.discount_code else "",
                                i.user.id if i.user else "",
                                i.user.firstname if i.user else "",
                                i.user.email if i.user else "",
                                i.user.phone if i.user else "",
                                i.user.district_id.english_name if i.user.district_id else "",
                                i.user.school_id.school_name if i.user.school_id else "",
                                i.user.form_id.name if i.user.form_id else "",
                            ])
                        elif i.deleted_user_id:
                            student_id_list.append([
                                i.discount_code.discount_code if i.discount_code else "",
                                i.discount_code.promotion_name if i.discount_code else "",
                                "Percent",
                                i.discount_code.discount_percentage_value if i.discount_code else "",
                                "",
                                i.discount_code.discount_start_date if i.discount_code else "",
                                i.discount_code.discount_end_date if i.discount_code else "",
                                i.deleted_user_id.user_id if i.deleted_user_id else "",
                                i.deleted_user_id.firstname if i.deleted_user_id else "",
                                i.deleted_user_id.email if i.deleted_user_id else "",
                                i.deleted_user_id.phone if i.deleted_user_id else "",
                                i.deleted_user_id.district_id.english_name if i.deleted_user_id.district_id else "",
                                i.deleted_user_id.school_id.school_name if i.deleted_user_id.school_id else "",
                                i.deleted_user_id.form_id.name if i.deleted_user_id.form_id else "",
                            ])
                    if i.discount_code.discount_reduce_amount:
                        if i.user:
                            student_id_list.append([
                                i.discount_code.discount_code if i.discount_code else "",
                                i.discount_code.promotion_name if i.discount_code else "",
                                "Reduce",
                                "",
                                i.discount_code.discount_reduce_amount_value if i.discount_code else "",
                                i.discount_code.discount_start_date if i.discount_code else "",
                                i.discount_code.discount_end_date if i.discount_code else "",
                                i.user.id if i.user else "",
                                i.user.firstname if i.user else "",
                                i.user.email if i.user else "",
                                i.user.phone if i.user else "",
                                i.user.district_id.english_name if i.user.district_id else "",
                                i.user.school_id.school_name if i.user.school_id else "",
                                i.user.form_id.name if i.user.form_id else "",
                            ])
                        if i.deleted_user_id:
                            student_id_list.append([
                                i.discount_code.discount_code if i.discount_code else "",
                                i.discount_code.promotion_name if i.discount_code else "",
                                "Reduce",
                                "",
                                i.discount_code.discount_reduce_amount_value if i.discount_code else "",
                                i.discount_code.discount_start_date if i.discount_code else "",
                                i.discount_code.discount_end_date if i.discount_code else "",
                                i.deleted_user_id.user_id if i.deleted_user_id else "",
                                i.deleted_user_id.firstname if i.deleted_user_id else "",
                                i.deleted_user_id.email if i.deleted_user_id else "",
                                i.deleted_user_id.phone if i.deleted_user_id else "",
                                i.deleted_user_id.district_id.english_name if i.deleted_user_id.district_id else "",
                                i.deleted_user_id.school_id.school_name if i.deleted_user_id.school_id else "",
                                i.deleted_user_id.form_id.name if i.deleted_user_id.form_id else "",
                            ])
                for i in student_id_list:
                    print(i)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": student_id_list,
                    "count": len(student_id_list),
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found, No discount is applied"},
                                status=status.HTTP_404_NOT_FOUND)
        except DiscountUsage.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)