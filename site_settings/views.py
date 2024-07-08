from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from site_settings import serializers, models
from site_settings.models import PrivacyPolicy, TermsAndCondition
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser


class PrivacyPolicyAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    # permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.PrivacyPolicySerializer
    queryset = models.PrivacyPolicy.objects.all().order_by('-id')

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
            if PrivacyPolicy.objects.exists():
                return Response({
                    "success": False,
                    "message": "This model has already its record",
                    "data": serializer.data,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
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


class TermsAndConditionAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    # permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.TermsAndConditionSerializer
    queryset = models.TermsAndCondition.objects.all().order_by('-id')

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
            if TermsAndCondition.objects.exists():
                return Response({
                    "success": False,
                    "message": "This model has already its record",
                    "data": serializer.data,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
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


class PrivacyPolicyGetAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    # permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.PrivacyPolicySerializer
    queryset = models.PrivacyPolicy.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        try:
            privacy_policy = PrivacyPolicy.objects.all()
            vals = {}
            if privacy_policy:
                for i in privacy_policy:
                    vals = {
                        'id': i.id,
                        'privacy_policy_heading': i.privacy_policy_heading,
                        'privacy_policy_content': i.privacy_policy_content,
                        'created_date': i.created_date,
                        'updated_date': i.updated_date,
                    }

                return Response({
                    "success": True,
                    "message": "Success",
                    "data": vals
                }, status=status.HTTP_201_CREATED)

            else:
                return Response({"success": False, "message": "No Data", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"success": False, "message": "Failed", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class TermsAndConditionGetAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    # permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.TermsAndConditionSerializer
    queryset = models.TermsAndCondition.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        try:
            terms_condition = models.TermsAndCondition.objects.all()
            vals = {}
            if terms_condition:
                for i in terms_condition:
                    vals = {
                        'id': i.id,
                        'terms_and_condition_policy_heading': i.terms_and_condition_policy_heading,
                        'terms_and_condition_policy_content': i.terms_and_condition_policy_content,
                        'created_date': i.created_date,
                        'updated_date': i.updated_date,
                    }
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": vals
                }, status=status.HTTP_201_CREATED)

            else:
                return Response({"success": False, "message": "No Data", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"success": False, "message": "Failed", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)

