import uuid
from django.db import models
from django.contrib import admin
from django.utils.translation import gettext as _
from djmoney.models.fields import MoneyField

# Create your models here.


class Advertisement(models.Model):

    customer_name = models.CharField(max_length=500, null=True, blank=True)
    company_name = models.CharField(max_length=500, null=True, blank=True)
    english_title = models.CharField(max_length=500, null=True, blank=True)
    chinese_title = models.CharField(max_length=500, null=True, blank=True)

    advertisement_image = models.ImageField(_("Image"), upload_to='media/', blank=True, null=True)
    advertisement_link = models.CharField(max_length=500, blank=True, null=True)

    advertisement_start_date = models.DateField(editable=True, null=True, blank=True)
    advertisement_end_date = models.DateField(editable=True, null=True, blank=True)
    advertisement_price = models.CharField(max_length=500, null=True, blank=True)
    # advertisement_price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', blank=True, null=True)
    advertisement_payment_method = models.CharField(max_length=500, blank=True, null=True)

    advertisement_active = models.BooleanField(default=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.english_title)

    class Meta:
        ordering = ['-created_date']


class AdvertisementList(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'company_name', 'english_title',
                    'advertisement_price', 'advertisement_payment_method', 'advertisement_active')


admin.site.register(Advertisement, AdvertisementList)
