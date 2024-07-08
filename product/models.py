import uuid
from django.db import models
from django.contrib import admin
from django.utils.translation import gettext as _
from djmoney.models.fields import MoneyField

# Create your models here.


class ProductPrice(models.Model):

    product_apple_pay_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', blank=True, null=True)
    product_google_pay_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.product_apple_pay_amount)


admin.site.register(ProductPrice)
