from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from product import serializers, models
from product.models import ProductPrice
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser

# Create your views here.


class ProductPriceAPI(generics.ListCreateAPIView):
    """
        List and Create Topic
    """
    # permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = serializers.ProductPriceSerializers
    queryset = models.ProductPrice.objects.all().order_by('-id')

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
            if ProductPrice.objects.exists():
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


class ProductPriceGetItem(generics.ListCreateAPIView):
    """
        Get One Advertisement
    """
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ProductPriceSerializers
    queryset = models.ProductPrice.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            pk = request.data.get('id')
            snippet = models.ProductPrice.objects.get(id=pk)
        except ProductPrice.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            serializer = serializers.ProductPriceSerializers(snippet)
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)

