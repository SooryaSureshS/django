from django.db import models
from django.contrib import admin


class PrivacyPolicy(models.Model):

    privacy_policy_heading = models.CharField(max_length=200, blank=True, null=True)
    privacy_policy_content = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.privacy_policy_heading)

    class Meta:
        ordering = ['-created_date']


class PrivacyPolicyList(admin.ModelAdmin):
    list_display = (
        'id', 'privacy_policy_heading', 'privacy_policy_content', 'created_date', 'updated_date')


class TermsAndCondition(models.Model):

    terms_and_condition_policy_heading = models.CharField(max_length=200, blank=True, null=True)
    terms_and_condition_policy_content = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.terms_and_condition_policy_heading)

    class Meta:
        ordering = ['-created_date']


class TermsAndConditionList(admin.ModelAdmin):
    list_display = (
        'id', 'terms_and_condition_policy_heading', 'terms_and_condition_policy_content',
        'created_date', 'updated_date')


admin.site.register(PrivacyPolicy, PrivacyPolicyList)
admin.site.register(TermsAndCondition, TermsAndConditionList)
