from django.db import models
from django.contrib import admin
from accounts.models import user
from theme.models import Cards
from theme.models import ShortQuestion
from theme.models import MC
from deleted_users.models import DeletedUsers


class CardsBookmarks(models.Model):

    name = models.CharField(max_length=200, blank=True, null=True)
    partner_id = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_user_id = models.ForeignKey(DeletedUsers, null=True, blank=True, on_delete=models.SET_NULL)
    card_id = models.ForeignKey(Cards, on_delete=models.CASCADE, null=True, blank=True)
    card_index = models.IntegerField(null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['-name']


class CardsBookmarksList(admin.ModelAdmin):
    list_display = ('id', 'name', 'card_id', 'partner_id', 'deleted_user_id', 'created_date', 'updated_date')


class MCBookmarks(models.Model):

    name = models.CharField(max_length=200, blank=True, null=True)
    partner_id = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_user_id = models.ForeignKey(DeletedUsers, null=True, blank=True, on_delete=models.SET_NULL)
    mc_id = models.ForeignKey(MC, on_delete=models.CASCADE, null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['-name']


class MCBookmarksList(admin.ModelAdmin):
    list_display = ('id', 'name', 'mc_id', 'partner_id', 'deleted_user_id', 'created_date', 'updated_date')


class SQBookmarks(models.Model):

    name = models.CharField(max_length=200, blank=True, null=True)
    partner_id = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_user_id = models.ForeignKey(DeletedUsers, null=True, blank=True, on_delete=models.SET_NULL)
    sq_id = models.ForeignKey(ShortQuestion, on_delete=models.CASCADE, null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['-name']


class SQBookmarksList(admin.ModelAdmin):
    list_display = ('id', 'name', 'sq_id', 'partner_id', 'deleted_user_id', 'created_date', 'updated_date')


admin.site.register(CardsBookmarks, CardsBookmarksList)
admin.site.register(MCBookmarks, MCBookmarksList)
admin.site.register(SQBookmarks, SQBookmarksList)
