import math

from django.db.models import Q
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Test import serializers, models
from Test.models import TestDetails, TestAttendedQuestions
from theme.models import Theme, Topic
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from datetime import timedelta
from dateutil import relativedelta

class TestDetailsAPI(generics.ListCreateAPIView):
    """
        Test Details API
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.TestDetailsSerializers
    queryset = models.TestDetails.objects.all().order_by('-id')

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
            create Test details
            :param request: Test details
            :param kwargs: NA
            :return: Test details
        """
        is_mc = request.data.get('is_mc')
        is_sq = request.data.get('is_sq')
        if is_mc:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": serializer.data,
                }, status=status.HTTP_201_CREATED)

        elif is_sq:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": serializer.data,
                }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Failed", "data": {}},
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


class TestAnsweredQuestionAPI(generics.ListCreateAPIView):
    """
        Test Answered Question API
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.TestAttendedSerializers
    queryset = models.TestAttendedQuestions.objects.all().order_by('-id')

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
        serializer = self.serializer_class(instance=snippets, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class TestDetailsGetItem(generics.ListCreateAPIView):
    """
        Test Details Get Item
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.TestDetailsSerializers
    queryset = models.TestDetails.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            pk = request.data.get('id')
            snippet = models.TestDetails.objects.get(id=pk)
        except TestDetails.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            serializer = serializers.TestDetailsSerializers(snippet, context={"request": request})
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)


