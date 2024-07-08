from rest_framework import serializers
from bookmarks.models import *


class CardsBookmarksSerializers(serializers.ModelSerializer):

    class Meta:
        model = CardsBookmarks
        fields = '__all__'


class McBookmarksSerializers(serializers.ModelSerializer):

    class Meta:
        model = MCBookmarks
        fields = '__all__'


class SqBookmarksSerializers(serializers.ModelSerializer):

    class Meta:
        model = SQBookmarks
        fields = '__all__'
