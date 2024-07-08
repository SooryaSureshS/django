from rest_framework import serializers
from Test.models import *


class TestDetailsSerializers(serializers.ModelSerializer):

    class Meta:
        model = TestDetails
        fields = (
            'id', 'partner_id', 'mc_id',
            'sq_id', 'total_mark', 'unique_string',
            'obtained_total_mark', 'is_mc', 'topic_id',
            'is_sq', 'answer', 'duration',
            'created_date', 'updated_date')


class TestAttendedSerializers(serializers.ModelSerializer):

    class Meta:
        model = TestAttendedQuestions
        fields = (
            'id', 'partner_id', 'mc_id', 'sq_id',
            'total_mark', 'obtained_total_mark',
            'is_mc', 'is_sq', 'answer', 'unique_string',
            'created_date', 'updated_date')
