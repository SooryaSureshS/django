from django.db import models
from accounts.models import District, Region, School
from accounts.models import User_role, Forms, Address, User_profile

class DeletedUsers(models.Model):
    email = models.EmailField(unique=True, max_length=255, blank=False, null=False, )
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
    registration_date = models.DateField(editable=True, null=True, blank=True)
    registration_time = models.TimeField(editable=True, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)
    role = models.CharField(max_length=200, null=True, blank=True)

    is_purchased = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('zh', 'Chinese'),
    )

    language = models.CharField(max_length=30, default="en", choices=LANGUAGE_CHOICES, null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.email

