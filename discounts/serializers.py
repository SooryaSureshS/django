from rest_framework import serializers
from discounts.models import Discount
from discounts.models import DiscountUsage


class DiscountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Discount
        fields = '__all__'


class DiscountUsageSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiscountUsage
        fields = '__all__'
