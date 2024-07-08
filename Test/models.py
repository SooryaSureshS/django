import uuid
from django.db import models
from django.contrib import admin
from django.utils.translation import gettext as _
from djmoney.models.fields import MoneyField
from accounts.models import user
from theme.models import *
from deleted_users.models import DeletedUsers
# Create your models here.


class TestDetails(models.Model):

    partner_id = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_user_id = models.ForeignKey(DeletedUsers, null=True, blank=True, on_delete=models.SET_NULL)
    mc_id = models.ForeignKey(MC, on_delete=models.CASCADE, null=True, blank=True)
    sq_id = models.ForeignKey(ShortQuestion, on_delete=models.CASCADE, null=True, blank=True)
    theme_id = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, blank=True)
    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    total_mark = models.FloatField(blank=False, null=True)
    answer = models.TextField(blank=False, null=True)
    obtained_total_mark = models.FloatField(blank=False, null=True)
    is_mc = models.BooleanField(default=False)
    is_sq = models.BooleanField(default=False)
    duration = models.TextField(null=True, blank=True) # In Minutes
    unique_string = models.CharField(max_length=500, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.partner_id)


class TestDetailsList(admin.ModelAdmin):
    list_display = ('id', 'partner_id', 'deleted_user_id','mc_id', 'sq_id', 'theme_id', 'topic_id',
                    'total_mark', 'obtained_total_mark', 'is_mc', 'is_sq')


class TestAttendedQuestions(models.Model):

    partner_id = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_user_id = models.ForeignKey(DeletedUsers, null=True, blank=True, on_delete=models.SET_NULL)
    mc_id = models.ForeignKey(MC, on_delete=models.CASCADE, null=True, blank=True)
    sq_id = models.ForeignKey(ShortQuestion, on_delete=models.CASCADE, null=True, blank=True)
    theme_id = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, blank=True)
    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    total_mark = models.FloatField(blank=False, null=True)
    answer = models.TextField(blank=False, null=True)
    obtained_total_mark = models.FloatField(blank=False, null=True)
    is_mc = models.BooleanField(default=False)
    is_sq = models.BooleanField(default=False)
    duration = models.FloatField(null=True, blank=True)
    unique_string = models.CharField(max_length=500, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.id)


class TestAttendedQuestionsList(admin.ModelAdmin):
    list_display = ('id', 'partner_id', 'deleted_user_id', 'mc_id', 'sq_id', 'theme_id', 'topic_id',
                    'total_mark', 'obtained_total_mark', 'is_mc', 'is_sq')


admin.site.register(TestDetails, TestDetailsList)
admin.site.register(TestAttendedQuestions, TestAttendedQuestionsList)