class IntegratedTest(generics.ListCreateAPIView):
    """
        Integrated Test
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.TestDetailsSerializers
    queryset = models.TestDetails.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
        Retrieve, update or delete a code snippet.
        """
        themes_dict = []
        try:
            import socket
            import re
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            url = request.build_absolute_uri()

            http_layer = request.is_secure() and "https" or "http"
            http_address = request.get_host()
            http_port = request.META['SERVER_PORT']
            urls = str(http_layer+"://"+http_address)

            mcq = models.MC.objects.all().order_by('?')[:10]
            short_questions = models.ShortQuestion.objects.all().order_by('?')[:6]
            mc_list = []
            sq_list = []
            for mc in mcq:
                mc_options_list = []
                mc_options = models.McOptions.objects.filter(mc_id=mc.id)
                for option in mc_options:
                    mc_option_dict = {
                        "id": option.id,
                        "mc_id": option.mc_id.id if option.mc_id else False,
                        "mc_english_options": option.mc_english_options,
                        "mc_chinese_options": option.mc_chinese_options,
                        "mc_answer_index": option.mc_answer_index,
                        "created_date": mc.created_date,
                        "updated_date": mc.updated_date
                    }
                    mc_options_list.append(mc_option_dict)
                mc_dict = {
                    "id": mc.id,
                    "theme_id": mc.theme_id.id if mc.theme_id else False,
                    "theme_name": mc.theme_id.theme_english_name if mc.theme_id else False,
                    "theme_chinese_name": mc.theme_id.theme_chinese_name if mc.theme_id else False,
                    "topic_id": mc.topic_id.id if mc.topic_id else False,
                    "topic_name": mc.topic_id.topic_english_name if mc.topic_id else False,
                    "topic_chinese_name": mc.topic_id.topic_chinese_name if mc.topic_id else False,
                    "learning_focus_id": mc.learning_focus_id.id if mc.learning_focus_id else False,
                    "learning_focus_english_name": mc.learning_focus_id.english if mc.learning_focus_id else False,
                    "learning_focus_chinese_name": mc.learning_focus_id.chinese if mc.learning_focus_id else False,
                    "mc_english_source_ref": mc.mc_english_source_ref,
                    "mc_chinese_source_ref": mc.mc_chinese_source_ref,
                    "mc_english_source_details": mc.mc_english_source_details,
                    "mc_chinese_source_details": mc.mc_chinese_source_details,
                    "mc_english_question": mc.mc_english_question,
                    "mc_chinese_question": mc.mc_chinese_question,
                    "mc_english_question_bookmark": mc.mc_english_question_bookmark,
                    "mc_chinese_question_bookmark": mc.mc_chinese_question_bookmark,
                    "answer": mc.answer,
                    "mark": mc.mark,
                    "total_mark": mc.total_mark,
                    "no_of_respondents": mc.no_of_respondents,
                    "created_date": mc.created_date,
                    "updated_date": mc.updated_date,
                    "mc_options": mc_options_list
                }
                mc_list.append(mc_dict)
            for sq in short_questions:
                sq_points_list = []
                sq_mark_points = models.ShortQuestionMarkPoints.objects.filter(sq_id=sq.id)
                for points in sq_mark_points:
                    sq_option_dict = {
                        "id": points.id,
                        "sq_id": points.sq_id.id if points.sq_id else False,
                        "sq_english_mark_points": points.sq_english_mark_points,
                        "sq_chinese_mark_points": points.sq_chinese_mark_points,
                        "sq_english_mark": points.sq_english_mark,
                        "sq_chinese_mark": points.sq_chinese_mark,
                        "created_date": points.created_date,
                        "updated_date": points.updated_date
                    }
                    sq_points_list.append(sq_option_dict)
                sq_dict = {
                    "id": sq.id,
                    "theme_id": sq.theme_id.id if sq.theme_id else False,
                    "theme_name": sq.theme_id.theme_english_name if sq.theme_id else False,
                    "topic_id": sq.topic_id.id if sq.topic_id else False,
                    "topic_name": sq.topic_id.topic_english_name if sq.topic_id else False,
                    "learning_focus_id": sq.learning_focus_id.id if sq.learning_focus_id else False,
                    "learning_focus_english_name": sq.learning_focus_id.english if sq.learning_focus_id else False,
                    "learning_focus_chinese_name": sq.learning_focus_id.chinese if sq.learning_focus_id else False,
                    "sq_english_source_ref": sq.sq_english_source_ref,
                    "sq_chinese_source_ref": sq.sq_chinese_source_ref,
                    "sq_english_source_details": sq.sq_english_source_details,
                    "sq_chinese_source_details": sq.sq_chinese_source_details,
                    "sq_english_question": sq.sq_english_question,
                    "sq_chinese_question": sq.sq_chinese_question,
                    "sq_english_question_bookmark": sq.sq_english_question_bookmark,
                    "sq_chinese_question_bookmark": sq.sq_chinese_question_bookmark,
                    "sq_english_suggested_answer": sq.sq_english_suggested_answer,
                    "sq_chinese_suggested_answer": sq.sq_chinese_suggested_answer,
                    "sq_total_mark": sq.sq_total_mark,
                    "created_date": sq.created_date,
                    "updated_date": sq.updated_date,
                    "sq_points": sq_points_list
                }
                sq_list.append(sq_dict)
            test_list = {
                "mc":  mc_list,
                "sq":  sq_list
            }

            return Response({
                "success": True,
                "message": "Success",
                "data": test_list,
            }, status=status.HTTP_200_OK)
        except models.MC.DoesNotExist or models.ShortQuestion.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class TestDurationFrequency(generics.ListCreateAPIView):
    """
        Test Duration and Frequency
    """
    serializer_class = serializers.TestDetailsSerializers
    queryset = models.TestDetails.objects.all().order_by('theme_id')

    def get_frequency_per_day(self, date_list):
        """
        Find test frequency per day
        :return:
        """
        total_days = (max(date_list) - min(date_list)).days
        if total_days:
            frequency_per_day = math.trunc((len(date_list) / total_days)*10)/10
        else:
            return len(date_list)
        return frequency_per_day

    def get_frequency_per_week(self, date_list, count):
        num_weeks = abs((max(date_list) - min(date_list)).days) // 7
        if num_weeks:
            num_week = math.trunc((count/num_weeks)*10)/10
        else:
            return len(date_list)
        return num_week

    def get_frequency_per_month(self, date_list, count):
        start_date = min(date_list)
        end_date = max(date_list)
        # months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        delta = relativedelta.relativedelta(end_date, start_date)
        months = delta.months + (delta.years * 12)
        if months:
            return math.trunc((count/months)*10)/10
        else:
            return count

    def get_frequency_per_year(self, date_list, count):
        start_date = min(date_list)
        end_date = max(date_list)
        delta = relativedelta.relativedelta(end_date, start_date)
        years = delta.years
        if years:
            return math.trunc((count / years) * 10) / 10
        else:
            return count


    def post(self, request, *args, **kwargs):
        """
            create Test details
            :param request: Test details
            :param kwargs: NA
            :return: Test details
        """
        try:

            filters = {
                'topic_id': 'topic_id',
                'theme_id': 'theme_id',
            }
            selected_filters = {k: v for k, v in request.data.items() if v}
            test_data = TestDetails.objects.all().order_by('topic_id')
            for key, value in selected_filters.items():
                test_data = test_data.filter(**{filters[key]: value})

            mc_list = []
            sq_list = []
            for test in test_data:
                mc_topics = []
                if test.is_mc and not test.is_sq:
                    question_data_mc = TestAttendedQuestions.objects.filter(is_mc=True, is_sq=False,unique_string=test.unique_string).order_by('created_date').first()
                    if question_data_mc:
                        topics = Topic.objects.order_by('sequence').filter(theme_id=question_data_mc.mc_id.theme_id.id)
                        for topic in topics:
                            if topic.id == test.topic_id.id:
                                topics_val_mc = {
                                    "topic_id": topic.id if topic else False,
                                    "topic_name": topic.topic_english_name if topic else False,
                                    "topic_sequence": topic.sequence if topic else False,
                                    "average_duration": test.duration if test else "00:00",
                                    "frequency_day": 1,
                                    "frequency_week": 1,
                                    "frequency_month": 1,
                                    "frequency_year": 1,
                                    "no_of_respondents": 1,
                                    "create_date": test.created_date.date(),
                                    "user": test.partner_id.id
                                }
                                mc_topics.append(topics_val_mc)
                        theme_val_mc = {
                            "theme_id": question_data_mc.mc_id.theme_id.id if question_data_mc.mc_id.theme_id else False,
                            "theme_name": question_data_mc.mc_id.theme_id.theme_english_name if question_data_mc.mc_id.theme_id else False,
                            "theme_sequence": question_data_mc.mc_id.theme_id.sequence if question_data_mc.mc_id.theme_id else False,
                            "topics": mc_topics
                        }
                        if mc_topics:
                            mc_list.append(theme_val_mc)
            theme_ids_list = []
            for mc_list_item in mc_list:
                theme_ids_list.append(mc_list_item.get("theme_id"))
            theme_ids_list = list(set(theme_ids_list))
            final_theme_topic_ids = []
            for theme_id in theme_ids_list:
                topic_ids_list = []
                for mc_list_item in mc_list:
                    if theme_id == mc_list_item.get("theme_id"):
                        topic_ids_list.append(mc_list_item.get("topics")[0].get("topic_id"))
                topic_ids_list = list(set(topic_ids_list))
                final_theme_topic_ids.append([theme_id, topic_ids_list])
            # [[40, [56, 58, 59]], [41, [80, 57]]]
            mc_status_list = []
            total_avg_time = 0
            for final_theme_topic_id in final_theme_topic_ids:
                for mc_list_item in mc_list:
                    if mc_list_item.get("theme_id") == final_theme_topic_id[0]:
                        for topic_ids in final_theme_topic_id[1]:
                            if mc_list_item.get("topics")[0].get("topic_id") == topic_ids:
                                timeParts = [int(s) for s in mc_list_item.get("topics")[0].get("average_duration").split(':')]
                                total_avg_time += ((timeParts[0]) * 60 + timeParts[1])/3600
                                # print(mc_list_item.get("theme_id"), topic_ids, mc_list_item.get("topics")[0].get("average_duration"), total_avg_time)
                                if len(mc_status_list) != 0:
                                    if mc_status_list[-1].get("theme_id") == mc_list_item.get("theme_id") and mc_status_list[-1].get("topic_id") == topic_ids:
                                        mc_status_list[-1]["total_avg_duration"] = mc_status_list[-1]["total_avg_duration"] + (([int(s) for s in mc_list_item.get("topics")[0].get("average_duration").split(':')][0]) * 60 + [int(s) for s in mc_list_item.get("topics")[0].get("average_duration").split(':')][1])/3600
                                        mc_status_list[-1]["count"] += 1
                                        mc_status_list[-1]["test_created_date"].append(mc_list_item.get("topics")[0].get("create_date"))
                                        if mc_list_item.get("topics")[0].get("user") not in mc_status_list[-1]["users_attended"]:
                                            mc_status_list[-1]["users_attended"].append(mc_list_item.get("topics")[0].get("user"))
                                    else:
                                        mc_status_list.append(
                                            {"qn_type": "mc",
                                             "theme_id": mc_list_item.get("theme_id"),
                                             "theme_name": mc_list_item.get("theme_name"),
                                             "topic_id": topic_ids,
                                             "topic_name": mc_list_item.get("topics")[0].get("topic_name"),
                                             "topic_sequence": mc_list_item.get("topics")[0].get("topic_sequence"),
                                             "total_avg_duration": (([int(s) for s in mc_list_item.get("topics")[0].get("average_duration").split(':')][0]) * 60 + [int(s) for s in mc_list_item.get("topics")[0].get("average_duration").split(':')][1])/3600,
                                             "count": 1,
                                             "test_created_date": [mc_list_item.get("topics")[0].get("create_date")],
                                             "users_attended": [mc_list_item.get("topics")[0].get("user")]
                                             })
                                        total_avg_time = 0
                                else:
                                    mc_status_list.append(
                                        {"qn_type": "mc",
                                         "theme_id": mc_list_item.get("theme_id"),
                                         "theme_name": mc_list_item.get("theme_name"),
                                         "topic_id": topic_ids,
                                         "topic_name": mc_list_item.get("topics")[0].get("topic_name"),
                                         "topic_sequence": mc_list_item.get("topics")[0].get("topic_sequence"),
                                         "total_avg_duration": total_avg_time,
                                         "count": 1,
                                         "test_created_date": [mc_list_item.get("topics")[0].get("create_date")],
                                         "users_attended": [mc_list_item.get("topics")[0].get("user")]
                                         })

            for mc_item in mc_status_list:
                mc_item["average_duration"] = round(mc_item["total_avg_duration"] / mc_item["count"], 2)
                del mc_item["total_avg_duration"]
                mc_item["frequency_day"] = self.get_frequency_per_day(mc_item["test_created_date"])
                mc_item["frequency_week"] = self.get_frequency_per_week(mc_item["test_created_date"], mc_item["count"])
                mc_item["frequency_month"] = self.get_frequency_per_month(mc_item["test_created_date"], mc_item["count"])
                mc_item["frequency_year"] = self.get_frequency_per_year(mc_item["test_created_date"], mc_item["count"])
                mc_item["no_of_respondents"] = len(mc_item["users_attended"])
                del mc_item["test_created_date"]
                del mc_item["users_attended"]
            # print(mc_status_list)

            for test in test_data:
                sq_topics = []
                if test.is_sq and not test.is_mc:
                    question_data_sq = TestAttendedQuestions.objects.filter(is_mc=False, is_sq=True,unique_string=test.unique_string).order_by('created_date').first()
                    if question_data_sq:
                        topics = Topic.objects.order_by('sequence').filter(theme_id=question_data_sq.sq_id.theme_id.id)
                        for topic in topics:
                            if topic.id == question_data_sq.sq_id.topic_id.id:
                                topics_val_sq = {
                                    "topic_id": topic.id if topic else False,
                                    "topic_name": topic.topic_english_name if topic else False,
                                    "topic_sequence": topic.sequence if topic else False,
                                    "average_duration": test.duration if test else "00:00",
                                    "frequency_day": 1,
                                    "frequency_week": 1,
                                    "frequency_month": 1,
                                    "frequency_year": 1,
                                    "no_of_respondents": 1,
                                    "create_date": test.created_date.date(),
                                    "user": test.partner_id.id
                                }
                                sq_topics.append(topics_val_sq)
                        theme_val_sq = {
                            "theme_id": question_data_sq.sq_id.theme_id.id if question_data_sq.sq_id.theme_id else False,
                            "theme_name": question_data_sq.sq_id.theme_id.theme_english_name if question_data_sq.sq_id.theme_id else False,
                            "theme_sequence": question_data_sq.sq_id.theme_id.sequence if question_data_sq.sq_id.theme_id else False,
                            "topics": sq_topics
                        }
                        if sq_topics:
                            sq_list.append(theme_val_sq)

            theme_ids_list = []
            for sq_list_item in sq_list:
                theme_ids_list.append(sq_list_item.get("theme_id"))
            theme_ids_list = list(set(theme_ids_list))
            final_theme_topic_ids = []
            for theme_id in theme_ids_list:
                topic_ids_list = []
                for sq_list_item in sq_list:
                    if theme_id == sq_list_item.get("theme_id"):
                        topic_ids_list.append(sq_list_item.get("topics")[0].get("topic_id"))
                topic_ids_list = list(set(topic_ids_list))
                final_theme_topic_ids.append([theme_id, topic_ids_list])
                # [[40, [56, 58, 59]], [41, [80, 57]]]
            # print(final_theme_topic_ids)
            sq_status_list = []
            total_avg_time = 0
            for final_theme_topic_id in final_theme_topic_ids:
                for sq_list_item in sq_list:
                    if sq_list_item.get("theme_id") == final_theme_topic_id[0]:
                        for topic_ids in final_theme_topic_id[1]:
                            if sq_list_item.get("topics")[0].get("topic_id") == topic_ids:
                                timeParts = [int(s) for s in sq_list_item.get("topics")[0].get("average_duration").split(':')]
                                total_avg_time += ((timeParts[0]) * 60 + timeParts[1]) / 3600
                                print(sq_list_item.get("theme_id"), topic_ids, sq_list_item.get("topics")[0].get("average_duration"), total_avg_time)
                                if len(sq_status_list) != 0:
                                    if sq_status_list[-1].get("theme_id") == sq_list_item.get("theme_id") and sq_status_list[-1].get("topic_id") == topic_ids:
                                        sq_status_list[-1]["total_avg_duration"] = sq_status_list[-1]["total_avg_duration"] + (([int(s) for s in sq_list_item.get("topics")[0].get("average_duration").split(':')][0]) * 60 + [int(s) for s in sq_list_item.get("topics")[0].get("average_duration").split(':')][1])/3600
                                        sq_status_list[-1]["count"] += 1
                                        sq_status_list[-1]["test_created_date"].append(sq_list_item.get("topics")[0].get("create_date"))
                                        if sq_list_item.get("topics")[0].get("user") not in sq_status_list[-1]["users_attended"]:
                                            sq_status_list[-1]["users_attended"].append(sq_list_item.get("topics")[0].get("user"))
                                    else:
                                        sq_status_list.append(
                                            {"qn_type": "sq",
                                             "theme_id": sq_list_item.get("theme_id"),
                                             "theme_name": sq_list_item.get("theme_name"),
                                             "topic_id": topic_ids,
                                             "topic_name": sq_list_item.get("topics")[0].get("topic_name"),
                                             "topic_sequence": sq_list_item.get("topics")[0].get("topic_sequence"),
                                             "total_avg_duration": (([int(s) for s in sq_list_item.get("topics")[0].get("average_duration").split(':')][0]) * 60 +[int(s) for s in sq_list_item.get("topics")[0].get("average_duration").split(':')][1]) / 3600,
                                             "count": 1,
                                             "test_created_date": [sq_list_item.get("topics")[0].get("create_date")],
                                             "users_attended": [sq_list_item.get("topics")[0].get("user")]
                                             })
                                        total_avg_time = 0
                                else:
                                    sq_status_list.append(
                                        {"qn_type": "sq",
                                         "theme_id": sq_list_item.get("theme_id"),
                                         "theme_name": sq_list_item.get("theme_name"),
                                         "topic_id": topic_ids,
                                         "topic_name": sq_list_item.get("topics")[0].get("topic_name"),
                                         "topic_sequence": sq_list_item.get("topics")[0].get("topic_sequence"),
                                         "total_avg_duration": total_avg_time,
                                         "count": 1,
                                         "test_created_date": [sq_list_item.get("topics")[0].get("create_date")],
                                         "users_attended": [sq_list_item.get("topics")[0].get("user")]
                                         })
            for sq_item in sq_status_list:
                sq_item["average_duration"] = round(sq_item["total_avg_duration"] / sq_item["count"], 2)
                del sq_item["total_avg_duration"]
                sq_item["frequency_day"] = self.get_frequency_per_day(sq_item["test_created_date"])
                sq_item["frequency_week"] = self.get_frequency_per_week(sq_item["test_created_date"], sq_item["count"])
                sq_item["frequency_month"] = self.get_frequency_per_month(sq_item["test_created_date"], sq_item["count"])
                sq_item["frequency_year"] = self.get_frequency_per_year(sq_item["test_created_date"], sq_item["count"])
                sq_item["no_of_respondents"] = len(sq_item["users_attended"])
                del sq_item["test_created_date"]
                del sq_item["users_attended"]
            # print(sq_status_list)
            mc_sq = mc_status_list + sq_status_list
            test_vals = {
                # "mc": mc_list,
                "mc": mc_status_list,
                # "sq": sq_list,
                "sq": sq_status_list,
                "mc_sq": mc_sq
            }
            message = "No data" if not mc_status_list and not sq_status_list else "Success"
            return Response({
                "success": True,
                "message": message,
                "data": test_vals,
            }, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            return Response({"success": False, "message": "Failed", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)
