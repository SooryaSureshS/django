from rest_framework import serializers
from accounts.models import user, RegisterEmailVerify
from region.models import District
from region.models import Region
from region.models import School
from region.models import Forms
from region.models import User_profile
from region.models import User_role
from region.models import Address
from django.utils.translation import gettext as _

from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=user.objects.all())]
            )
    firstname = serializers.CharField(min_length=2)
    password = serializers.CharField(min_length=8)

    def create(self, validated_data):
        extra_fields = {}
        district_id = None
        extra_fields['district_id'] = district_id
        if validated_data.get('district_id'):
            district_id = District.objects.filter(id=validated_data['district_id'].id).first()
            extra_fields['district_id'] = district_id
        region_id = None
        extra_fields['region_id'] = region_id
        if validated_data.get('region_id'):
            region_id = Region.objects.filter(id=validated_data['region_id'].id).first()
            extra_fields['region_id'] = region_id
        school_id = None
        extra_fields['school_id'] = school_id
        if validated_data.get('school_id'):
            school_id = School.objects.filter(id=validated_data['school_id'].id).first()
            extra_fields['school_id'] = school_id
        form_id = None
        extra_fields['form_id'] = form_id
        if validated_data.get('form_id'):
            form_id = Forms.objects.filter(id=validated_data['form_id'].id).first()
            extra_fields['form_id'] = form_id
        profile = None
        extra_fields['profile'] = profile
        if validated_data.get('profile'):
            profile_id = User_profile.objects.filter(id=validated_data['profile'].id).first()
            extra_fields['profile'] = profile.id
        address = None
        extra_fields['address'] = address
        if validated_data.get('address'):
            address = Address.objects.filter(id=validated_data['address'].id).first()
            extra_fields['address_id'] = address.id
        phone = None
        extra_fields['phone'] = phone
        if validated_data.get('phone'):
            phone = validated_data['phone']
            extra_fields['phone'] = phone
        lastname = None
        extra_fields['lastname'] = lastname
        if validated_data.get('lastname'):
            lastname = validated_data['lastname']
            extra_fields['lastname'] = lastname
        if validated_data.get('language'):
            language = validated_data['language']
            extra_fields['language'] = language

        role = None
        role_id = None
        extra_fields['role'] = role
        extra_fields['role_id'] = role_id
        if validated_data.get('role'):
            if validated_data['role'] == "Admin":
                if User_role.objects.filter(name=validated_data['role']).first():
                    role = User_role.objects.filter(name=validated_data['role']).first()
                    extra_fields['role'] = validated_data['role']
                    extra_fields['role_id'] = role
                    extra_fields['is_admin'] = True
            if validated_data['role'] == "Student":
                if User_role.objects.filter(name=validated_data['role']).first():
                    role = User_role.objects.filter(name=validated_data['role']).first()
                    extra_fields['role'] = validated_data['role']
                    extra_fields['role_id'] = role
                    extra_fields['is_student'] = True
            if validated_data['role'] == "Teacher":
                if User_role.objects.filter(name=validated_data['role']).first():
                    role = User_role.objects.filter(name=validated_data['role']).first()
                    extra_fields['role'] = validated_data['role']
                    extra_fields['role_id'] = role
                    extra_fields['is_teacher'] = True
        is_superuser = None
        extra_fields['is_superuser'] = is_superuser
        if validated_data.get('is_superuser'):
            is_superuser = validated_data['is_superuser']
            extra_fields['is_superuser'] = is_superuser
            if is_superuser:
                extra_fields['is_staff'] = True
                extra_fields['is_superuser'] = True
        users = user.objects.create_user(validated_data['email'], validated_data['password'],
                                         validated_data['firstname'], extra_fields)
        users.language = validated_data.get('language')
        users.save()
        return users

    def save(self):
        user = super(UserSerializer, self).save()
        user.is_student = True
        user.save()
        return user

    class Meta:
        model = user
        fields = ('id', 'firstname', 'email', 'password', 'district_id', 'region_id', 'school_id', 'form_id',
                  'profile_id', 'address_id', 'profile_id', 'phone', 'lastname', 'role', 'role_id', 'language',
                  'is_teacher', 'is_student', 'is_admin')


# Register Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = user
        fields = ('id', 'firstname', 'email', 'password', 'district_id', 'region_id', 'form_id'
                  'school_id', 'profile_id', 'address_id', 'profile_id', 'phone', 'lastname', 'role', 'role_id',
                  'is_teacher', 'is_student', 'is_admin')

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError({
            'warning': _('Incorrect Credentials Passed.')
        })


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = ('id', 'email', 'password', 'region_id')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        users = user.objects.create_user(validated_data['email'], validated_data['password'])
        return users


from django.contrib.auth import authenticate


class TokenSerializer(serializers.Serializer):


    class Meta:
        model = user
        fields = ('id', 'firstname', 'email', 'password', 'district_id', 'region_id', 'school_id', 'form_id'
                  'profile_id', 'address_id', 'profile_id', 'phone', 'lastname', 'role', 'role_id', 'is_teacher',
                  'is_student', 'is_admin')


class AccountSerializers1(serializers.ModelSerializer):

    class Meta:
        model = user
        fields = '__all__'


class RegisterEmailVerifySerializers1(serializers.ModelSerializer):

    class Meta:
        model = RegisterEmailVerify
        fields = '__all__'
