from rest_framework import serializers
from product.models import ProductPrice


class ProductPriceSerializers(serializers.ModelSerializer):

    class Meta:
        model = ProductPrice
        fields = '__all__'
