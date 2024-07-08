from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from bookmarks import serializers, models
from theme import models as theme_models
from rest_framework.decorators import api_view
from accounts.models import user
from knox.models import AuthToken


class MCBookmarksAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.McBookmarksSerializers
    queryset = models.MCBookmarks.objects.all().order_by('-id')

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
            create MC Bookmark details
            :param request: Bookmark details
            :param kwargs: NA
            :return: Bookmark details
        """
        partner_id = request.data.get('partner_id')
        mc_id = request.data.get('mc_id')
        snippets = self.queryset.filter(partner_id=partner_id, mc_id=mc_id)
        if snippets:
            snippets.delete()
            return Response({
                "success": True,
                "message": "Successfully Deleted",
                "data": {},
            }, status=status.HTTP_200_OK)
        else:
            serializer = self.serializer_class(data=request.data, context={"user": self.get_user()})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": serializer.data,
                }, status=status.HTTP_200_OK)

        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        """
        Updates snippets delete
        :param kwargs: snippets id
        :return: message
        """
        partner_id = request.data.get('partner_id')
        mc_id = request.data.get('mc_id')
        snippets = self.queryset.filter(partner_id=partner_id, mc_id=mc_id)
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


class MCBookmarksGetAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.McBookmarksSerializers
    queryset = models.MCBookmarks.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
        """
            create MC Bookmark details
            :param request: Bookmark details
            :param kwargs: NA
            :return: Bookmark details
        """

        try:
            current_user = request.user.id
            mc_bookmarks = models.MCBookmarks.objects.filter(partner_id=current_user)
            if mc_bookmarks:
                mc_list = []
                for i in mc_bookmarks:
                    mc_data = models.MC.objects.filter(id=i.mc_id.id)
                    for val in mc_data:
                        option_list = []
                        mc_options = theme_models.McOptions.objects.filter(mc_id=i.mc_id.id)
                        if mc_options:
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
                        mark_dict = {
                            "id": i.id,
                            "mc_id": i.mc_id.id if i.mc_id else False,
                            "partner_id": i.partner_id.id if i.partner_id else False,
                            "theme_id": val.theme_id.id if val.theme_id else False,
                            "theme_name": val.theme_id.theme_english_name if val.theme_id else False,
                            "theme_sequence": val.theme_id.sequence if val.theme_id else False,
                            "topic_id": val.topic_id.id if val.topic_id else False,
                            "topic_name": val.topic_id.topic_english_name if val.topic_id else False,
                            "topic_sequence": val.topic_id.sequence if val.topic_id else False,
                            "learning_focus_id": val.learning_focus_id.id if val.learning_focus_id else False,
                            "learning_focus_name": val.learning_focus_id.english if val.learning_focus_id else False,
                            "learning_focus_chinese_name": val.learning_focus_id.chinese if val.learning_focus_id else False,
                            "mc_english_source_ref": val.mc_english_source_ref,
                            "mc_chinese_source_ref": val.mc_chinese_source_ref,
                            "mc_english_source_details": val.mc_english_source_details,
                            "mc_chinese_source_details": val.mc_chinese_source_details,
                            "mc_english_question": val.mc_english_question,
                            "mc_chinese_question": val.mc_chinese_question,
                            "mc_english_question_bookmark": val.mc_english_question_bookmark,
                            "mc_chinese_question_bookmark": val.mc_chinese_question_bookmark,
                            "answer": val.answer,
                            "mark": val.mark,
                            "total_mark": val.total_mark,
                            "no_of_respondents": val.no_of_respondents,
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date),
                            "is_bookmarked": True,
                            "option_list": option_list
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
        except:
            return Response({"success": False, "Message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class SQBookmarksAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.SqBookmarksSerializers
    queryset = models.SQBookmarks.objects.all().order_by('-id')

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
            create MC Bookmark details
            :param request: Bookmark details
            :param kwargs: NA
            :return: Bookmark details
        """
        partner_id = request.data.get('partner_id')
        sq_id = request.data.get('sq_id')
        snippets = self.queryset.filter(partner_id=partner_id, sq_id=sq_id)
        if snippets:
            snippets.delete()
            return Response({
                "success": True,
                "message": "Successfully Deleted",
                "data": {},
            }, status=status.HTTP_200_OK)
        else:
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
        partner_id = request.data.get('partner_id')
        sq_id = request.data.get('sq_id')
        snippets = self.queryset.filter(partner_id=partner_id, sq_id=sq_id)
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


class SQBookmarksGetAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.SqBookmarksSerializers
    queryset = models.SQBookmarks.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
        """
            create MC Bookmark details
            :param request: Bookmark details
            :param kwargs: NA
            :return: Bookmark details
        """

        try:
            current_user = request.user.id
            sq_bookmarks = models.SQBookmarks.objects.filter(partner_id=current_user)
            if sq_bookmarks:
                mc_list = []
                for i in sq_bookmarks:
                    sq_data = models.ShortQuestion.objects.filter(id=i.sq_id.id)
                    for val in sq_data:
                        mark_list = []
                        sq_options = theme_models.ShortQuestionMarkPoints.objects.filter(sq_id=i.sq_id.id)
                        if sq_options:
                            for mark in sq_options:
                                option_dict = {
                                    "id": mark.id,
                                    "sq_id": mark.sq_id.id if mark.sq_id else False,
                                    "sq_english_mark_points": mark.sq_english_mark_points,
                                    "sq_chinese_mark_points": mark.sq_chinese_mark_points,
                                    "sq_english_mark": mark.sq_english_mark,
                                    "sq_chinese_mark": mark.sq_chinese_mark,
                                    "created_date": str(mark.created_date),
                                    "updated_date": str(mark.updated_date)
                                }
                                mark_list.append(option_dict)
                        mark_dict = {
                            "id": i.id,
                            "sq_id": i.sq_id.id if i.sq_id else False,
                            "partner_id": i.partner_id.id if i.partner_id else False,
                            "theme_id": val.theme_id.id if val.theme_id else False,
                            "theme_name": val.theme_id.theme_english_name if val.theme_id else False,
                            "theme_sequence": val.theme_id.sequence if val.theme_id else False,
                            "topic_id": val.topic_id.id if val.topic_id else False,
                            "topic_name": val.topic_id.topic_english_name if val.topic_id else False,
                            "topic_sequence": val.topic_id.sequence if val.topic_id else False,
                            "learning_focus_id": val.learning_focus_id.id if val.learning_focus_id else False,
                            "learning_focus_name": val.learning_focus_id.english if val.learning_focus_id else False,
                            "learning_focus_chinese_name": val.learning_focus_id.chinese if val.learning_focus_id else False,
                            "sq_english_source_ref": val.sq_english_source_ref,
                            "sq_chinese_source_ref": val.sq_chinese_source_ref,
                            "sq_english_source_details": val.sq_english_source_details,
                            "sq_chinese_source_details": val.sq_chinese_source_details,
                            "sq_english_question": val.sq_english_question,
                            "sq_chinese_question": val.sq_chinese_question,
                            "sq_english_question_bookmark": val.sq_english_question_bookmark,
                            "sq_chinese_question_bookmark": val.sq_chinese_question_bookmark,
                            "sq_english_suggested_answer": val.sq_english_suggested_answer,
                            "sq_chinese_suggested_answer": val.sq_chinese_suggested_answer,
                            "sq_total_mark": val.sq_total_mark,
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date),
                            "is_bookmarked": True,
                            "mark_list": mark_list
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
        except:
            return Response({"success": False, "Message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class CardsBookmarksAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CardsBookmarksSerializers
    queryset = models.CardsBookmarks.objects.all().order_by('-id')

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
            create MC Bookmark details
            :param request: Bookmark details
            :param kwargs: NA
            :return: Bookmark details
        """
        partner_id = request.data.get('partner_id')
        card_id = request.data.get('card_id')
        # card_index passed when creating bookmark
        snippets = self.queryset.filter(partner_id=partner_id, card_id=card_id)
        if snippets:
            snippets.delete()
            return Response({
                "success": True,
                "message": "Successfully Deleted",
                "data": {},
            }, status=status.HTTP_200_OK)
        else:
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

        partner_id = request.data.get('partner_id')
        card_id = request.data.get('card_id')
        snippets = self.queryset.filter(partner_id=partner_id, card_id=card_id)
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


class CardBookmarksGetAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CardsBookmarksSerializers
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = models.CardsBookmarks.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
        """
            create MC Bookmark details
            :param request: Bookmark details
            :param kwargs: NA
            :return: Bookmark details
        """

        try:
            current_user = request.user.id
            http_layer = request.is_secure() and "https" or "http"
            http_address = request.get_host()
            urls = str(http_layer + "://" + http_address)
            card_bookmarks = models.CardsBookmarks.objects.filter(partner_id=current_user)
            if card_bookmarks:
                mc_list = []
                for i in card_bookmarks:
                    sq_data = models.Cards.objects.filter(id=i.card_id.id)
                    for val in sq_data:
                        mark_dict = {
                            "id": i.id,
                            "card_id": i.card_id.id if i.card_id else False,
                            "card_index": i.card_index if i.card_index else 0,
                            "partner_id": i.partner_id.id if i.partner_id else False,
                            "card_title_id": val.card_title_id.id if val.card_title_id else False,
                            "card_title_name": val.card_title_id.card_english_title if val.card_title_id else False,
                            "card_chinese_title_name": val.card_title_id.card_chinese_title if val.card_title_id else False,
                            "theme_id": val.card_title_id.theme_id.id if val.card_title_id.theme_id else False,
                            "theme_name": val.card_title_id.theme_id.theme_english_name if val.card_title_id.theme_id else False,
                            "theme_chinese_name": val.card_title_id.theme_id.theme_chinese_name if val.card_title_id.theme_id else False,
                            "theme_image": urls + "/media/" + str(val.card_title_id.theme_id.theme_image) or False,
                            "topic_id": val.card_title_id.topic_id.id if val.card_title_id.topic_id else False,
                            "topic_name": val.card_title_id.topic_id.topic_english_name if val.card_title_id.topic_id else False,
                            "theme_sequence": val.card_title_id.theme_id.sequence if val.card_title_id.theme_id else False,
                            "topic_sequence": val.card_title_id.topic_id.sequence if val.card_title_id.topic_id else False,
                            "topic_chinese_name": val.card_title_id.topic_id.topic_chinese_name if val.card_title_id.topic_id else False,
                            "card_english_summary_title": val.card_english_summary_title,
                            "card_chinese_summary_title": val.card_chinese_summary_title,
                            "card_english_summary": val.card_english_summary,
                            "card_chinese_summary": val.card_chinese_summary,
                            "is_bookmarked": True,
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
        except:
            return Response({"success": False, "Message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class BookmarkCount(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CardsBookmarksSerializers
    queryset = models.CardsBookmarks.objects.all().order_by('-id')

    @api_view(['GET'])
    def snippet_detail(request):
        """
            create MC Bookmark details
            :param request: Bookmark details
            :param kwargs: NA
            :return: Bookmark details
        """

        try:
            user_status = ""
            current_user = request.user.id
            try:
                user_data = user.objects.get(id=current_user)
                if user_data:
                    user_data = user.objects.get(id=current_user)
                    tokens = AuthToken.objects.filter(user_id=user_data.id)
                    if tokens:
                        user_status = "Authentication failed"
                else:
                    user_status = "User Does not Exists"

            except ObjectDoesNotExist:
                return Response({"success": False, "Message": "User Not Found"},
                                status=status.HTTP_400_BAD_REQUEST)
            mc_bookmarks = models.MCBookmarks.objects.filter(partner_id=current_user)
            sq_bookmarks = models.SQBookmarks.objects.filter(partner_id=current_user)
            card_bookmarks = models.CardsBookmarks.objects.filter(partner_id=current_user)

            count_dict = {
                "mc_bookmarks_count": len(mc_bookmarks),
                "sq_bookmarks_count": len(sq_bookmarks),
                "card_bookmarks_count": len(card_bookmarks)
            }
            return Response({
                "success": True,
                "message": "Success",
                "user_status": user_status,
                "data": count_dict,
            }, status=status.HTTP_200_OK)

        except:
            return Response({"success": False, "Message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)

