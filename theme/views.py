from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from theme import serializers, models
from theme.models import Theme
from theme.models import Topic
from theme.models import Cards
from theme.models import Cardstitle
from theme.models import MC
from theme.models import McOptions
from theme.models import ShortQuestion
from theme.models import ShortQuestionMarkPoints
from theme.models import Learningfocus
from bookmarks.models import CardsBookmarks
from bookmarks.models import SQBookmarks
from bookmarks.models import MCBookmarks
from Test.models import TestDetails
import math
from region.pagination import CustomPagination
from openpyxl import load_workbook
from io import BytesIO
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser,MultiPartParser
# from django.http import MultiPartParser
import json
from django.http import JsonResponse
from django.db import connection


class ThemeUsageCreateApi(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ThemeUsage
    queryset = models.ThemeUsage.objects.all().order_by('-id')

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
            themes = models.ThemeUsage.objects.all()
            serializer = self.serializer_class(themes, many=True)
            if len(themes) < 1:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"success": True, "message": "Theme Details",
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


class ThemeTopicListCreate(generics.ListCreateAPIView):
    serializer_class = serializers.ThemeSerializer
    queryset = models.Theme.objects.all().order_by('-id')

    """
        List and Create Theme
    """
    # permission_classes = (IsAuthenticated,)
    queryset = models.Cards.objects.all().order_by('id')

    @api_view(['GET'])
    def snippet_detail(request):
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
            urls = str(http_layer + "://" + http_address)

            themes = Theme.objects.all().order_by('-id')
            for theme in themes.iterator():
                topic_list = []
                topics = Topic.objects.filter(theme_id=theme.id).order_by('id')
                for topic in topics:
                    card_list = []
                    cards = models.Learningfocus.objects.filter(topic_id=topic.id).order_by('id')
                    for card in cards:
                        card_dict = {
                            'id': card.id,
                            'topic_id': card.topic_id.id,
                            'english': card.english,
                            'chinese': card.chinese,
                            'created_date': card.created_date,
                            'updated_date': card.updated_date,
                        }
                        card_list.append(card_dict)
                    topic_dict = {
                        "id": topic.id,
                        "theme_id": topic.theme_id.id,
                        "topic_english_name": topic.topic_english_name,
                        "topic_chinese_name": topic.topic_chinese_name,
                        "learning_focus": topic.learning_focus,
                        "created_date": str(topic.created_date),
                        "updated_date": str(topic.updated_date),
                        "learning_cards": card_list
                    }
                    topic_list.append(topic_dict)
                theme_dict = {
                    "id": theme.id,
                    "theme_english_name": theme.theme_english_name,
                    "theme_chinese_name": theme.theme_chinese_name,
                    "theme_image": urls + "/media/" + str(theme.theme_image) or False,
                    "theme_color": theme.theme_color,
                    "english_tag": theme.english_tag,
                    "chinese_tag": theme.chinese_tag,
                    "theme_number": theme.theme_number,
                    "created_date": str(theme.created_date),
                    "updated_date": str(theme.updated_date),
                    "topics": topic_list
                }
                themes_dict.append(theme_dict)
                dicts = {}
            return Response({
                "success": True,
                "message": "Success",
                "data": themes_dict,
            }, status=status.HTTP_201_CREATED)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class ThemeTopicCardList(generics.ListCreateAPIView):
    serializer_class = serializers.ThemeSerializer
    queryset = models.Theme.objects.all().order_by('-id')

    """
        List and Create Theme
    """
    permission_classes = (IsAuthenticated,)
    queryset = models.Cards.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
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
            themes = Theme.objects.all().order_by('-id')
            for theme in themes.iterator():
                topic_list = []
                topics = Topic.objects.filter(theme_id=theme.id)
                for topic in topics:
                    card_title = models.Cardstitle.objects.filter(topic_id=topic.id)
                    card_list = []
                    for title in card_title:
                        cards = models.Cards.objects.filter(card_title_id=title.id)
                        current_user = request.user.id
                        for card in cards:
                            bookmark = False
                            bookmark_data = CardsBookmarks.objects.filter(card_id=card.id, partner_id=current_user)
                            if bookmark_data:
                                bookmark = True
                            card_dict = {
                                "card_thumbnail_background": urls + "/media/" + str(title.card_thumbnail_background) or False,
                                "card_full_background": urls + "/media/" + str(title.card_full_background) or False,
                                "is_bookmarked": bookmark,
                                'card_english_title': title.card_english_title,
                                'card_chinese_title': title.card_chinese_title,
                                'card_english_subtitle': title.card_english_subtitle,
                                'card_chinese_subtitle': title.card_chinese_subtitle,
                                'card_created_date': title.card_title_number,
                                'card_updated_date': title.card_title_number,
                                'id': card.id,
                                'card_title_id': card.card_title_id.id,
                                'card_english_summary_title': card.card_english_summary_title,
                                'card_chinese_summary_title': card.card_chinese_summary_title,
                                'card_english_summary': card.card_english_summary,
                                'card_chinese_summary': card.card_chinese_summary,
                                'card_number': card.card_number,
                                'created_date': card.created_date,
                                'updated_date': card.updated_date,
                            }
                            card_list.append(card_dict)
                    topic_dict = {
                        "id": topic.id,
                        "theme_id": topic.theme_id.id,
                        "topic_english_name": topic.topic_english_name,
                        "topic_chinese_name": topic.topic_chinese_name,
                        "learning_focus": topic.learning_focus,
                        "created_date": str(topic.created_date),
                        "updated_date": str(topic.updated_date),
                        "learning_cards": card_list
                    }
                    topic_list.append(topic_dict)
                theme_dict = {
                    "id": theme.id,
                    "theme_english_name": theme.theme_english_name,
                    "theme_chinese_name": theme.theme_chinese_name,
                    "theme_image": urls + "/media/" + str(theme.theme_image) or False,
                    "theme_color": theme.theme_color,
                    "english_tag": theme.english_tag,
                    "chinese_tag": theme.chinese_tag,
                    "theme_number": theme.theme_number,
                    "created_date": str(theme.created_date),
                    "updated_date": str(theme.updated_date),
                    "topics": topic_list
                }
                themes_dict.append(theme_dict)
                dicts = {}
            return Response({
                "success": True,
                "message": "Success",
                "data": themes_dict,
            }, status=status.HTTP_201_CREATED)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


class ThemeCreate(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.ThemeSerializer
    queryset = models.Theme.objects.all().order_by('-id')

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
            themes = models.Theme.objects.all().order_by('-id')
            serializer = serializers.ThemeSerializer(themes, many=True, context={"user": self.get_user(),'request': request})
            if len(themes) < 1:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"success": True, "message": "Theme Details",
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
        serializer = self.serializer_class(data=request.data, context={"user": self.get_user(), 'request': request})
        if serializer.is_valid():
            serializer.save()
            theme_data = Theme.objects.all().order_by('created_date')
            seq = 1
            for theme in theme_data:
                theme.sequence = seq
                theme.save()
                seq = seq + 1
            return Response({
                "success": True,
                "message": "Theme Created",
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
            theme_data = Theme.objects.all().order_by('created_date')
            seq = 1
            for theme in theme_data:
                theme.sequence = seq
                theme.save()
                seq = seq + 1

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
        serializer = serializers.ThemeSerializerPut(instance=snippets, data=request.data,context= {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class ThemeBulkDelete(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.ThemeSerializer
    queryset = models.Theme.objects.all().order_by('-id')

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


class TopicBulkDelete(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.TopicSerializer
    queryset = models.Topic.objects.all().order_by('-id')

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


class ThemeGetOne(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ThemeSerializerGet
    queryset = models.Theme.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request, pk):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            snippet = Theme.objects.get(pk=pk)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = serializers.ThemeSerializerGet(snippet, context={"request": request})
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)


class TopicCreate(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.TopicSerializer
    queryset = models.Topic.objects.all().order_by('-id')

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
            theme_id = request.data['theme_id']
            seq = 1
            if theme_id:
                topic_data = Topic.objects.filter(theme_id=theme_id).order_by('created_date')
                for topic in topic_data:
                    topic.sequence = seq
                    topic.save()
                    seq = seq + 1

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
        try:
            pk = request.data.get('id')
            snippets = self.queryset.filter(id=pk)
            data = Topic.objects.get(id=pk)
            theme_id = data.theme_id
            if snippets:
                snippets.delete()
                seq = 1
                if theme_id:
                    topic_data = Topic.objects.filter(theme_id=theme_id).order_by('created_date')
                    for topic in topic_data:
                        topic.sequence = seq
                        topic.save()
                        seq = seq + 1
                return Response({
                    "success": True,
                    "message": "Successfully Deleted",
                    "data": {},
                }, status=status.HTTP_201_CREATED)
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
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


class LearnigFocusCreate(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.LearningFocusSerializer
    queryset = models.Learningfocus.objects.all().order_by('-id')

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


class LearningFocusTopicCreate(generics.ListCreateAPIView):
    """
        List and Create cardtitle / card
    """

    # permission_classes = (IsAuthenticated,)
    topicSerializerUpdate = serializers.TopicSerializerUpdate
    learningFocusSerializer = serializers.LearningFocusSerializer
    queryset = models.Topic.objects.all().order_by('-id')
    queryset_learning = models.Learningfocus.objects.all().order_by('-id')
    queryset_topic = models.Topic.objects.all().order_by('-id')

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

    def get_card_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_learning.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_card_topic_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_topic.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """

        card = []
        card_fail = False
        card_serializer = []
        topic_json = request.data.get('topic')
        serializer = self.topicSerializerUpdate(data=topic_json, context={"user": self.get_user()})

        if serializer.is_valid():
            serializer.save()
            if serializer.data.get('id'):
                cards_json = request.data.get('learning_cards')
                for i in cards_json:
                    try:
                        i['topic_id'] = serializer.data.get('id')
                        serializercard = self.learningFocusSerializer(data=i, context={"user": self.get_user()})
                        if serializercard.is_valid():
                            serializercard.save()
                            card.append(serializercard.data.get('id'))
                            card_serializer.append(serializercard.data)
                        else:
                            card_fail = True
                    except:
                        card_fail = True
                if card_fail:
                    for j in card:
                        pk = j
                        snippets = self.get_card_object(pk)
                        if snippets:
                            snippets.delete()
                    pk1 = serializer.data.get('id')
                    snippets1 = self.get_card_topic_object(pk1)
                    if snippets1:
                        snippets1.delete()
                    return Response({"success": False, "message": "Failed to create Topic", "data": serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    theme_id = topic_json['theme_id']
                    seq = 1
                    if theme_id:
                        topic_data = Topic.objects.filter(theme_id=theme_id).order_by('created_date')
                        for topic in topic_data:
                            topic.sequence = seq
                            topic.save()
                            seq = seq + 1
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": {"cardtitle": serializer.data, "cards": card_serializer}
                    }, status=status.HTTP_201_CREATED)

            else:
                return Response({"success": False, "message": "Failed to create Learning Focus", "data": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class LearningFocusToipcForm(generics.ListCreateAPIView):
    """
        List and Create cardtitle / Form
    """
    # permission_classes = (IsAuthenticated,)
    topicSerializerUpdate = serializers.TopicSerializerUpdate
    learningFocusSerializer = serializers.LearningFocusSerializer
    queryset = models.Topic.objects.all().order_by('-id')
    queryset_learning = models.Learningfocus.objects.all().order_by('-id')
    queryset_topic = models.Topic.objects.all().order_by('-id')

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

    def get_card_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_learning.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_card_topic_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_topic.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        learning = []
        topic_id = request.data.get('id')

        topic = self.get_card_topic_object(topic_id)
        if topic:

            learning_cards = models.Learningfocus.objects.filter(topic_id=topic.id)
            for cards in learning_cards:
                d = {
                    'id': cards.id,
                    'topic_id': cards.topic_id.id,
                    'english': cards.english,
                    'chinese': cards.chinese,
                    'created_date': cards.created_date,
                    'updated_date': cards.updated_date,
                }
                learning.append(d)
            dict = {
               'id': topic.id,
               'theme_id': topic.theme_id.id,
               'topic_english_name': topic.topic_english_name,
               'topic_chinese_name': topic.topic_chinese_name,
               'learning_focus': topic.learning_focus,
               'created_date': topic.created_date,
               'updated_date': topic.updated_date,
               'learning_cards': learning
            }

            return Response({
                "success": True,
                "message": "Success",
                "data": dict
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "message": "Failed", "data": "Please check the topic id"},
                            status=status.HTTP_400_BAD_REQUEST)


class LearningFocusToipcUpdate(generics.ListCreateAPIView):
    """
        List and Create cardtitle / card
    """

    # permission_classes = (IsAuthenticated,)
    topicSerializerUpdate = serializers.TopicSerializerUpdate
    learningFocusSerializer = serializers.LearningFocusSerializerUpdate
    queryset = models.Topic.objects.all().order_by('-id')
    queryset_learning = models.Learningfocus.objects.all().order_by('-id')
    queryset_topic = models.Topic.objects.all().order_by('-id')

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

    def get_card_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_learning.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_card_topic_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_topic.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """

        topic = request.data.get('topic')
        topic_id = topic.get('id')
        snippets = self.get_object(topic_id)
        serializer = self.topicSerializerUpdate(instance=snippets, data=topic)
        if serializer.is_valid():
            cards_json = request.data.get('learning_cards')
            for i in cards_json:
                if i.get('id'):
                    card_snippets = self.get_card_object(i['id'])
                    aaa = self.queryset_learning.filter(id=1)
                    serializercard = self.learningFocusSerializer(instance=card_snippets, data=i)
                    if serializercard.is_valid():
                        serializercard.save()
                    else:
                        return Response({"success": False, "message": "Failed to update Learning card", "data": str(list(serializercard.errors.keys())[0]) +": "+ str(list(serializercard.errors.values())[0][0])},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializercard = self.learningFocusSerializer(data=i, context={"user": self.get_user()})
                    if serializercard.is_valid():
                        serializercard.save()

            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "message": "Failed to Update Topic/card", "data": str(list(serializer.errors.keys())[0]) +": "+ str(list(serializer.errors.values())[0][0])},
                            status=status.HTTP_400_BAD_REQUEST)


class TopicGetOne(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ThemeSerializerGet
    queryset = models.Topic.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request, pk):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            snippet = Topic.objects.get(pk=pk)
        except Topic.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = serializers.TopicSerializerGet(snippet)
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)


class CardsCreate(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CardsSerializer
    queryset = models.Cards.objects.all().order_by('-id')

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


class CardGetOne(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CardsSerializerGet
    queryset = models.Cards.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request, pk):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            snippet = Cards.objects.get(pk=pk)
        except Cards.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = serializers.CardsSerializerGet(snippet)
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)


class CardsTitleCreate(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    # permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.CardstitleSerializer
    queryset = models.Cardstitle.objects.all().order_by('-id')

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
        from .serializers import CardstitleSerializerUpdate
        serializer = CardstitleSerializerUpdate(instance=snippets, data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class CardTitleGetOne(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CardstitleSerializerGet
    queryset = models.Cardstitle.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request, pk):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            snippet = Cardstitle.objects.get(pk=pk)
        except Cardstitle.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = serializers.CardsSerializerGet(snippet)
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)


class ThemeTopicCreate(generics.ListCreateAPIView):
    """
        List and Create Theme / Topic
    """

    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ThemeSerializer
    serializer_topicSerializer = serializers.TopicSerializer
    queryset = models.Theme.objects.all().order_by('-id')
    queryset_theme = models.Theme.objects.all().order_by('-id')
    queryset_topic = models.Topic.objects.all().order_by('-id')

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

    def get_topic_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_topic.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_theme_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_theme.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """

        topic = []
        theme = []
        topic_fail = False
        topic_serializer = []
        theme_json = request.data.get('theme')
        serializer = self.serializer_class(data=theme_json, context={"user": self.get_user()})
        if serializer.is_valid():
            serializer.save()
            if serializer.data.get('id'):
                topic_json = request.data.get('topic')
                for i in topic_json:
                    i['theme_id'] = serializer.data.get('id')
                    serializertopic = self.serializer_topicSerializer(data=i, context={"user": self.get_user()})
                    if serializertopic.is_valid():
                        serializertopic.save()
                        topic.append(serializertopic.data.get('id'))
                        topic_serializer.append(serializertopic.data)
                    else:
                        topic_fail = True
                if topic_fail:
                    for j in topic:
                        pk = j
                        snippets = self.get_topic_object(pk)
                        if snippets:
                            snippets.delete()
                    pk1 = serializer.data.get('id')
                    snippets1 = self.get_theme_object(pk1)
                    if snippets1:
                        snippets1.delete()
                    return Response({"success": False, "message": "Failed to create Theme", "data": serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": {"theme": serializer.data, "topic": topic_serializer}
                    }, status=status.HTTP_201_CREATED)

            else:
                return Response({"success": False, "message": "Failed to create Theme", "data": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class ThemeIdTopicGet(generics.ListCreateAPIView):
    """
        List and Create Theme / Topic
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ThemeSerializer
    serializer_topicSerializer = serializers.TopicSerializer

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        topic_list = []
        id = request.data.get('id')
        try:
            snippet = Topic.objects.filter(theme_id=id)
        except Cards.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        for topic in snippet.iterator():
            topic_dict = {
                "id": topic.id,
                "theme_id": topic.theme_id.id,
                "topic_english_name": topic.topic_english_name,
                "topic_chinese_name": topic.topic_chinese_name,
                "learning_focus": topic.learning_focus,
                "created_date": str(topic.created_date),
                "updated_date": str(topic.updated_date)
            }
            topic_list.append(topic_dict)
        return Response({
            "success": True,
            "message": "Success",
            "data": topic_list,
        }, status=status.HTTP_201_CREATED)


class ThemeIdTopicUpdate(generics.ListCreateAPIView):
    """
        List and Create Theme / Topic
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ThemeSerializer
    serializer_topicSerializer = serializers.TopicSerializerUpdate
    queryset = models.Theme.objects.all().order_by('-id')
    queryset_theme = models.Theme.objects.all().order_by('-id')
    queryset_topic = models.Topic.objects.all().order_by('-id')

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

    def get_topic_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_topic.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_theme_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_theme.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """

        theme = request.data.get('theme')
        theme_id = theme.get('id')
        snippets = self.get_object(theme_id)
        serializer = self.serializer_class(instance=snippets, data=theme)
        if serializer.is_valid():
            topic_json = request.data.get('topic')
            for i in topic_json:
                topic_snippets = self.get_topic_object(i['id'])
                serializertopic = self.serializer_topicSerializer(instance=topic_snippets, data=i)
                if serializertopic.is_valid():
                    serializertopic.save()
                else:
                    return Response({"success": False, "message": "Failed to create Theme", "data": str(list(serializertopic.errors.keys())[0]) +": "+ str(list(serializertopic.errors.values())[0][0])},
                                    status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "message": "Failed to create Theme", "data": str(list(serializer.errors.keys())[0]) +": "+ str(list(serializer.errors.values())[0][0])},
                            status=status.HTTP_400_BAD_REQUEST)


class ThemeIdTopicFormView(generics.ListCreateAPIView):
    """
        List and Create Theme / Topic
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ThemeSerializer
    serializer_topicSerializer = serializers.TopicSerializer

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        id = request.data.get('id')
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
            urls = str(http_layer + "://" + http_address)

            themes = Theme.objects.filter(id=id)
            for theme in themes.iterator():
                topic_list = []
                topics = Topic.objects.filter(theme_id=theme.id)
                for topic in topics:
                    topic_dict = {
                        "id": topic.id,
                        "theme_id": topic.theme_id.id,
                        "topic_english_name": topic.topic_english_name,
                        "topic_chinese_name": topic.topic_chinese_name,
                        "learning_focus": topic.learning_focus,
                        "created_date": str(topic.created_date),
                        "updated_date": str(topic.updated_date)
                    }
                    topic_list.append(topic_dict)
                theme_dict = {
                    "id": theme.id,
                    "theme_english_name": theme.theme_english_name,
                    "theme_chinese_name": theme.theme_chinese_name,
                    "theme_image": urls + "/media/" + str(theme.theme_image) or False,
                    "theme_color": theme.theme_color,
                    "theme_number": theme.theme_number,
                    "created_date": str(theme.created_date),
                    "updated_date": str(theme.updated_date),
                    "topics": topic_list
                }
                themes_dict.append(theme_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": themes_dict,
            }, status=status.HTTP_201_CREATED)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class CardCartitleCreate(generics.ListCreateAPIView):
    """
        List and Create cardtitle / card
    """

    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.CardsSerializer
    serializer_titleSerializer = serializers.CardstitleSerializer
    queryset = models.Cardstitle.objects.all().order_by('-id')
    queryset_cards = models.Cards.objects.all().order_by('-id')
    queryset_cardstitle = models.Cardstitle.objects.all().order_by('-id')

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

    def get_card_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_cards.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_card_title_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_cardstitle.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """

        card = []
        card_fail = False
        card_serializer = []
        cardtitle_json = request.data.get('cardtitle')
        serializer = self.serializer_titleSerializer(data=cardtitle_json, context={"user": self.get_user()})
        if serializer.is_valid():
            serializer.save()
            if serializer.data.get('id'):
                cards_json = request.data.get('cards')
                for i in cards_json:
                    try:
                        i['card_title_id'] = serializer.data.get('id')
                        serializercard = self.serializer_class(data=i, context={"user": self.get_user()})
                        if serializercard.is_valid():
                            serializercard.save()
                            card.append(serializercard.data.get('id'))
                            card_serializer.append(serializercard.data)
                        else:
                            card_fail = True
                    except:
                        card_fail = True
                if card_fail:
                    for j in card:
                        pk = j
                        snippets = self.get_card_object(pk)
                        if snippets:
                            snippets.delete()
                    pk1 = serializer.data.get('id')
                    snippets1 = self.get_card_title_object(pk1)
                    if snippets1:
                        snippets1.delete()
                    return Response({"success": False, "message": "Failed to create Theme", "data": serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": {"cardtitle": serializer.data, "cards": card_serializer}
                    }, status=status.HTTP_201_CREATED)

            else:
                return Response({"success": False, "message": "Failed to create Learning Card", "data": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)




class CardCartitleUpdate(generics.ListCreateAPIView):
    """
        List and Create Theme / Topic
    """

    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.CardsSerializer
    serializer_titleSerializer = serializers.CardstitleSerializer
    queryset = models.Cardstitle.objects.all().order_by('-id')
    queryset_cards = models.Cards.objects.all().order_by('-id')
    queryset_cardstitle = models.Cardstitle.objects.all().order_by('-id')

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

    def get_card_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_cards.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_card_title_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_cardstitle.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """

        cardtitle = request.data.get('cardtitle')
        cardtitle_id = cardtitle.get('id')
        snippets = self.get_object(cardtitle_id)
        serializer = self.serializer_titleSerializer(instance=snippets, data=cardtitle)
        if serializer.is_valid():
            cards_json = request.data.get('cards')
            for i in cards_json:
                if i.get('id'):
                    card_snippets = self.get_card_object(i['id'])
                    serializercard = self.serializer_class(instance=card_snippets, data=i)
                    if serializercard.is_valid():
                        serializercard.save()
                    else:
                        return Response({"success": False, "message": "Failed to update card", "data": str(list(serializercard.errors.keys())[0]) +": "+ str(list(serializercard.errors.values())[0][0])},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializercards = self.serializer_class(data=i, context={"user": self.get_user()})
                    if serializercards.is_valid():
                        serializercards.save()

            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "message": "Failed to Update Card", "data": str(list(serializer.errors.keys())[0]) +": "+ str(list(serializer.errors.values())[0][0])},
                            status=status.HTTP_400_BAD_REQUEST)


class CardCartitleForm(generics.ListCreateAPIView):
    """
        List and Create Theme / Topic
    """

    # permission_classes = (IsAuthenticated,)
    # serializer_class = serializers.CardsSerializer
    # serializer_class = serializers.CardsSerializer
    serializer_class = serializers.CardsSerializer
    serializer_titleSerializer = serializers.CardstitleSerializer
    queryset = models.Cardstitle.objects.all().order_by('-id')
    queryset_cards = models.Cards.objects.all().order_by('-id')
    queryset_cardstitle = models.Cardstitle.objects.all().order_by('-id')

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

    def get_card_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_cards.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_card_title_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_cardstitle.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        id = request.data.get('id')
        title_dict = []
        try:
            import socket
            import re
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            url = request.build_absolute_uri()

            http_layer = request.is_secure() and "https" or "http"
            http_address = request.get_host()
            urls = str(http_layer+"://"+http_address)
            card_title = Cardstitle.objects.filter(id=id)
            for title in card_title.iterator():
                card_list = []
                cards = Cards.objects.filter(card_title_id=title.id)
                current_user = request.user.id
                for card in cards:
                    bookmark = False
                    bookmark_data = CardsBookmarks.objects.filter(card_id=card.id, partner_id=current_user)
                    if bookmark_data:
                        bookmark = True
                    card_dict = {
                        "id": card.id,
                        "is_bookmarked": bookmark,
                        "card_title_id": card.card_title_id.id if card.card_title_id else False,
                        "card_english_summary_title": card.card_english_summary_title,
                        "card_chinese_summary_title": card.card_chinese_summary_title,
                        "card_english_summary": card.card_english_summary,
                        "card_chinese_summary": card.card_chinese_summary,
                        "card_number": card.card_number,
                        "created_date": str(card.created_date),
                        "updated_date": str(card.updated_date)
                    }
                    card_list.append(card_dict)
                catitle_dict = {
                    "id": title.id,
                    "topic_id": title.topic_id.id if title.topic_id else False,
                    "theme_id": title.theme_id.id if title.theme_id else False,
                    "card_thumbnail_background": urls+"/media/"+str(title.card_thumbnail_background) or False,
                    "card_full_background": urls+"/media/"+str(title.card_full_background) or False,
                    "card_english_title": title.card_english_title,
                    "card_chinese_title": title.card_chinese_title,
                    "card_english_subtitle": title.card_english_subtitle,
                    "card_chinese_subtitle": title.card_chinese_subtitle,
                    "card_title_number": title.card_title_number,
                    "created_date": str(title.created_date),
                    "updated_date": str(title.updated_date),
                    "cards": card_list
                }
                title_dict.append(catitle_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": title_dict,
            }, status=status.HTTP_201_CREATED)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class CardTitleList(generics.ListCreateAPIView):
    """
        List and Create Theme / Topic
    """

    serializer_class = serializers.CardsSerializer
    serializer_titleSerializer = serializers.CardstitleSerializer
    queryset = models.Cardstitle.objects.all().order_by('-id')
    queryset_cards = models.Cards.objects.all().order_by('-id')
    queryset_cardstitle = models.Cardstitle.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            title_dict = []
            card_title = Cardstitle.objects.all()
            for title in card_title.iterator():
                card_list = []
                cards = Cards.objects.filter(card_title_id=title.id)
                current_user = request.user.id
                for card in cards:
                    bookmark = False
                    bookmark_data = CardsBookmarks.objects.filter(card_id=card.id, partner_id=current_user)
                    if bookmark_data:
                        bookmark = True

                    card_dict = {
                        "id": card.id,
                        "is_bookmarked": bookmark,
                        "card_title_id": card.card_title_id.id,
                        "card_english_summary_title": card.card_english_summary_title,
                        "card_chinese_summary_title": card.card_chinese_summary_title,
                        "card_english_summary": card.card_english_summary,
                        "card_chinese_summary": card.card_chinese_summary,
                        "card_number": card.card_number,
                        "created_date": str(card.created_date),
                        "updated_date": str(card.updated_date)
                    }
                    card_list.append(card_dict)
                catitle_dict = {
                    "id": title.id,
                    "topic_id": title.topic_id.id if title.topic_id else False,
                    "theme_id": title.theme_id.id if title.theme_id else False,
                    "card_english_title": title.card_english_title,
                    "card_chinese_title": title.card_chinese_title,
                    "card_english_subtitle": title.card_english_subtitle,
                    "card_chinese_subtitle": title.card_chinese_subtitle,
                    "card_title_number": title.card_title_number,
                    "created_date": str(title.created_date),
                    "updated_date": str(title.updated_date),
                    "cards": card_list
                }
                title_dict.append(catitle_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": title_dict,
            }, status=status.HTTP_200_OK)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class CardTitleListViewFilter(generics.ListCreateAPIView):
    """
        List and List Theme / Topic
    """

    serializer_class = serializers.CardsSerializer
    serializer_titleSerializer = serializers.CardstitleSerializer
    queryset = models.Cardstitle.objects.all().order_by('-id')
    queryset_cards = models.Cards.objects.all().order_by('-id')
    queryset_cardstitle = models.Cardstitle.objects.all().order_by('-id')

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

    def get_card_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_cards.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_card_title_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_cardstitle.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        theme_id = request.data.get('theme_id')
        topic_id = request.data.get('topic_id')
        title_dict = []
        try:
            import math
            page_size = 10
            paginator = CustomPagination()
            paginator.page_size = page_size
            title_dict = []
            card_title = Cardstitle.objects.all().order_by('id')
            if theme_id and topic_id:
                card_title = Cardstitle.objects.filter(theme_id=theme_id, topic_id=topic_id)
            elif theme_id:
                card_title = Cardstitle.objects.filter(theme_id=theme_id)
            elif topic_id:
                card_title = Cardstitle.objects.filter(topic_id=topic_id)
            else:
                card_title = Cardstitle.objects.all().order_by('id')
            for title in card_title.iterator():
                card_list = []
                cards = Cards.objects.filter(card_title_id=title.id)
                current_user = request.user.id
                for card in cards:
                    bookmark = False
                    bookmark_data = CardsBookmarks.objects.filter(card_id=card.id, partner_id=current_user)
                    if bookmark_data:
                        bookmark = True
                    card_dict = {
                        "id": card.id,
                        "is_bookmarked": bookmark,
                        "card_title_id": card.card_title_id.id,
                        "card_english_summary_title": card.card_english_summary_title,
                        "card_chinese_summary_title": card.card_chinese_summary_title,
                        "card_english_summary": card.card_english_summary,
                        "card_chinese_summary": card.card_chinese_summary,
                        "card_number": card.card_number,
                        "created_date": str(card.created_date),
                        "updated_date": str(card.updated_date)
                    }
                    card_list.append(card_dict)
                catitle_dict = {
                    "id": title.id,
                    "sequence": title.topic_id.sequence if title.topic_id else False,
                    "theme_sequence": title.theme_id.sequence if title.theme_id else False,
                    "topic_id": title.topic_id.id if title.topic_id else False,
                    "theme_id": title.theme_id.id if title.theme_id else False,
                    "english_tag": title.theme_id.english_tag if title.theme_id else False,
                    "chinese_tag": title.theme_id.chinese_tag if title.theme_id else False,
                    "topic_english_name": title.topic_id.topic_english_name if title.topic_id else False,
                    "topic_chinese_name": title.topic_id.topic_chinese_name if title.topic_id else False,
                    "theme_english_name": title.theme_id.theme_english_name if title.theme_id else False,
                    "theme_chinese_name": title.theme_id.theme_chinese_name if title.theme_id else False,
                    "card_english_title": title.card_english_title,
                    "card_chinese_title": title.card_chinese_title,
                    "card_english_subtitle": title.card_english_subtitle,
                    "card_chinese_subtitle": title.card_chinese_subtitle,
                    "card_title_number": title.card_title_number,
                    "created_date": str(title.created_date),
                    "updated_date": str(title.updated_date),
                    "cards": card_list
                }

                title_dict.append(catitle_dict)
            result_page = paginator.paginate_queryset(title_dict, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(title_dict) > 0:
                paginator_data['total_pages'] = math.ceil(len(title_dict) / page_size)
            else:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "success": True,
                "message": "Success",
                "data": paginator_data,
            }, status=status.HTTP_200_OK)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class CardTitleListView(generics.ListCreateAPIView):
    """
        List and Create Theme / Topic
    """

    serializer_class = serializers.CardsSerializer
    serializer_titleSerializer = serializers.CardstitleSerializer
    queryset = models.Cardstitle.objects.all().order_by('-id')
    queryset_cards = models.Cards.objects.all().order_by('-id')
    queryset_cardstitle = models.Cardstitle.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            title_dict = []
            card_title = Cardstitle.objects.all()
            for title in card_title.iterator():
                card_list = []
                cards = Cards.objects.filter(card_title_id=title.id)
                current_user = request.user.id
                for card in cards:
                    bookmark = False
                    bookmark_data = CardsBookmarks.objects.filter(card_id=card.id, partner_id=current_user)
                    if bookmark_data:
                        bookmark = True

                    card_dict = {
                        "id": title.id,
                        "is_bookmarked": bookmark,
                        "topic_id": title.topic_id.id if title.topic_id else False,
                        "theme_id": title.theme_id.id if title.theme_id else False,
                        "card_english_title": title.card_english_title,
                        "card_chinese_title": title.card_chinese_title,
                        "card_english_subtitle": title.card_english_subtitle,
                        "card_chinese_subtitle": title.card_chinese_subtitle,
                        "card_title_number": title.card_title_number,
                        "created_date": str(title.created_date),
                        "updated_date": str(title.updated_date),
                        "card_id": card.id,
                        "card_title_id": card.card_title_id.id,
                        "card_english_summary_title": card.card_english_summary_title,
                        "card_chinese_summary_title": card.card_chinese_summary_title,
                        "card_english_summary": card.card_english_summary,
                        "card_chinese_summary": card.card_chinese_summary,
                        "card_number": card.card_number,
                        "card_created_date": str(card.created_date),
                        "card_updated_date": str(card.updated_date)
                    }
                title_dict.append(card_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": title_dict,
            }, status=status.HTTP_200_OK)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class CardTitleListViewItem(generics.ListCreateAPIView):
    """
        List and Create Theme / Topic
    """

    serializer_class = serializers.CardsSerializer
    serializer_titleSerializer = serializers.CardstitleSerializer
    queryset = models.Cardstitle.objects.all().order_by('-id')
    queryset_cards = models.Cards.objects.all().order_by('-id')
    queryset_cardstitle = models.Cardstitle.objects.all().order_by('-id')

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

    def get_card_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_cards.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_card_title_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_cardstitle.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            id = request.data.get('id')
            title_dict = []
            card_title = Cardstitle.objects.filter(id=id)
            for title in card_title.iterator():
                card_list = []
                cards = Cards.objects.filter(card_title_id=title.id)
                card_dict = {}
                current_user = request.user.id
                for card in cards:
                    bookmark = False
                    bookmark_data = CardsBookmarks.objects.filter(card_id=card.id, partner_id=current_user)
                    if bookmark_data:
                        bookmark = True
                    card_dict = {
                        "id": title.id,
                        "is_bookmarked": bookmark,
                        "topic_id": title.topic_id.id if title.topic_id else False,
                        "theme_id": title.theme_id.id if title.theme_id else False,
                        "card_english_title": title.card_english_title,
                        "card_chinese_title": title.card_chinese_title,
                        "card_english_subtitle": title.card_english_subtitle,
                        "card_chinese_subtitle": title.card_chinese_subtitle,
                        "card_title_number": title.card_title_number,
                        "created_date": str(title.created_date),
                        "updated_date": str(title.updated_date),
                        "card_id": card.id,
                        "card_title_id": card.card_title_id.id,
                        "card_english_summary_title": card.card_english_summary_title,
                        "card_chinese_summary_title": card.card_chinese_summary_title,
                        "card_english_summary": card.card_english_summary,
                        "card_chinese_summary": card.card_chinese_summary,
                        "card_number": card.card_number,
                        "card_created_date": str(card.created_date),
                        "card_updated_date": str(card.updated_date)
                    }
                title_dict.append(card_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": title_dict,
            }, status=status.HTTP_200_OK)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class McCreate(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.MCSerializer
    queryset = models.MC.objects.all().order_by('-id')

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

            seq = 1
            mc_data = MC.objects.all().order_by('id')
            if mc_data:
                for mc in mc_data:
                    mc.mc_sequence = seq
                    mc.save()
                    seq = seq + 1

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

            seq = 1
            mc_data = MC.objects.all().order_by('id')
            if mc_data:
                for mc in mc_data:
                    mc.mc_sequence = seq
                    mc.save()
                    seq = seq + 1

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


class McOptionsCreate(generics.ListCreateAPIView):
    """
        List and Create MC / Options
    """

    # permission_classes = (IsAuthenticated,)
    # serializer_class = serializers.CardsSerializer
    # serializer_class = serializers.CardsSerializer
    serializer_class = serializers.MCSerializer
    serializer_optionSerializer = serializers.OptionSerializer
    queryset = models.MC.objects.all().order_by('-id')
    queryset_theme = models.MC.objects.all().order_by('-id')
    queryset_topic = models.McOptions.objects.all().order_by('-id')

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

    def get_topic_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_topic.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_theme_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_theme.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """

        options = []
        mc = []
        option_fail = False
        option_serializer = []
        mc_json = request.data.get('mc')
        serializer = self.serializer_class(data=mc_json, context={"user": self.get_user()})
        if serializer.is_valid():
            serializer.save()
            if serializer.data.get('id'):
                option_json = request.data.get('option')
                for i in option_json:
                    i['mc_id'] = serializer.data.get('id')
                    serializertopic = self.serializer_optionSerializer(data=i, context={"user": self.get_user()})
                    if serializertopic.is_valid():
                        serializertopic.save()
                        mc.append(serializertopic.data.get('id'))
                        options.append(serializertopic.data)
                    else:
                        option_fail = True
                if option_fail:
                    for j in options:
                        pk = j
                        snippets = self.get_topic_object(pk)
                        if snippets:
                            snippets.delete()
                    pk1 = serializer.data.get('id')
                    snippets1 = self.get_theme_object(pk1)
                    if snippets1:
                        snippets1.delete()
                    return Response({"success": False, "message": "Failed to create Mc", "data": serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": {"mc": serializer.data, "option": options}
                    }, status=status.HTTP_201_CREATED)

            else:
                return Response({"success": False, "message": "Failed to create Mc", "data": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class McOptionsFilter(generics.ListCreateAPIView):
    """
        List and Create MC / Options
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.MCSerializer
    serializer_optionSerializer = serializers.OptionSerializer
    queryset = models.MC.objects.all().order_by('-id')
    queryset_theme = models.Theme.objects.all().order_by('-id')
    queryset_topic = models.McOptions.objects.all().order_by('-id')

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

    def get_topic_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_topic.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_theme_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_theme.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        page_size = request.data.get('show_entries')
        try:
            import math
            if not page_size:
                page_size = 10
            paginator = CustomPagination()
            paginator.page_size = page_size
            mc_dict = []
            filters = {
                'topic_id': 'topic_id',
                'theme_id': 'theme_id',
            }
            selected_filters = {k: v for k, v in request.data.items() if v}
            mc_info = MC.objects.all().order_by('id')
            for key, value in selected_filters.items():
                mc_info = mc_info.filter(**{filters[key]: value})

            current_user = request.user.id

            total_mark = 0
            obtained_total_mark = 0

            # seq = 1
            # for mc_val in mc_info:
            #     mc_val.mc_sequence = seq
            #     mc_val.save()
            #     seq = seq + 1

            for mc in mc_info.iterator():
                bookmark = False
                bookmark_data = MCBookmarks.objects.filter(mc_id=mc.id, partner_id=current_user)
                if bookmark_data:
                    bookmark = True
                option_list = []
                mc_options = McOptions.objects.filter(mc_id=mc.id)
                test_details = TestDetails.objects.filter(mc_id=mc.id, is_mc=True)
                no_of_respondents = len(test_details)
                total_mark = 0
                obtained_total_mark = 0
                for total in test_details:
                    total_mark = total_mark+total.total_mark
                    obtained_total_mark = obtained_total_mark+total.obtained_total_mark

                correct_percentage = 0
                incorrect_percentage = 0
                if obtained_total_mark > 0 and total_mark > 0:
                    correct_percentage = (obtained_total_mark/total_mark)*100
                    incorrect_percentage = 100-correct_percentage
                elif total_mark <= 0:
                    correct_percentage = 0
                    incorrect_percentage = 0
                elif obtained_total_mark <= 0:
                    correct_percentage = 0
                    incorrect_percentage = 100

                option_list = list(mc_options.values(
                    'id',
                    'mc_id__id',
                    'mc_english_options',
                    'mc_chinese_options',
                    'mc_answer_index',
                    'created_date',
                    'updated_date'
                ))
                for option in option_list:
                    option['created_date'] = str(option['created_date'])
                    option['updated_date'] = str(option['updated_date'])

                mc_info_dict = {
                    "id": mc.id,
                    "mc_sequence": mc.mc_sequence,
                    "sequence": mc.topic_id.sequence if mc.topic_id else False,
                    "theme_sequence": mc.theme_id.sequence if mc.theme_id else False,
                    "theme_id": mc.theme_id.id if mc.theme_id else False,
                    "english_tag": mc.theme_id.english_tag if mc.theme_id else False,
                    "chinese_tag": mc.theme_id.chinese_tag if mc.theme_id else False,
                    "topic_id": mc.topic_id.id if mc.topic_id else False,
                    "is_bookmarked": bookmark,
                    "topic_english_name": mc.topic_id.topic_english_name if mc.topic_id else False,
                    "topic_chinese_name": mc.topic_id.topic_chinese_name if mc.topic_id else False,
                    "theme_english_name": mc.theme_id.theme_english_name if mc.theme_id else False,
                    "theme_chinese_name": mc.theme_id.theme_chinese_name if mc.theme_id else False,
                    "learning_focus_id": mc.learning_focus_id.id if mc.learning_focus_id else False,
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
                    "total_mark": total_mark,
                    "obtained_total_mark": obtained_total_mark,
                    "no_of_respondents": no_of_respondents,
                    "correct_percentage": round(correct_percentage, 2),
                    "incorrect_percentage": round(incorrect_percentage, 2),
                    "created_date": str(mc.created_date),
                    "updated_date": str(mc.updated_date),
                    "option_list": option_list
                }

                mc_dict.append(mc_info_dict)

            result_page = paginator.paginate_queryset(mc_dict, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(mc_dict) > 0:
                paginator_data['total_pages'] = math.ceil(len(mc_dict) / page_size)
            else:
                return Response({"success": True, "message": "No data", "data": {}},
                                status=status.HTTP_200_OK)

            return Response({
                "success": True,
                "message": "Success",
                "data": paginator_data
            }, status=status.HTTP_200_OK)
        except MC.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class McOptionList(generics.ListCreateAPIView):
    """
        List and Create Theme / Topic
    """

    serializer_class = serializers.CardsSerializer
    serializer_titleSerializer = serializers.CardstitleSerializer
    queryset = models.MC.objects.all().order_by('-id')
    queryset_cards = models.McOptions.objects.all().order_by('-id')
    queryset_cardstitle = models.MC.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
        """
        Retrieve, Mc And Mc Options snippet.
        """
        try:
            mc_dict = []
            mc_info = MC.objects.all().order_by('id')
            current_user = request.user.id
            for mc in mc_info.iterator():
                bookmark = False
                bookmark_data = MCBookmarks.objects.filter(mc_id=mc.id, partner_id=current_user)
                if bookmark_data:
                    bookmark = True
                option_list = []
                mc_options = McOptions.objects.filter(mc_id=mc.id)
                for option in mc_options:
                    option_dict = {
                        "id": option.id,
                        "mc_id": option.mc_id.id if option.mc_id else False,
                        "mc_english_options": option.mc_english_options,
                        "mc_chinese_options": option.mc_chinese_options,
                        "mc_answer_index": option.mc_answer_index,
                        "created_date": str(option.created_date),
                        "updated_date": str(option.updated_date)
                    }
                    option_list.append(option_dict)
                mc_info_dict = {
                    "id": mc.id,
                    "theme_id": mc.theme_id.id if mc.theme_id else False,
                    "topic_id": mc.topic_id.id if mc.topic_id else False,
                    "learning_focus_id": mc.learning_focus_id.id if mc.learning_focus_id else False,
                    "is_bookmarked": bookmark,
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
                    "created_date": str(mc.created_date),
                    "updated_date": str(mc.updated_date),
                    "option_list": option_list
                }
                mc_dict.append(mc_info_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": mc_dict,
            }, status=status.HTTP_200_OK)
        except MC.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class McOptionsForm(generics.ListCreateAPIView):
    """
        List and Create Theme / Topic
    """

    # permission_classes = (IsAuthenticated,)
    # serializer_class = serializers.CardsSerializer
    # serializer_class = serializers.CardsSerializer
    serializer_class = serializers.MCSerializer
    serializer_optionSerializer = serializers.OptionSerializer
    queryset = models.MC.objects.all().order_by('-id')
    queryset_theme = models.MC.objects.all().order_by('-id')
    queryset_topic = models.McOptions.objects.all().order_by('-id')

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

    def get_topic_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_topic.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_theme_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_theme.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """

        options = []
        mc = []
        option_fail = False
        option_serializer = []
        mc_id = request.data.get('id')
        try:
            mc_dict = []
            mc_info = MC.objects.filter(id=mc_id)
            current_user = request.user.id
            for mc in mc_info.iterator():
                bookmark = False
                bookmark_data = MCBookmarks.objects.filter(mc_id=mc.id, partner_id=current_user)
                if bookmark_data:
                    bookmark = True
                option_list = []
                mc_options = McOptions.objects.filter(mc_id=mc.id)
                for option in mc_options:
                    option_dict = {
                        "id": option.id,
                        "mc_id": option.mc_id.id,
                        "mc_english_options": option.mc_english_options,
                        "mc_chinese_options": option.mc_chinese_options,
                        "mc_answer_index": option.mc_answer_index,
                        "created_date": str(option.created_date),
                        "updated_date": str(option.updated_date)
                    }
                    option_list.append(option_dict)
                mc_info_dict = {
                    "id": mc.id,
                    "theme_id": mc.theme_id.id,
                    "topic_id": mc.topic_id.id,
                    "learning_focus_id": mc.learning_focus_id.id,
                    "is_bookmarked": bookmark,
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
                    "created_date": str(mc.created_date),
                    "updated_date": str(mc.updated_date),
                    "option_list": option_list
                }
                mc_dict.append(mc_info_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": mc_dict,
            }, status=status.HTTP_200_OK)
        except MC.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class McOptionsUpdate(generics.ListCreateAPIView):
    """
        Mc Mc option update
    """

    # permission_classes = (IsAuthenticated,)
    # serializer_class = serializers.CardsSerializer
    # serializer_class = serializers.CardsSerializer
    serializer_class = serializers.OptionSerializer
    serializer_mc_Serializer = serializers.MCSerializer
    queryset = models.MC.objects.all().order_by('-id')
    queryset_mcoption = models.McOptions.objects.all().order_by('-id')
    queryset_mc = models.MC.objects.all().order_by('-id')

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

    def get_card_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_mcoption.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_card_title_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_mc.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """

        mc_json = request.data.get('mc')
        mc_id = mc_json.get('id')
        snippets = self.get_object(mc_id)
        serializer = self.serializer_mc_Serializer(instance=snippets, data=mc_json)
        if serializer.is_valid():
            options_json = request.data.get('option')
            for i in options_json:
                if i.get('id'):
                    option_snippets = self.get_card_object(i['id'])
                    serializercard = self.serializer_class(instance=option_snippets, data=i)
                    if serializercard.is_valid():
                        serializercard.save()
                    else:
                        return Response({"success": False, "message": "Failed to update MC", "data": str(list(serializercard.errors.keys())[0]) +": "+ str(list(serializercard.errors.values())[0][0])},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializercards = self.serializer_class(data=i, context={"user": self.get_user()})
                    if serializercards.is_valid():
                        serializercards.save()
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "message": "Failed to Update MC", "data": str(list(serializer.errors.keys())[0]) +": "+ str(list(serializer.errors.values())[0][0])},
                            status=status.HTTP_400_BAD_REQUEST)


class SqCreate(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.SQSerializer
    queryset = models.ShortQuestion.objects.all().order_by('-id')

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

            seq = 1
            sq_data = ShortQuestion.objects.all().order_by('id')
            if sq_data:
                for sq in sq_data:
                    sq.sq_sequence = seq
                    sq.save()
                    seq = seq + 1
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

            seq = 1
            sq_data = ShortQuestion.objects.all().order_by('id')
            if sq_data:
                for sq in sq_data:
                    sq.sq_sequence = seq
                    sq.save()
                    seq = seq + 1

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


class SqMarkCreate(generics.ListCreateAPIView):
    """
        List and Create SQ / Mark
    """

    # permission_classes = (IsAuthenticated,)
    # serializer_class = serializers.CardsSerializer
    # serializer_class = serializers.CardsSerializer
    serializer_class = serializers.SQSerializer
    serializer_markSerializer = serializers.MarkPointsSerializer
    queryset = models.ShortQuestion.objects.all().order_by('-id')
    queryset_theme = models.ShortQuestion.objects.all().order_by('-id')
    queryset_topic = models.ShortQuestionMarkPoints.objects.all().order_by('-id')

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

    def get_topic_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_topic.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_theme_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_theme.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create SQ Mark
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """

        mark = []
        sq = []
        mark_fail = False
        mark_serializer = []
        sq_json = request.data.get('sq')
        serializer = self.serializer_class(data=sq_json, context={"user": self.get_user()})
        if serializer.is_valid():
            serializer.save()
            if serializer.data.get('id'):
                mark_json = request.data.get('marks')
                for i in mark_json:
                    i['sq_id'] = serializer.data.get('id')
                    serializertopic = self.serializer_markSerializer(data=i, context={"user": self.get_user()})
                    if serializertopic.is_valid():
                        serializertopic.save()
                        sq.append(serializertopic.data.get('id'))
                        mark.append(serializertopic.data)
                    else:
                        mark_fail = True
                if mark_fail:
                    for j in mark:
                        pk = j
                        snippets = self.get_topic_object(pk)
                        if snippets:
                            snippets.delete()
                    pk1 = serializer.data.get('id')
                    snippets1 = self.get_theme_object(pk1)
                    if snippets1:
                        snippets1.delete()
                    return Response({"success": False, "message": "Failed to Create SQ", "data": serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": {"sq": serializer.data, "mark": mark}
                    }, status=status.HTTP_201_CREATED)

            else:
                return Response({"success": False, "message": "Failed to create Mc", "data": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class SqMarkUpdate(generics.ListCreateAPIView):
    """
        SQ/Mark update
    """

    # permission_classes = (IsAuthenticated,)
    # serializer_class = serializers.CardsSerializer
    # serializer_class = serializers.CardsSerializer
    serializer_class = serializers.MarkPointsSerializer
    serializer_sq_Serializer = serializers.SQSerializer
    queryset = models.ShortQuestion.objects.all().order_by('-id')
    queryset_sq_mark = models.ShortQuestionMarkPoints.objects.all().order_by('-id')
    queryset_sq = models.ShortQuestion.objects.all().order_by('-id')

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

    def get_card_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_sq_mark.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_card_title_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_sq.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            Update SQ / Mark
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """

        sq_json = request.data.get('sq')
        sq_id = sq_json.get('id')
        snippets = self.get_object(sq_id)
        serializer = self.serializer_sq_Serializer(instance=snippets, data=sq_json)
        if serializer.is_valid():
            mark_json = request.data.get('mark')
            for i in mark_json:
                if i.get('id'):
                    mark_snippets = self.get_card_object(i['id'])
                    serializercard = self.serializer_class(instance=mark_snippets, data=i)
                    if serializercard.is_valid():
                        serializercard.save()
                    else:
                        return Response({"success": False, "message": "Failed to update Mark", "data": str(list(serializercard.errors.keys())[0]) +": "+ str(list(serializercard.errors.values())[0][0])},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializercards = self.serializer_class(data=i, context={"user": self.get_user()})
                    if serializercards.is_valid():
                        serializercards.save()

            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
                "mark": serializercard.data,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "message": "Failed to Update SQ", "data": str(list(serializer.errors.keys())[0]) +": "+ str(list(serializer.errors.values())[0][0])},
                            status=status.HTTP_400_BAD_REQUEST)


class SqMarkList(generics.ListCreateAPIView):
    """
        List SQ/MARK
    """

    serializer_class = serializers.SQSerializer
    serializer_titleSerializer = serializers.MarkPointsSerializer
    queryset = models.ShortQuestion.objects.all().order_by('-id')
    queryset_cards = models.ShortQuestionMarkPoints.objects.all().order_by('-id')
    queryset_cardstitle = models.ShortQuestion.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
        """
        Retrieve, SQ and Mark snippet.
        """
        try:
            sq_dict = []
            sq_info = ShortQuestion.objects.all().order_by('id')
            current_user = request.user.id
            for sq in sq_info.iterator():
                bookmark = False
                bookmark_data = SQBookmarks.objects.filter(sq_id=sq.id, partner_id=current_user)
                if bookmark_data:
                    bookmark = True
                mark_list = []
                sq_mark = ShortQuestionMarkPoints.objects.filter(sq_id=sq.id)
                for mark in sq_mark:
                    mark_dict = {
                        "id": mark.id,
                        "sq_id": mark.sq_id.id if mark.sq_id else False,
                        "sq_english_mark_points": mark.sq_english_mark_points,
                        "sq_chinese_mark_points": mark.sq_chinese_mark_points,
                        "sq_english_mark": mark.sq_english_mark,
                        "sq_chinese_mark": mark.sq_chinese_mark,
                        "created_date": str(mark.created_date),
                        "updated_date": str(mark.updated_date)
                    }
                    mark_list.append(mark_dict)
                sq_info_dict = {
                    "id": sq.id,
                    "theme_id": sq.theme_id.id if sq.theme_id else False,
                    "topic_id": sq.topic_id.id if sq.topic_id else False,
                    "learning_focus_id": sq.learning_focus_id.id if sq.learning_focus_id else False,
                    "is_bookmarked": bookmark,
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
                    "created_date": str(sq.created_date),
                    "updated_date": str(sq.updated_date),
                    "mark_list": mark_list
                }
                sq_dict.append(sq_info_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": sq_dict,
            }, status=status.HTTP_200_OK)
        except ShortQuestion.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class SqMarkFilter(generics.ListCreateAPIView):
    """
        List and Create MC / Options
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.MCSerializer
    serializer_optionSerializer = serializers.OptionSerializer
    queryset = models.MC.objects.all().order_by('-id')
    queryset_theme = models.Theme.objects.all().order_by('-id')
    queryset_topic = models.McOptions.objects.all().order_by('-id')

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

    def get_topic_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_topic.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_theme_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_theme.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Theme Topic details
            :param request: Theme details
            :param kwargs: NA
            :return: Theme details
        """
        page_size = request.data.get('show_entries')
        try:
            import math
            if not page_size:
                page_size = 10
            paginator = CustomPagination()
            paginator.page_size = page_size

            sq_dict = []
            filters = {
                'topic_id': 'topic_id',
                'theme_id': 'theme_id',
            }
            selected_filters = {k: v for k, v in request.data.items() if v}
            sq_info = ShortQuestion.objects.all().order_by('id')
            for key, value in selected_filters.items():
                sq_info = sq_info.filter(**{filters[key]: value})

            # seq = 1
            # for sq_val in sq_info:
            #     sq_val.sq_sequence = seq
            #     sq_val.save()
            #     seq = seq + 1
            current_user = request.user.id
            for sq in sq_info.iterator():
                test_details = TestDetails.objects.filter(sq_id=sq.id, is_sq=True)
                no_of_respondents = len(test_details)
                total_mark = 0
                obtained_total_mark = 0
                for total in test_details:
                    total_mark = total_mark + total.total_mark
                    obtained_total_mark = obtained_total_mark + total.obtained_total_mark

                correct_percentage = 0
                incorrect_percentage = 0
                if obtained_total_mark > 0 and total_mark > 0:
                    correct_percentage = (obtained_total_mark / total_mark) * 100
                    incorrect_percentage = 100 - correct_percentage
                elif total_mark <= 0:
                    correct_percentage = 0
                    incorrect_percentage = 0
                elif obtained_total_mark <= 0:
                    correct_percentage = 0
                    incorrect_percentage = 100

                bookmark = False
                bookmark_data = SQBookmarks.objects.filter(sq_id=sq.id, partner_id=current_user)
                if bookmark_data:
                    bookmark = True
                mark_list = []
                sq_mark = ShortQuestionMarkPoints.objects.filter(sq_id=sq.id)

                mark_list = list(sq_mark.values(
                    "id",
                    "sq_id__id",
                    "sq_english_mark_points",
                    "sq_chinese_mark_points",
                    "sq_english_mark",
                    "sq_chinese_mark",
                    "created_date",
                    "updated_date"
                ))
                for option in mark_list:
                    option['created_date'] = str(option['created_date'])
                    option['updated_date'] = str(option['updated_date'])


                sq_info_dict = {
                    "id": sq.id,
                    "sq_sequence": sq.sq_sequence,
                    "sequence": sq.topic_id.sequence if sq.topic_id else False,
                    "theme_sequence": sq.theme_id.sequence if sq.theme_id else False,
                    "theme_id": sq.theme_id.id if sq.theme_id else False,
                    "english_tag": sq.theme_id.english_tag if sq.theme_id else False,
                    "chinese_tag": sq.theme_id.chinese_tag if sq.theme_id else False,
                    "topic_id": sq.topic_id.id if sq.topic_id else False,
                    "is_bookmarked": bookmark,
                    "topic_english_name": sq.topic_id.topic_english_name if sq.topic_id else False,
                    "topic_chinese_name": sq.topic_id.topic_chinese_name if sq.topic_id else False,
                    "theme_english_name": sq.theme_id.theme_english_name if sq.theme_id else False,
                    "theme_chinese_name": sq.theme_id.theme_chinese_name if sq.theme_id else False,
                    "learning_focus_id": sq.learning_focus_id.id if sq.learning_focus_id else False,
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
                    "total_mark": total_mark,
                    "obtained_total_mark": obtained_total_mark,
                    "no_of_respondents": no_of_respondents,
                    "correct_percentage": correct_percentage,
                    "incorrect_percentage": incorrect_percentage,
                    "created_date": str(sq.created_date),
                    "updated_date": str(sq.updated_date),
                    "mark_list": mark_list
                }
                sq_dict.append(sq_info_dict)
            result_page = paginator.paginate_queryset(sq_dict, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(sq_dict) > 0:
                paginator_data['total_pages'] = math.ceil(len(sq_dict) / page_size)
            else:
                return Response({"success": True, "message": "No data", "data": {}},
                                status=status.HTTP_200_OK)
            return Response({
                "success": True,
                "message": "Success",
                "data": paginator_data,
            }, status=status.HTTP_200_OK)
        except ShortQuestion.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


# class SqMarkFilter(generics.ListCreateAPIView):
#     """
#         List and Create MC / Options
#     """
#
#     permission_classes = (IsAuthenticated,)
#     serializer_class = serializers.MCSerializer
#     serializer_optionSerializer = serializers.OptionSerializer
#     queryset = models.MC.objects.all().order_by('-id')
#     queryset_theme = models.Theme.objects.all().order_by('-id')
#     queryset_topic = models.McOptions.objects.all().order_by('-id')
#
#     def get_object(self, pk):
#         """
#         Fetch corresponding snippets object
#         :param pk: snippets id
#         :return: snippets object
#         """
#         try:
#             return self.queryset.get(pk=pk)
#         except ObjectDoesNotExist:
#             raise Http404
#
#     def get_topic_object(self, pk):
#         """
#         Fetch corresponding snippets object
#         :param pk: snippets id
#         :return: snippets object
#         """
#         try:
#             return self.queryset_topic.get(pk=pk)
#         except ObjectDoesNotExist:
#             raise Http404
#
#     def get_theme_object(self, pk):
#         """
#         Fetch corresponding snippets object
#         :param pk: snippets id
#         :return: snippets object
#         """
#         try:
#             return self.queryset_theme.get(pk=pk)
#         except ObjectDoesNotExist:
#             raise Http404
#
#     def get_user(self):
#         return self.request.user
#
#     def post(self, request, *args, **kwargs):
#         """
#             create Theme Topic details
#             :param request: Theme details
#             :param kwargs: NA
#             :return: Theme details
#         """
#         theme_id = request.data.get('theme_id')
#         topic_id = request.data.get('topic_id')
#
#         try:
#             import math
#             page_size = 10
#             paginator = CustomPagination()
#             paginator.page_size = page_size
#
#             sq_dict = []
#             sq_info = ShortQuestion.objects.all().order_by('id')
#
#             # seq = 1
#             # for sq_val in sq_info:
#             #     sq_val.sq_sequence = seq
#             #     sq_val.save()
#             #     seq = seq + 1
#
#             if theme_id and topic_id:
#                 sq_info = ShortQuestion.objects.filter(theme_id=theme_id, topic_id=topic_id)
#             elif theme_id:
#                 sq_info = ShortQuestion.objects.filter(theme_id=theme_id)
#             elif topic_id:
#                 sq_info = ShortQuestion.objects.filter(topic_id=topic_id)
#             else:
#                 sq_info = ShortQuestion.objects.all().order_by('id')
#             current_user = request.user.id
#             for sq in sq_info.iterator():
#                 test_details = TestDetails.objects.filter(sq_id=sq.id, is_sq=True)
#                 no_of_respondents = len(test_details)
#                 total_mark = 0
#                 obtained_total_mark = 0
#                 for total in test_details:
#                     total_mark = total_mark + total.total_mark
#                     obtained_total_mark = obtained_total_mark + total.obtained_total_mark
#
#                 correct_percentage = 0
#                 incorrect_percentage = 0
#                 if obtained_total_mark > 0 and total_mark > 0:
#                     correct_percentage = (obtained_total_mark / total_mark) * 100
#                     incorrect_percentage = 100 - correct_percentage
#                 elif total_mark <= 0:
#                     correct_percentage = 0
#                     incorrect_percentage = 0
#                 elif obtained_total_mark <= 0:
#                     correct_percentage = 0
#                     incorrect_percentage = 100
#
#                 bookmark = False
#                 bookmark_data = SQBookmarks.objects.filter(sq_id=sq.id, partner_id=current_user)
#                 if bookmark_data:
#                     bookmark = True
#                 mark_list = []
#                 sq_mark = ShortQuestionMarkPoints.objects.filter(sq_id=sq.id)
#                 for mark in sq_mark:
#                     mark_dict = {
#                         "id": mark.id,
#                         "sq_id": mark.sq_id.id if mark.sq_id else False,
#                         "sq_english_mark_points": mark.sq_english_mark_points,
#                         "sq_chinese_mark_points": mark.sq_chinese_mark_points,
#                         "sq_english_mark": mark.sq_english_mark,
#                         "sq_chinese_mark": mark.sq_chinese_mark,
#                         "created_date": str(mark.created_date),
#                         "updated_date": str(mark.updated_date)
#                     }
#                     mark_list.append(mark_dict)
#                 sq_info_dict = {
#                     "id": sq.id,
#                     "sq_sequence": sq.sq_sequence,
#                     "sequence": sq.topic_id.sequence if sq.topic_id else False,
#                     "theme_sequence": sq.theme_id.sequence if sq.theme_id else False,
#                     "theme_id": sq.theme_id.id if sq.theme_id else False,
#                     "english_tag": sq.theme_id.english_tag if sq.theme_id else False,
#                     "chinese_tag": sq.theme_id.chinese_tag if sq.theme_id else False,
#                     "topic_id": sq.topic_id.id if sq.topic_id else False,
#                     "is_bookmarked": bookmark,
#                     "topic_english_name": sq.topic_id.topic_english_name if sq.topic_id else False,
#                     "topic_chinese_name": sq.topic_id.topic_chinese_name if sq.topic_id else False,
#                     "theme_english_name": sq.theme_id.theme_english_name if sq.theme_id else False,
#                     "theme_chinese_name": sq.theme_id.theme_chinese_name if sq.theme_id else False,
#                     "learning_focus_id": sq.learning_focus_id.id if sq.learning_focus_id else False,
#                     "sq_english_source_ref": sq.sq_english_source_ref,
#                     "sq_chinese_source_ref": sq.sq_chinese_source_ref,
#                     "sq_english_source_details": sq.sq_english_source_details,
#                     "sq_chinese_source_details": sq.sq_chinese_source_details,
#                     "sq_english_question": sq.sq_english_question,
#                     "sq_chinese_question": sq.sq_chinese_question,
#                     "sq_english_question_bookmark": sq.sq_english_question_bookmark,
#                     "sq_chinese_question_bookmark": sq.sq_chinese_question_bookmark,
#                     "sq_english_suggested_answer": sq.sq_english_suggested_answer,
#                     "sq_chinese_suggested_answer": sq.sq_chinese_suggested_answer,
#                     "sq_total_mark": sq.sq_total_mark,
#                     "total_mark": total_mark,
#                     "obtained_total_mark": obtained_total_mark,
#                     "no_of_respondents": no_of_respondents,
#                     "correct_percentage": correct_percentage,
#                     "incorrect_percentage": incorrect_percentage,
#                     "created_date": str(sq.created_date),
#                     "updated_date": str(sq.updated_date),
#                     "mark_list": mark_list
#                 }
#                 sq_dict.append(sq_info_dict)
#             result_page = paginator.paginate_queryset(sq_dict, request)
#             paginator_data = paginator.get_paginated_response(result_page).data
#             if len(sq_dict) > 0:
#                 paginator_data['total_pages'] = math.ceil(len(sq_dict) / page_size)
#             else:
#                 return Response({"success": True, "message": "No data", "data": {}},
#                                 status=status.HTTP_200_OK)
#             return Response({
#                 "success": True,
#                 "message": "Success",
#                 "data": paginator_data,
#             }, status=status.HTTP_200_OK)
#         except ShortQuestion.DoesNotExist:
#             return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class SqMarkForm(generics.ListCreateAPIView):
    """
        List and Create SQ / Mark
    """

    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.SQSerializer
    serializer_optionSerializer = serializers.MCSerializer
    queryset = models.ShortQuestion.objects.all().order_by('-id')
    queryset_theme = models.ShortQuestion.objects.all().order_by('-id')
    queryset_topic = models.ShortQuestionMarkPoints.objects.all().order_by('-id')

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

    def get_topic_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_topic.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_theme_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset_theme.get(pk=pk)
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

        marks = []
        sq = []
        mark_fail = False
        mark_serializer = []
        sq_id = request.data.get('id')
        try:
            sq_dict = []
            sq_info = ShortQuestion.objects.filter(id=sq_id)
            current_user = request.user.id
            for sq in sq_info.iterator():
                bookmark = False
                bookmark_data = SQBookmarks.objects.filter(sq_id=sq.id, partner_id=current_user)
                if bookmark_data:
                    bookmark = True
                mark_list = []
                sq_options = ShortQuestionMarkPoints.objects.filter(sq_id=sq.id)
                for mark in sq_options:
                    mark_dict = {
                        "id": mark.id,
                        "sq_id": mark.sq_id.id,
                        "sq_english_mark_points": mark.sq_english_mark_points,
                        "sq_chinese_mark_points": mark.sq_chinese_mark_points,
                        "sq_english_mark": mark.sq_english_mark,
                        "sq_chinese_mark": mark.sq_chinese_mark,
                        "created_date": str(mark.created_date),
                        "updated_date": str(mark.updated_date)
                    }
                    mark_list.append(mark_dict)
                sq_info_dict = {
                    "id": sq.id,
                    "theme_id": sq.theme_id.id,
                    "topic_id": sq.topic_id.id,
                    "learning_focus_id": sq.learning_focus_id.id,
                    "is_bookmarked": bookmark,
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
                    "created_date": str(sq.created_date),
                    "updated_date": str(sq.updated_date),
                    "mark_list": mark_list
                }
                sq_dict.append(sq_info_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": sq_dict,
            }, status=status.HTTP_200_OK)
        except ShortQuestion.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class ThemeUsageView(generics.ListCreateAPIView):
    """
        List and Create SQ / Mark
    """

    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ThemeUsage
    queryset = models.ThemeUsage.objects.all().order_by('-id')

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
        if filter_method:
            if filter_method == 'all':
                today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
                today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
                n = 1
                form_data = []

                final_end1 = today_min
                final_start1 = today_max
                dataset_label1 = []
                for x in range(23):
                    final_end1 = final_end1 + timedelta(hours=n)
                    dataset_label1.append(final_end1.strftime("%I:%M %p"))

                themes = models.Theme.objects.all().order_by('-id')
                for theme in themes:
                    final_end = today_min
                    final_start = today_max
                    dataset_value = []
                    dataset_label = []
                    for x in range(23):
                        final_end = final_end + timedelta(hours=n)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                        theme_id=theme.id).count()
                        final_start = final_end
                        dataset_value.append(informations)
                        dataset_label.append(final_end.strftime("%I:%M %p"))
                    topics_val = []
                    topics = models.Topic.objects.filter(theme_id=theme.id).order_by('-id')
                    if topics:
                        for i in topics:
                            topic_dict = {
                                "topic_id": i.id,
                                "topic_english_name": i.topic_english_name,
                                "topic_chinese_name": i.topic_chinese_name,
                            }
                            topics_val.append(topic_dict)
                    form_dict = {
                        'theme': theme.id,
                        'theme_english_tag': theme.english_tag if theme.english_tag else "",
                        'theme_chinese_tag': theme.chinese_tag if theme.chinese_tag else "",
                        'theme_english_name': theme.theme_english_name,
                        'theme_chinese_name': theme.theme_chinese_name,
                        'topics': topics_val,
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

                final_start1 = week_min
                final_end1 = week_min
                dataset_label1 = []
                for x in range(7):
                    final_end1 = final_end1 + timedelta(hours=24)
                    dataset_label1.append(final_start1.strftime("%a"))
                    final_start1 = final_end1

                Themes = models.Theme.objects.all().order_by('-id')
                for theme in Themes:
                    final_start = week_min
                    final_end = week_min
                    dataset_value = []
                    dataset_label = []
                    for x in range(7):
                        final_end = final_end + timedelta(hours=24)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                        theme_id=theme.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%a"))
                        final_start = final_end
                    topics_val = []
                    topics = models.Topic.objects.filter(theme_id=theme.id).order_by('-id')
                    if topics:
                        for i in topics:
                            topic_dict = {
                                "topic_id": i.id,
                                "topic_english_name": i.topic_english_name,
                                "topic_chinese_name": i.topic_chinese_name,
                            }
                            topics_val.append(topic_dict)
                    form_dict = {
                        'theme': theme.id,
                        'theme_english_tag': theme.english_tag if theme.english_tag else "",
                        'theme_chinese_tag': theme.chinese_tag if theme.chinese_tag else "",
                        'theme_english_name': theme.theme_english_name,
                        'theme_chinese_name': theme.theme_chinese_name,
                        'topics': topics_val,
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

                final_start1 = first_date
                final_end1 = first_date
                dataset_label1 = []
                for x in range(delta.days):
                    final_end1 = final_end1 + timedelta(days=1)
                    dataset_label1.append(final_start1.strftime("%Y:%m %d"))
                    final_start1 = final_end1

                themes = models.Theme.objects.all().order_by('-id')
                for theme in themes:
                    final_start = first_date
                    final_end = first_date
                    dataset_value = []
                    dataset_label = []
                    for x in range(delta.days):
                        final_end = final_end + timedelta(days=1)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                        theme_id=theme.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%Y:%m %d"))
                        final_start = final_end
                    topics_val = []
                    topics = models.Topic.objects.filter(theme_id=theme.id).order_by('-id')
                    if topics:
                        for i in topics:
                            topic_dict = {
                                "topic_id": i.id,
                                "topic_english_name": i.topic_english_name,
                                "topic_chinese_name": i.topic_chinese_name,
                            }
                            topics_val.append(topic_dict)
                    form_dict = {
                        'theme': theme.id,
                        'theme_english_tag': theme.english_tag if theme.english_tag else "",
                        'theme_chinese_tag': theme.chinese_tag if theme.chinese_tag else "",
                        'theme_english_name': theme.theme_english_name,
                        'theme_chinese_name': theme.theme_chinese_name,
                        'topics': topics_val,
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

                final_start1 = first_date
                final_end1 = first_date
                dataset_label1 = []
                for x in range(12):
                    final_end1 = final_end1 + relativedelta(months=1)
                    dataset_label1.append(final_start1.strftime("%b"))
                    final_start1 = final_end1

                themes = models.Theme.objects.all().order_by('-id')
                for theme in themes:
                    final_start = first_date
                    final_end = first_date
                    dataset_value = []
                    dataset_label = []
                    for x in range(12):
                        final_end = final_end + relativedelta(months=1)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                        theme_id=theme.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%b"))
                        final_start = final_end
                    topics_val = []
                    topics = models.Topic.objects.filter(theme_id=theme.id).order_by('-id')
                    if topics:
                        for i in topics:
                            topic_dict = {
                                "topic_id": i.id,
                                "topic_english_name": i.topic_english_name,
                                "topic_chinese_name": i.topic_chinese_name,
                            }
                            topics_val.append(topic_dict)
                    form_dict = {
                        'theme': theme.id,
                        'theme_english_tag': theme.english_tag if theme.english_tag else "",
                        'theme_chinese_tag': theme.chinese_tag if theme.chinese_tag else "",
                        'theme_english_name': theme.theme_english_name,
                        'theme_chinese_name': theme.theme_chinese_name,
                        'topics': topics_val,
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
        else:
            return Response({
                "success": False,
                "message": "Not Found",
            }, status=status.HTTP_400_BAD_REQUEST)


class ThemeUsageViewfilter(generics.ListCreateAPIView):
    """
        List and Create SQ / Mark
    """

    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ThemeUsage
    queryset = models.ThemeUsage.objects.all().order_by('-id')

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
        theme_id = request.data.get('theme_id')
        if filter_method and theme_id:
            if filter_method == 'all':
                today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
                today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
                n = 1
                form_data = []
                themes = models.Theme.objects.filter(id=theme_id)
                for theme in themes:
                    final_end = today_min
                    final_start = today_max
                    dataset_value = []
                    dataset_label = []
                    for x in range(23):
                        final_end = final_end + timedelta(hours=n)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end], theme_id= theme.id).count()
                        final_start = final_end
                        dataset_value.append(informations)
                        dataset_label.append(final_end.strftime("%I:%M %p"))
                    topics_val = []
                    topics = models.Topic.objects.filter(theme_id=theme.id).order_by('-id')
                    if topics:
                        for i in topics:
                            topic_dict = {
                                "topic_id": i.id,
                                "topic_english_name": i.topic_english_name,
                                "topic_chinese_name": i.topic_chinese_name,
                            }
                            topics_val.append(topic_dict)
                    form_dict = {
                        'theme': theme.id,
                        'theme_english_tag': theme.english_tag if theme.english_tag else "",
                        'theme_chinese_tag': theme.chinese_tag if theme.chinese_tag else "",
                        'theme_english_name': theme.theme_english_name,
                        'theme_chinese_name': theme.theme_chinese_name,
                        'topics': topics_val,
                        'label': dataset_label,
                        'data': dataset_value

                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
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
                Themes = models.Theme.objects.filter(id=theme_id)
                for theme in Themes:
                    final_start = week_min
                    final_end = week_min
                    dataset_value = []
                    dataset_label = []
                    for x in range(7):
                        final_end = final_end + timedelta(hours=24)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                      theme_id=theme.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%a"))
                        final_start = final_end
                    topics_val = []
                    topics = models.Topic.objects.filter(theme_id=theme.id).order_by('-id')
                    if topics:
                        for i in topics:
                            topic_dict = {
                                "topic_id": i.id,
                                "topic_english_name": i.topic_english_name,
                                "topic_chinese_name": i.topic_chinese_name,
                            }
                            topics_val.append(topic_dict)
                    form_dict = {
                        'theme': theme.id,
                        'theme_english_tag': theme.english_tag if theme.english_tag else "",
                        'theme_chinese_tag': theme.chinese_tag if theme.chinese_tag else "",
                        'theme_english_name': theme.theme_english_name,
                        'theme_chinese_name': theme.theme_chinese_name,
                        'topics': topics_val,
                        'label': dataset_label,
                        'data': dataset_value
                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
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
                themes = models.Theme.objects.filter(id=theme_id)
                for theme in themes:
                    final_start = first_date
                    final_end = first_date
                    dataset_value = []
                    dataset_label = []
                    for x in range(delta.days):
                        final_end = final_end + timedelta(days=1)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                      theme_id=theme.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%Y:%m %d"))
                        final_start = final_end
                    topics_val = []
                    topics = models.Topic.objects.filter(theme_id=theme.id).order_by('-id')
                    if topics:
                        for i in topics:
                            topic_dict = {
                                "topic_id": i.id,
                                "topic_english_name": i.topic_english_name,
                                "topic_chinese_name": i.topic_chinese_name,
                            }
                            topics_val.append(topic_dict)
                    form_dict = {
                        'theme': theme.id,
                        'theme_english_tag': theme.english_tag if theme.english_tag else "",
                        'theme_chinese_tag': theme.chinese_tag if theme.chinese_tag else "",
                        'theme_english_name': theme.theme_english_name,
                        'theme_chinese_name': theme.theme_chinese_name,
                        'topics': topics_val,
                        'label': dataset_label,
                        'data': dataset_value

                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
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
                themes = models.Theme.objects.filter(id=theme_id)
                for theme in themes:
                    final_start = first_date
                    final_end = first_date
                    dataset_value = []
                    dataset_label = []
                    for x in range(12):
                        final_end = final_end + relativedelta(months=1)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                      theme_id=theme.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%b"))
                        final_start = final_end
                    topics_val = []
                    topics = models.Topic.objects.filter(theme_id=theme.id).order_by('-id')
                    if topics:
                        for i in topics:
                            topic_dict = {
                                "topic_id": i.id,
                                "topic_english_name": i.topic_english_name,
                                "topic_chinese_name": i.topic_chinese_name,
                            }
                            topics_val.append(topic_dict)
                    form_dict = {
                        'theme': theme.id,
                        'theme_english_tag': theme.english_tag if theme.english_tag else "",
                        'theme_chinese_tag': theme.chinese_tag if theme.chinese_tag else "",
                        'theme_english_name': theme.theme_english_name,
                        'theme_chinese_name': theme.theme_chinese_name,
                        'topics': topics_val,
                        'label': dataset_label,
                        'data': dataset_value

                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "success": False,
                "message": "Not Found",
            }, status=status.HTTP_400_BAD_REQUEST)


class TopicUsageView(generics.ListCreateAPIView):
    """
        List and Create SQ / Mark
    """

    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ThemeUsage
    queryset = models.ThemeUsage.objects.all().order_by('-id')

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
        if filter_method:
            if filter_method == 'all':
                today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
                today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
                n = 1
                form_data = []
                topics = models.Topic.objects.all().order_by('id')
                for topic in topics:
                    final_end = today_min
                    final_start = today_max
                    dataset_value = []
                    dataset_label = []
                    for x in range(23):
                        final_end = final_end + timedelta(hours=n)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end], topic_id= topic.id).count()
                        final_start = final_end
                        dataset_value.append(informations)
                        dataset_label.append(final_end.strftime("%I:%M %p"))
                    form_dict = {
                        'topic': topic.id,
                        'topic_sequence': topic.sequence,
                        'topic_english_name': topic.topic_english_name,
                        'topic_chinese_name': topic.topic_chinese_name,
                        'label': dataset_label,
                        'data': dataset_value
                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
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
                topics = models.Topic.objects.all().order_by('id')
                for topic in topics:
                    final_start = week_min
                    final_end = week_min
                    dataset_value = []
                    dataset_label = []
                    for x in range(7):
                        final_end = final_end + timedelta(hours=24)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                      topic_id=topic.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%a"))
                        final_start = final_end
                    form_dict = {
                        'topic': topic.id,
                        'topic_sequence': topic.sequence,
                        'topic_english_name': topic.topic_english_name,
                        'topic_chinese_name': topic.topic_chinese_name,
                        'label': dataset_label,
                        'data': dataset_value
                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
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
                topics = models.Topic.objects.all().order_by('id')
                for topic in topics:
                    final_start = first_date
                    final_end = first_date
                    dataset_value = []
                    dataset_label = []
                    for x in range(delta.days):
                        final_end = final_end + timedelta(days=1)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                      topic_id=topic.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%Y:%m %d"))
                        final_start = final_end
                    form_dict = {
                        'topic': topic.id,
                        'topic_sequence': topic.sequence,
                        'topic_english_name': topic.topic_english_name,
                        'topic_chinese_name': topic.topic_chinese_name,
                        'label': dataset_label,
                        'data': dataset_value
                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
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
                topics = models.Topic.objects.all().order_by('id')
                for topic in topics:
                    final_start = first_date
                    final_end = first_date
                    dataset_value = []
                    dataset_label = []
                    for x in range(12):
                        final_end = final_end + relativedelta(months=1)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                      topic_id=topic.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%b"))
                        final_start = final_end
                    form_dict = {
                        'topic': topic.id,
                        'topic_sequence': topic.sequence,
                        'topic_english_name': topic.topic_english_name,
                        'topic_chinese_name': topic.topic_chinese_name,
                        'label': dataset_label,
                        'data': dataset_value
                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "success": False,
                "message": "Not Found",
            }, status=status.HTTP_400_BAD_REQUEST)


class TopicUsageViewfilter(generics.ListCreateAPIView):
    """
        List and Create SQ / Mark
    """

    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ThemeUsage
    queryset = models.ThemeUsage.objects.all().order_by('-id')

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
        theme_id = request.data.get('theme_id')
        if filter_method and theme_id:
            if filter_method == 'all':
                today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
                today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
                n = 1
                form_data = []
                topics = models.Topic.objects.filter(theme_id=theme_id)
                final_end1 = today_min
                final_start1 = today_max
                dataset_label1 = []
                for x in range(23):
                    final_end1 = final_end1 + timedelta(hours=n)
                    dataset_label1.append(final_end1.strftime("%I:%M %p"))
                for topic in topics:
                    final_end = today_min
                    final_start = today_max
                    dataset_value = []
                    dataset_label = []
                    for x in range(23):
                        final_end = final_end + timedelta(hours=n)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end], topic_id=topic.id).count()
                        final_start = final_end
                        dataset_value.append(informations)
                        dataset_label.append(final_end.strftime("%I:%M %p"))
                    form_dict = {
                        'topic': topic.id,
                        'topic_sequence': topic.sequence,
                        'topic_english_name': topic.topic_english_name,
                        'topic_chinese_name': topic.topic_chinese_name,
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

                final_start1 = week_min
                final_end1 = week_min
                dataset_label1 = []
                for x in range(7):
                    final_end1 = final_end1 + timedelta(hours=24)
                    dataset_label1.append(final_start1.strftime("%a"))
                    final_start1 = final_end1

                topics = models.Topic.objects.filter(theme_id=theme_id)
                for topic in topics:
                    final_start = week_min
                    final_end = week_min
                    dataset_value = []
                    dataset_label = []
                    for x in range(7):
                        final_end = final_end + timedelta(hours=24)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                      topic_id=topic.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%a"))
                        final_start = final_end
                    form_dict = {
                        'topic': topic.id,
                        'topic_sequence': topic.sequence,
                        'topic_english_name': topic.topic_english_name,
                        'topic_chinese_name': topic.topic_chinese_name,
                        'label': dataset_label,
                        'data': dataset_value
                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                    "label":dataset_label1
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
                topics = models.Topic.objects.filter(theme_id=theme_id)

                final_start1 = first_date
                final_end1 = first_date
                dataset_label1 = []
                for x in range(delta.days):
                    final_end1 = final_end1 + timedelta(days=1)
                    dataset_label1.append(final_start1.strftime("%Y:%m %d"))
                    final_start1 = final_end1
                for topic in topics:
                    final_start = first_date
                    final_end = first_date
                    dataset_value = []
                    dataset_label = []
                    for x in range(delta.days):
                        final_end = final_end + timedelta(days=1)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                      topic_id=topic.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%Y:%m %d"))
                        final_start = final_end
                    form_dict = {
                        'topic': topic.id,
                        'topic_sequence': topic.sequence,
                        'topic_english_name': topic.topic_english_name,
                        'topic_chinese_name': topic.topic_chinese_name,
                        'label': dataset_label,
                        'data': dataset_value
                    }
                    form_data.append(form_dict)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": form_data,
                    "label":dataset_label1
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

                final_start1 = first_date
                final_end1 = first_date
                dataset_label1 = []
                for x in range(12):
                    final_end1 = final_end1 + relativedelta(months=1)
                    dataset_label1.append(final_start1.strftime("%b"))
                    final_start1 = final_end1
                topics = models.Topic.objects.filter(theme_id=theme_id)
                for topic in topics:
                    final_start = first_date
                    final_end = first_date
                    dataset_value = []
                    dataset_label = []
                    for x in range(12):
                        final_end = final_end + relativedelta(months=1)
                        informations = models.ThemeUsage.objects.filter(created_date__range=[final_start, final_end],
                                                                      topic_id=topic.id).count()
                        dataset_value.append(informations)
                        dataset_label.append(final_start.strftime("%b"))
                        final_start = final_end
                    form_dict = {
                        'topic': topic.id,
                        'topic_sequence': topic.sequence,
                        'topic_english_name': topic.topic_english_name,
                        'topic_chinese_name': topic.topic_chinese_name,
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
        else:
            return Response({
                "success": False,
                "message": "Not Found",
            }, status=status.HTTP_400_BAD_REQUEST)


# Test
class ThemeTestList(generics.ListCreateAPIView):
    serializer_class = serializers.ThemeSerializer
    queryset = models.Theme.objects.all().order_by('-id')

    """
        List and Test MC/SQ
    """
    permission_classes = (IsAuthenticated,)
    queryset = models.Theme.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
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
            themes = Theme.objects.all().order_by('-id')
            current_user = request.user.id
            for theme in themes.iterator():
                topics_list = []
                topics = models.Topic.objects.filter(theme_id=theme.id)
                for topic in topics:
                    learning_focus_list = []
                    mc_list = []
                    sq_list = []
                    learning_focus = models.Learningfocus.objects.filter(topic_id=topic.id)
                    for lf in learning_focus:
                        mcq = models.MC.objects.filter(theme_id=theme.id, topic_id=topic.id, learning_focus_id=lf.id)
                        short_questions = models.ShortQuestion.objects.filter(theme_id=theme.id, topic_id=topic.id,
                                                                              learning_focus_id=lf.id)
                        for mc in mcq:
                            mc_options_list = []
                            mc_options = models.McOptions.objects.filter(mc_id=mc.id)
                            bookmark = False
                            bookmark_data = MCBookmarks.objects.filter(mc_id=mc.id, partner_id=current_user)
                            if bookmark_data:
                                bookmark = True
                            for option in mc_options:
                                mc_option_dict = {
                                    "id": option.id,
                                    "mc_id": option.mc_id.id,
                                    "mc_english_options": option.mc_english_options,
                                    "mc_chinese_options": option.mc_chinese_options,
                                    "mc_answer_index": option.mc_answer_index,
                                    "created_date": mc.created_date,
                                    "updated_date": mc.updated_date
                                }
                                mc_options_list.append(mc_option_dict)
                            mc_dict = {
                                "id": mc.id,
                                "is_bookmarked": bookmark,
                                "theme_id": mc.theme_id.id,
                                "topic_id": mc.topic_id.id,
                                "learning_focus_id": mc.learning_focus_id.id,
                                "learning_focus_english_name": mc.learning_focus_id.english,
                                "learning_focus_chinese_name": mc.learning_focus_id.chinese,
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
                            bookmark = False
                            bookmark_data = SQBookmarks.objects.filter(sq_id=mc.id, partner_id=current_user)
                            if bookmark_data:
                                bookmark = True
                            for points in sq_mark_points:
                                sq_option_dict = {
                                    "id": points.id,
                                    "sq_id": points.sq_id.id,
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
                                "is_bookmarked": bookmark,
                                "theme_id": sq.theme_id.id,
                                "topic_id": sq.topic_id.id,
                                "learning_focus_id": sq.learning_focus_id.id,
                                "learning_focus_english_name": sq.learning_focus_id.english,
                                "learning_focus_chinese_name": sq.learning_focus_id.chinese,
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
                        for learn_foc in learning_focus:

                            learning_focus_dict = {
                                "id": learn_foc.id,
                                "topic_id": learn_foc.topic_id.id,
                                "english": learn_foc.english,
                                "chinese": learn_foc.chinese,
                                "created_date": learn_foc.created_date,
                                "updated_date": learn_foc.updated_date,
                            }
                            learning_focus_list.append(learning_focus_dict)
                    topics_dict = {
                        "id": topic.id,
                        "theme_id": topic.theme_id.id,
                        "topic_english_name": topic.topic_english_name,
                        "topic_chinese_name": topic.topic_chinese_name,
                        "created_date": topic.created_date,
                        "updated_date": topic.updated_date,
                        "learning_focus": learning_focus_list,
                        "mc": mc_list,
                        "sq": sq_list
                    }
                    topics_list.append(topics_dict)
                theme_dict = {
                    "id": theme.id,
                    "is_purchased": True,
                    "english_tag": theme.english_tag,
                    "chinese_tag": theme.chinese_tag,
                    "theme_english_name": theme.theme_english_name,
                    "theme_chinese_name": theme.theme_chinese_name,
                    "theme_image": urls + "/media/" + str(theme.theme_image) or False,
                    "theme_color": theme.theme_color,
                    "theme_number": theme.theme_number,
                    "created_date": str(theme.created_date),
                    "updated_date": str(theme.updated_date),
                    "topics": topics_list
                }
                themes_dict.append(theme_dict)
            dicts = {}
            return Response({
                "success": True,
                "message": "Success",
                "data": themes_dict,
            }, status=status.HTTP_200_OK)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


# Test MC and SQ
class ThemeTestMcSq(generics.ListCreateAPIView):
    serializer_class = serializers.ThemeSerializer
    queryset = models.Theme.objects.all().order_by('-id')

    """
        List and Test MC/SQ
    """
    permission_classes = (IsAuthenticated,)
    queryset = models.Theme.objects.all().order_by('-id')

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
            themes = Theme.objects.all().order_by('-id')
            current_user = request.user.id
            mc_list = []
            sq_list = []
            theme_id = request.data.get('theme_id')
            topic_id = request.data.get('topic_id')
            lf_id = request.data.get('lf_id')
            mcq = models.MC.objects.all().order_by('?')[:10]
            short_questions = models.ShortQuestion.objects.all().order_by('?')[:6]

            if theme_id and topic_id and lf_id:
                mcq = models.MC.objects.filter(theme_id=theme_id, topic_id=topic_id,
                                               learning_focus_id=lf_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(theme_id=theme_id,
                                                                      topic_id=topic_id,
                                                                      learning_focus_id=lf_id).order_by('?')[:6]
            elif theme_id and topic_id:
                mcq = models.MC.objects.filter(theme_id=theme_id, topic_id=topic_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(theme_id=theme_id,
                                                                      topic_id=topic_id).order_by('?')[:6]
            elif topic_id and lf_id:
                mcq = models.MC.objects.filter(learning_focus_id=lf_id, topic_id=topic_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(learning_focus_id=lf_id,
                                                                      topic_id=topic_id).order_by('?')[:6]
            elif theme_id and lf_id:
                mcq = models.MC.objects.filter(learning_focus_id=lf_id, theme_id=theme_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(learning_focus_id=lf_id,
                                                                      theme_id=theme_id).order_by('?')[:6]
            elif theme_id:
                mcq = models.MC.objects.filter(theme_id=theme_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(theme_id=theme_id).order_by('?')[:6]
            elif topic_id:
                mcq = models.MC.objects.filter(topic_id=topic_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(topic_id=topic_id).order_by('?')[:6]
            elif lf_id:
                mcq = models.MC.objects.filter(learning_focus_id=lf_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(learning_focus_id=lf_id).order_by('?')[:6]
            else:
                mcq = models.MC.objects.all().order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.all().order_by('?')[:6]

            for mc in mcq:
                mc_options_list = []
                mc_options = models.McOptions.objects.filter(mc_id=mc.id)
                bookmark = False
                bookmark_data = MCBookmarks.objects.filter(mc_id=mc.id, partner_id=current_user)
                if bookmark_data:
                    bookmark = True
                for option in mc_options:
                    mc_option_dict = {
                        "id": option.id,
                        "mc_id": option.mc_id.id,
                        "mc_english_options": option.mc_english_options,
                        "mc_chinese_options": option.mc_chinese_options,
                        "mc_answer_index": option.mc_answer_index,
                        "created_date": mc.created_date,
                        "updated_date": mc.updated_date
                    }
                    mc_options_list.append(mc_option_dict)
                mc_dict = {
                    "id": mc.id,
                    "is_bookmarked": bookmark,
                    "theme_id": mc.theme_id.id,
                    "topic_id": mc.topic_id.id,
                    "learning_focus_id": mc.learning_focus_id.id,
                    "learning_focus_english_name": mc.learning_focus_id.english,
                    "learning_focus_chinese_name": mc.learning_focus_id.chinese,
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
                bookmark = False
                bookmark_data = SQBookmarks.objects.filter(sq_id=mc.id, partner_id=current_user)
                if bookmark_data:
                    bookmark = True
                for points in sq_mark_points:
                    sq_option_dict = {
                        "id": points.id,
                        "sq_id": points.sq_id.id,
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
                    "is_bookmarked": bookmark,
                    "theme_id": sq.theme_id.id,
                    "topic_id": sq.topic_id.id,
                    "learning_focus_id": sq.learning_focus_id.id,
                    "learning_focus_english_name": sq.learning_focus_id.english,
                    "learning_focus_chinese_name": sq.learning_focus_id.chinese,
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
            topics_dict = {
                "mc_count": len(mc_list),
                "sq_count": len(sq_list),
                "mc": mc_list,
                "sq": sq_list
            }
            return Response({
                "success": True,
                "message": "Success",
                "data": topics_dict,
            }, status=status.HTTP_200_OK)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


# Test Theme Topic LF
class ThemeTestData(generics.ListCreateAPIView):
    serializer_class = serializers.ThemeSerializer
    queryset = models.Theme.objects.all().order_by('-id')

    """
        List and Test MC/SQ
    """
    permission_classes = (IsAuthenticated,)
    queryset = models.Theme.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
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
            themes = Theme.objects.all().order_by('-id')
            current_user = request.user.id
            for theme in themes.iterator():
                topics_list = []
                topics = models.Topic.objects.filter(theme_id=theme.id)
                for topic in topics:
                    learning_focus_list = []
                    mc_list = []
                    sq_list = []
                    learning_focus = models.Learningfocus.objects.filter(topic_id=topic.id)
                    for lf in learning_focus:
                        mcq = models.MC.objects.filter(theme_id=theme.id, topic_id=topic.id, learning_focus_id=lf.id)
                        short_questions = models.ShortQuestion.objects.filter(theme_id=theme.id, topic_id=topic.id,
                                                                              learning_focus_id=lf.id)
                        for learn_foc in learning_focus:

                            learning_focus_dict = {
                                "id": learn_foc.id if learn_foc.id else "",
                                "topic_id": learn_foc.topic_id.id if learn_foc.topic_id else "",
                                "english": learn_foc.english if learn_foc else "",
                                "chinese": learn_foc.chinese if learn_foc else "",
                                "created_date": str(learn_foc.created_date),
                                "updated_date": str(learn_foc.updated_date),
                            }
                            learning_focus_list.append(learning_focus_dict)
                    topics_dict = {
                        "id": topic.id if topic else "",
                        "theme_id": topic.theme_id.id if topic.theme_id else "",
                        "topic_english_name": topic.topic_english_name if topic else "",
                        "topic_chinese_name": topic.topic_chinese_name if topic else "",
                        "created_date": str(topic.created_date),
                        "updated_date": str(topic.updated_date),
                        "learning_focus": learning_focus_list,
                    }
                    topics_list.append(topics_dict)
                theme_dict = {
                    "id": theme.id if theme else "",
                    "is_purchased": True,
                    "english_tag": theme.english_tag if theme else "",
                    "chinese_tag": theme.chinese_tag if theme else "",
                    "theme_english_name": theme.theme_english_name if theme else "",
                    "theme_chinese_name": theme.theme_chinese_name if theme else "",
                    "theme_image": urls + "/media/" + str(theme.theme_image) or "",
                    "theme_color": theme.theme_color if theme else "",
                    "theme_number": theme.theme_number if theme else "",
                    "created_date": str(theme.created_date),
                    "updated_date": str(theme.updated_date),
                    "topics": topics_list
                }
                themes_dict.append(theme_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": themes_dict,
            }, status=status.HTTP_200_OK)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class MCBulkDeleteAPI(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.MCSerializer
    queryset = models.MC.objects.all().order_by('-id')

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


class SQBulkDeleteAPI(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.SQSerializer
    queryset = models.ShortQuestion.objects.all().order_by('-id')

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


class LearningCardBulkDeleteAPI(generics.ListCreateAPIView):
    """
        List and Create Theme
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.CardstitleSerializer
    queryset = models.Cardstitle.objects.all().order_by('-id')

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


class LearningCardUserAccessData(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.UserLearningCardDataSerializer
    queryset = models.UserLearningCardData.objects.all().order_by('-id')

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
        serializer = serializers.UserLearningCardDataSerializer(instance=snippets, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


# Public user test

class PublicUserThemeTestData(generics.ListCreateAPIView):
    serializer_class = serializers.ThemeSerializer
    queryset = models.Theme.objects.all().order_by('-id')

    """
        List and Test MC/SQ
    """
    # permission_classes = (IsAuthenticated,)
    queryset = models.Theme.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
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
            themes = Theme.objects.all().order_by('-id')
            current_user = request.user.id
            for theme in themes.iterator():
                topics_list = []
                topics = models.Topic.objects.filter(theme_id=theme.id)
                for topic in topics:
                    learning_focus_list = []
                    mc_list = []
                    sq_list = []
                    learning_focus = models.Learningfocus.objects.filter(topic_id=topic.id)
                    for lf in learning_focus:
                        mcq = models.MC.objects.filter(theme_id=theme.id, topic_id=topic.id, learning_focus_id=lf.id)
                        short_questions = models.ShortQuestion.objects.filter(theme_id=theme.id, topic_id=topic.id,
                                                                              learning_focus_id=lf.id)
                        for learn_foc in learning_focus:

                            learning_focus_dict = {
                                "id": learn_foc.id if learn_foc.id else "",
                                "topic_id": learn_foc.topic_id.id if learn_foc.topic_id else "",
                                "english": learn_foc.english if learn_foc else "",
                                "chinese": learn_foc.chinese if learn_foc else "",
                                "created_date": str(learn_foc.created_date),
                                "updated_date": str(learn_foc.updated_date),
                            }
                            learning_focus_list.append(learning_focus_dict)
                    topics_dict = {
                        "id": topic.id if topic else "",
                        "theme_id": topic.theme_id.id if topic.theme_id else "",
                        "topic_english_name": topic.topic_english_name if topic else "",
                        "topic_chinese_name": topic.topic_chinese_name if topic else "",
                        "created_date": str(topic.created_date),
                        "updated_date": str(topic.updated_date),
                        "learning_focus": learning_focus_list,
                    }
                    topics_list.append(topics_dict)
                theme_dict = {
                    "id": theme.id if theme else "",
                    "is_purchased": True,
                    "english_tag": theme.english_tag if theme else "",
                    "chinese_tag": theme.chinese_tag if theme else "",
                    "theme_english_name": theme.theme_english_name if theme else "",
                    "theme_chinese_name": theme.theme_chinese_name if theme else "",
                    "theme_image": urls + "/media/" + str(theme.theme_image) or "",
                    "theme_color": theme.theme_color if theme else "",
                    "theme_number": theme.theme_number if theme else "",
                    "created_date": str(theme.created_date),
                    "updated_date": str(theme.updated_date),
                    "topics": topics_list
                }
                themes_dict.append(theme_dict)
            return Response({
                "success": True,
                "message": "Success",
                "data": themes_dict,
            }, status=status.HTTP_200_OK)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


# Public User Test MC and SQ
class PublicThemeTestMcSq(generics.ListCreateAPIView):
    serializer_class = serializers.ThemeSerializer
    queryset = models.Theme.objects.all().order_by('-id')

    """
        List and Test MC/SQ
    """
    # permission_classes = (IsAuthenticated,)
    queryset = models.Theme.objects.all().order_by('-id')

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
            themes = Theme.objects.all().order_by('-id')
            current_user = request.user.id
            mc_list = []
            sq_list = []
            theme_id = request.data.get('theme_id')
            topic_id = request.data.get('topic_id')
            lf_id = request.data.get('lf_id')
            mcq = models.MC.objects.all().order_by('?')[:10]
            short_questions = models.ShortQuestion.objects.all().order_by('?')[:6]

            if theme_id and topic_id and lf_id:
                mcq = models.MC.objects.filter(theme_id=theme_id, topic_id=topic_id,
                                               learning_focus_id=lf_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(theme_id=theme_id,
                                                                      topic_id=topic_id,
                                                                      learning_focus_id=lf_id).order_by('?')[:6]
            elif theme_id and topic_id:
                mcq = models.MC.objects.filter(theme_id=theme_id, topic_id=topic_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(theme_id=theme_id,
                                                                      topic_id=topic_id).order_by('?')[:6]
            elif topic_id and lf_id:
                mcq = models.MC.objects.filter(learning_focus_id=lf_id, topic_id=topic_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(learning_focus_id=lf_id,
                                                                      topic_id=topic_id).order_by('?')[:6]
            elif theme_id and lf_id:
                mcq = models.MC.objects.filter(learning_focus_id=lf_id, theme_id=theme_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(learning_focus_id=lf_id,
                                                                      theme_id=theme_id).order_by('?')[:6]
            elif theme_id:
                mcq = models.MC.objects.filter(theme_id=theme_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(theme_id=theme_id).order_by('?')[:6]
            elif topic_id:
                mcq = models.MC.objects.filter(topic_id=topic_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(topic_id=topic_id).order_by('?')[:6]
            elif lf_id:
                mcq = models.MC.objects.filter(learning_focus_id=lf_id).order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.filter(learning_focus_id=lf_id).order_by('?')[:6]
            else:
                mcq = models.MC.objects.all().order_by('?')[:10]
                short_questions = models.ShortQuestion.objects.all().order_by('?')[:6]

            for mc in mcq:
                mc_options_list = []
                mc_options = models.McOptions.objects.filter(mc_id=mc.id)
                bookmark = False
                bookmark_data = MCBookmarks.objects.filter(mc_id=mc.id, partner_id=current_user)
                if bookmark_data:
                    bookmark = True
                for option in mc_options:
                    mc_option_dict = {
                        "id": option.id,
                        "mc_id": option.mc_id.id,
                        "mc_english_options": option.mc_english_options,
                        "mc_chinese_options": option.mc_chinese_options,
                        "mc_answer_index": option.mc_answer_index,
                        "created_date": mc.created_date,
                        "updated_date": mc.updated_date
                    }
                    mc_options_list.append(mc_option_dict)
                mc_dict = {
                    "id": mc.id,
                    "is_bookmarked": bookmark,
                    "theme_id": mc.theme_id.id,
                    "topic_id": mc.topic_id.id,
                    "learning_focus_id": mc.learning_focus_id.id,
                    "learning_focus_english_name": mc.learning_focus_id.english,
                    "learning_focus_chinese_name": mc.learning_focus_id.chinese,
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
                bookmark = False
                bookmark_data = SQBookmarks.objects.filter(sq_id=mc.id, partner_id=current_user)
                if bookmark_data:
                    bookmark = True
                for points in sq_mark_points:
                    sq_option_dict = {
                        "id": points.id,
                        "sq_id": points.sq_id.id,
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
                    "is_bookmarked": bookmark,
                    "theme_id": sq.theme_id.id,
                    "topic_id": sq.topic_id.id,
                    "learning_focus_id": sq.learning_focus_id.id,
                    "learning_focus_english_name": sq.learning_focus_id.english,
                    "learning_focus_chinese_name": sq.learning_focus_id.chinese,
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
            topics_dict = {
                "mc_count": len(mc_list),
                "sq_count": len(sq_list),
                "mc": mc_list,
                "sq": sq_list
            }
            return Response({
                "success": True,
                "message": "Success",
                "data": topics_dict,
            }, status=status.HTTP_200_OK)
        except Theme.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
