from django.db import models
from django.contrib import admin
from region.models import School
from accounts.models import user
from deleted_users.models import DeletedUsers


class Discount(models.Model):
    promotion_name = models.CharField(max_length=500, null=True, blank=True)
    discount_code = models.CharField(max_length=500, null=True, blank=True)
    discount_percentage = models.BooleanField(default=False, null=True, blank=True)
    discount_percentage_value = models.CharField(max_length=500, editable=True, null=True, blank=True)
    discount_reduce_amount = models.BooleanField(default=False, null=True, blank=True)
    discount_reduce_amount_value = models.CharField(max_length=500, editable=True, null=True, blank=True)
    discount_start_date = models.DateField(editable=True, null=True, blank=True)
    discount_end_date = models.DateField(editable=True, null=True, blank=True)
    discount_status = models.BooleanField(default=True, null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.promotion_name)


class DiscountList(admin.ModelAdmin):
    list_display = (
        'id', 'promotion_name', 'discount_code', 'discount_percentage',
        'discount_reduce_amount', 'discount_start_date',
        'discount_end_date', 'discount_status',
        'created_date', 'updated_date')


class DiscountUsage(models.Model):

    discount_code = models.ForeignKey(Discount, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_user_id = models.ForeignKey(DeletedUsers, null=True, blank=True, on_delete=models.SET_NULL)
    school_id = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.discount_code)


class DiscountUsageList(admin.ModelAdmin):
    list_display = (
        'id', 'discount_code', 'user', 'deleted_user_id', 'school_id',
        'created_date', 'updated_date')


admin.site.register(DiscountUsage, DiscountUsageList)
admin.site.register(Discount, DiscountList)
