from django.db import models
from django.contrib import admin
from accounts.models import user
from region.models import Forms
from discounts.models import Discount
from djmoney.models.fields import MoneyField
from deleted_users.models import DeletedUsers

class PurchaseOrder(models.Model):

    name = models.CharField(max_length=200, blank=True, null=True)
    partner_id = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_user_id = models.ForeignKey(DeletedUsers, null=True, blank=True, on_delete=models.SET_NULL)
    form_id = models.ForeignKey(Forms, on_delete=models.CASCADE, null=True, blank=True)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
    tax = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
    discount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
    discount_id = models.ForeignKey(Discount, on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['-name']


class PurchaseOrderList(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'partner_id', 'deleted_user_id', 'created_date', 'updated_date')


class PaymentAcquirerStripe(models.Model):
    _inherit = 'payment.acquirer'

    provider = models.CharField(max_length=500, blank=True, null=True)
    stripe_secret_key = models.CharField(max_length=500, blank=True, null=True)
    stripe_publishable_key = models.CharField(max_length=500, blank=True, null=True)
    stripe_image_url = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class PaymentAcquirerStripeList(admin.ModelAdmin):
    list_display = (
        'id', 'provider', 'stripe_secret_key', 'stripe_publishable_key',
        'created_date', 'updated_date')


admin.site.register(PurchaseOrder, PurchaseOrderList)
admin.site.register(PaymentAcquirerStripe, PaymentAcquirerStripeList)
