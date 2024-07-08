from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager
from django.contrib import admin
from region.models import District
from region.models import Region
from region.models import School
from region.models import User_role
from region.models import Forms
from region.models import Address
from region.models import User_profile
from deleted_users.models import DeletedUsers
from django.db import models


class user(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True, max_length=255, blank=False, null=False,
                              error_messages={'unique': "This email has already been registered."})
    contact = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=17, blank=False, null=True, )

    profile_picture = models.ImageField(upload_to='media/', blank=True, null=True, )

    district_id = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    region_id = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    school_id = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)

    role_id = models.ForeignKey(User_role, on_delete=models.CASCADE, null=True, blank=True)
    form_id = models.ForeignKey(Forms, on_delete=models.CASCADE, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey(User_profile, on_delete=models.CASCADE, null=True, blank=True)
    firstname = models.CharField(max_length=200, default='', null=True, blank=True)
    lastname = models.CharField(max_length=200, default='', null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True, editable=False, null=True, blank=True)
    registration_time = models.TimeField(auto_now_add=True, editable=False, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)
    role = models.CharField(max_length=200, null=True, blank=True)

    is_purchased = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    otp = models.CharField(max_length=200, default=False, null=True, blank=True)
    email_otp = models.CharField(max_length=200, default=False, null=True, blank=True)
    email_url = models.CharField(max_length=500, default="1234587469502jhjghfgfsfdsxfxs", null=True, blank=True)
    reset_email = models.CharField(max_length=200, default=False, null=True, blank=True)
    password_url = models.CharField(max_length=500, default="1234587469502jhjghfgfsfdsxfxs", null=True, blank=True)
    password_set_url = models.CharField(max_length=500, default="1", null=True, blank=True)

    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('zh', 'Chinese'),
    )

    language = models.CharField(max_length=30, default="en", choices=LANGUAGE_CHOICES, null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    @property
    def full_name(self):
        return '%s %s (%s)' % (self.firstname, self.lastname, self.email)

    @property
    def show_name(self):
        return '%s %s' % (self.firstname, self.lastname)


class login_frequency(models.Model):

    user_id = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_user_id = models.ForeignKey(DeletedUsers, null=True, blank=True, on_delete=models.SET_NULL)
    form_id = models.ForeignKey(Forms, on_delete=models.CASCADE, null=True, blank=True)
    login_date = models.DateField(auto_now_add=True, editable=True, null=True, blank=True)
    login_time = models.TimeField(auto_now_add=True, editable=True, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=True, null=True, blank=True)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        ordering = ['-created_date']


class login_frequencyList(admin.ModelAdmin):
    list_display = (
        'id', 'user_id', 'deleted_user_id', 'form_id', 'login_date', 'login_time',
        'created_date', 'updated_date')


class RegisterEmailVerify(models.Model):

    email = models.CharField(max_length=200, default='', null=True, blank=True)
    email_otp = models.CharField(max_length=200, default=False, null=True, blank=True)
    email_url = models.CharField(max_length=500, default="1234587469502jhjghfgfsfdsxfxs", null=True, blank=True)
    reset_email = models.CharField(max_length=200, default=False, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=True, null=True, blank=True)


class RegisterEmailVerifyList(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'email_otp', 'email_url', 'reset_email',
        'created_date', 'updated_date')


admin.site.register(login_frequency, login_frequencyList)
admin.site.register(user)
admin.site.register(RegisterEmailVerify, RegisterEmailVerifyList)
