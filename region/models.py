import uuid
from django.db import models
from django.contrib import admin


class Region(models.Model):

    chinese_name = models.CharField(max_length=500)
    english_name = models.CharField(max_length=500)
    region_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.english_name


class RegionList(admin.ModelAdmin):
    list_display = (
        'id', 'english_name', 'chinese_name',
        'created_date', 'updated_date')


class District(models.Model):

    chinese_name = models.CharField(max_length=500)
    english_name = models.CharField(max_length=500)
    district_id = models.UUIDField(default=uuid.uuid4, editable=False)
    region_id = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, default="")
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.english_name

    class Meta:
        ordering = ['-english_name']


class DistrictList(admin.ModelAdmin):
    list_display = (
        'id', 'english_name', 'chinese_name', 'region_id',
        'created_date', 'updated_date')


class School(models.Model):
    school_name = models.CharField(max_length=500)
    school_chinese_name = models.CharField(max_length=500)
    school_id = models.UUIDField(default=uuid.uuid4, editable=False)
    region_id = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, default="")
    district_id = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True, default="")
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.school_name)

    class Meta:
        ordering = ['-school_name']


class SchoolList(admin.ModelAdmin):
    list_display = (
        'id', 'school_name', 'school_chinese_name', 'region_id',
        'district_id', 'created_date', 'updated_date')


class User_role(models.Model):

    role_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500)
    privileges = models.CharField(max_length=500)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['-name']


class User_profile(models.Model):

    profile_id = models.UUIDField(default=uuid.uuid4, editable=False)
    profile_pic = models.CharField(max_length=500)
    profile_pic_1920 = models.ImageField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.profile_id)


class Address(models.Model):

    # number = random.randint(1111, 9999)
    # id = models.BigAutoField(primary_key=True, blank=True, default=number)
    address_id = models.UUIDField(default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True, default="")
    region_id = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, default="")
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.address_id)


class Forms(models.Model):
    # number = random.randint(1111, 9999)
    # id = models.BigAutoField(primary_key=True, blank=True, default=number)
    form_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500)
    chinese_name = models.CharField(max_length=500, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['-name']


admin.site.register(Forms)
admin.site.register(Region, RegionList)
admin.site.register(District, DistrictList)
admin.site.register(School, SchoolList)
admin.site.register(User_role)
admin.site.register(User_profile)
admin.site.register(Address)
