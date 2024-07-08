from rest_framework import serializers
from .models import Region
from .models import District
from .models import School
from accounts.models import user
from .models import Forms


class RegionSerializers(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = '__all__'


class DistrictSerializers(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = '__all__'


class DistrictSerializersPost(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = ('region_id',)


class SchoolSerializers(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = '__all__'


class SchoolSerializersPost(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = ('region_id',)


class AccountSerializers(serializers.ModelSerializer):

    class Meta:
        model = user
        fields = '__all__'


class AccountSerializersPost(serializers.ModelSerializer):

    class Meta:
        model = user
        fields = ('user',)


class FormsSerializers(serializers.ModelSerializer):

    class Meta:
        model = Forms
        fields = '__all__'


class FormsSerializersPost(serializers.ModelSerializer):

    class Meta:
        model = Forms
        fields = ('form_id',)


from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect Credentials Passed.')
