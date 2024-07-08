from rest_framework import serializers
from PurchaseOrder.models import PurchaseOrder


class PurchaseOrderSerializers(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
