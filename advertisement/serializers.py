from rest_framework import serializers
from advertisement.models import Advertisement


class AdvertisementSerializers(serializers.ModelSerializer):

    class Meta:
        model = Advertisement
        fields = '__all__'


class AdvertisementSerializerPut(serializers.ModelSerializer):

    class Meta:
        model = Advertisement
        fields = (
            'id', 'customer_name', 'company_name', 'company_name', 'english_title', 'chinese_title',
            'advertisement_image', 'advertisement_link', 'advertisement_start_date', 'advertisement_end_date',
            'advertisement_price', 'advertisement_active',
        )
