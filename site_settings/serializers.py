from rest_framework import serializers
from site_settings. models import PrivacyPolicy, TermsAndCondition


class PrivacyPolicySerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivacyPolicy
        fields = '__all__'


class TermsAndConditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TermsAndCondition
        fields = '__all__'
