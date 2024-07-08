from django.db import models
import uuid
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
# from django_base64field.fields import Base64Field
# Create your models here.
from accounts.models import user
from deleted_users.models import DeletedUsers


class Theme(models.Model):

    sequence = models.IntegerField(blank=False, null=True)
    theme_english_name = models.CharField(max_length=200, blank=True, null=True)
    theme_chinese_name = models.CharField(max_length=200, blank=True, null=True)
    theme_image = models.ImageField(_("Image"), upload_to='media/', blank=True, null=True)
    theme_color = models.CharField(max_length=200, blank=True, null=True)
    theme_number = models.CharField(max_length=200, blank=True, null=True)
    english_tag = models.CharField(max_length=200, blank=True, null=True)
    chinese_tag = models.CharField(max_length=200, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.theme_english_name)

    class Meta:
        ordering = ['sequence']


class ThemeList(admin.ModelAdmin):
    list_display = (
                'id', 'sequence', 'theme_number', 'theme_english_name', 'theme_chinese_name', 'theme_color',
                'created_date', 'updated_date')


class Topic(models.Model):

    theme_id = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, blank=True)
    sequence = models.IntegerField(blank=False, null=True)
    topic_english_name = models.CharField(max_length=200, blank=False, null=True)
    topic_chinese_name = models.CharField(max_length=200, blank=False, null=True)
    learning_focus = models.CharField(max_length=500, blank=False,null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)
    english_tag = models.CharField(max_length=200, blank=True, null=True)
    chinese_tag = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.topic_english_name)

    class Meta:
        ordering = ['theme_id', 'sequence']


class TopicList(admin.ModelAdmin):
    list_display = ('id', 'sequence', 'topic_english_name', 'topic_chinese_name', 'learning_focus',
                    'theme_id', 'created_date', 'updated_date')


class Learningfocus(models.Model):

    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    english = models.CharField(max_length=500, blank=False, null=True)
    chinese = models.CharField(max_length=500, blank=False, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.english)

    class Meta:
        ordering = ['-created_date']


class LearningfocusList(admin.ModelAdmin):
    list_display = (
        'id', 'english','chinese',
        'created_date', 'updated_date')


class Cardstitle(models.Model):

    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    theme_id = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, blank=True)
    card_thumbnail_background = models.ImageField(_("Image"), upload_to='media/', blank=True, null=True)
    card_full_background = models.ImageField(_("Image"), upload_to='media/', blank=True, null=True)
    card_english_title = models.CharField(max_length=500, blank=False, null=True)
    card_chinese_title = models.CharField(max_length=500, blank=False, null=True)
    card_english_subtitle = models.CharField(max_length=500, blank=False, null=True)
    card_chinese_subtitle = models.CharField(max_length=500, blank=False, null=True)
    card_title_number = models.CharField(max_length=200, blank=True, null=True, editable=False)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.card_english_title)

    class Meta:
        ordering = ['-created_date']


class CardTitleList(admin.ModelAdmin):
    list_display = (
        'id', 'topic_id', 'theme_id', 'card_thumbnail_background',
        'card_full_background', 'card_title_number',
        'card_english_title',
        'card_chinese_title', 'card_english_subtitle', 'card_chinese_subtitle',
        'created_date', 'updated_date')


class Cards(models.Model):

    card_title_id = models.ForeignKey(Cardstitle, on_delete=models.CASCADE, null=True, blank=True)
    card_english_summary_title = models.CharField(max_length=500, blank=True, null=True)
    card_chinese_summary_title = models.CharField(max_length=500, blank=True, null=True)
    card_english_summary = models.TextField(blank=True, null=True)
    card_chinese_summary = models.TextField(blank=True, null=True)
    card_number = models.CharField(max_length=200, blank=True, null=True, editable=False)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.card_english_summary_title)

    class Meta:
        ordering = ['-created_date']


class CardList(admin.ModelAdmin):
    list_display = (
        'id', 'card_number','card_title_id',
        'card_english_summary_title',
        'card_chinese_summary_title','card_english_summary','card_chinese_summary',
        'created_date', 'updated_date')


class UserLearningCardData(models.Model):
    card_id = models.ForeignKey(Cards, on_delete=models.CASCADE, null=True, blank=True)
    partner_id = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_user_id = models.ForeignKey(DeletedUsers, null=True, blank=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class UserLearningCardDataList(admin.ModelAdmin):
    list_display = ('id', 'card_id', 'partner_id', 'deleted_user_id')


class MC(models.Model):

    mc_sequence = models.IntegerField(blank=False, null=True)
    theme_id = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, blank=True)
    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    learning_focus_id = models.ForeignKey(Learningfocus, on_delete=models.CASCADE, null=True, blank=True)

    mc_english_source_ref = models.TextField(blank=True, null=True)
    mc_chinese_source_ref = models.TextField(blank=True, null=True)

    mc_english_source_details = models.TextField(blank=True, null=True)
    mc_chinese_source_details = models.TextField(blank=True, null=True)

    mc_english_question = models.TextField(blank=False, null=True)
    mc_chinese_question = models.TextField(blank=False, null=True)
    mc_english_question_bookmark = models.TextField(blank=False, null=True)
    mc_chinese_question_bookmark = models.TextField(blank=False, null=True)

    answer = models.TextField(blank=False, null=True)
    mark = models.CharField(max_length=500, blank=False, null=True)
    total_mark = models.CharField(max_length=500, blank=False, null=True)
    no_of_respondents = models.CharField(max_length=500, blank=False, null=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.mc_english_source_ref)

    class Meta:
        ordering = ['-created_date']


class MCList(admin.ModelAdmin):
    list_display = (
        'id', 'mc_english_source_ref', 'theme_id', 'topic_id',
        'mc_english_source_details',
        'mc_english_question',
        'created_date', 'updated_date')


class McOptions(models.Model):

    mc_id = models.ForeignKey(MC, on_delete=models.CASCADE, null=True, blank=True)
    mc_answer_index = models.IntegerField(blank=False, null=True)
    mc_english_options = models.TextField(blank=False, null=True)
    mc_chinese_options = models.TextField(blank=False, null=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.mc_english_options)

    class Meta:
        ordering = ['-created_date']


class OptionsList(admin.ModelAdmin):
    list_display = (
        'id', 'mc_answer_index', 'mc_english_options',
        'mc_id', 'created_date', 'updated_date')


class ShortQuestion(models.Model):

    sq_sequence = models.IntegerField(blank=False, null=True)
    theme_id = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, blank=True)
    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    learning_focus_id = models.ForeignKey(Learningfocus, on_delete=models.CASCADE, null=True, blank=True)

    sq_english_source_ref = models.TextField(blank=True, null=True)
    sq_chinese_source_ref = models.TextField(blank=True, null=True)
    sq_english_source_details = models.TextField(blank=True, null=True)
    sq_chinese_source_details = models.TextField(blank=True, null=True)

    sq_english_question = models.TextField(blank=False, null=True)
    sq_chinese_question = models.TextField(blank=False, null=True)
    sq_english_question_bookmark = models.TextField(blank=False, null=True)
    sq_chinese_question_bookmark = models.TextField(blank=False, null=True)

    sq_english_suggested_answer = models.TextField(blank=False, null=True)
    sq_chinese_suggested_answer = models.TextField(blank=False, null=True)

    sq_total_mark = models.FloatField(blank=False, null=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.sq_english_source_ref)

    @property
    def full_name(self):
        return '%s' % str(self.sq_english_source_ref)

    @property
    def show_name(self):
        return '%s' % str(self.sq_english_source_ref)

    class Meta:
        ordering = ['-created_date']


class ShortQuestionList(admin.ModelAdmin):
    list_display = (
        'id', 'sq_english_source_ref', 'theme_id', 'topic_id',
        'learning_focus_id', 'sq_english_source_details',
        'sq_english_question_bookmark', 'sq_chinese_question_bookmark',
        'sq_english_question', 'sq_english_suggested_answer',
        'created_date', 'updated_date')


class ShortQuestionMarkPoints(models.Model):

    sq_id = models.ForeignKey(ShortQuestion, on_delete=models.CASCADE, null=True, blank=True)
    sq_english_mark_points = models.CharField(max_length=500, blank=False, null=True)
    sq_chinese_mark_points = models.CharField(max_length=500, blank=False, null=True)
    sq_english_mark = models.IntegerField(blank=False, null=True)
    sq_chinese_mark = models.IntegerField(blank=False, null=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.sq_english_mark_points)

    @property
    def full_name(self):
        return '%s' % str(self.sq_english_mark_points)

    @property
    def show_name(self):
        return '%s' % str(self.sq_english_mark_points)

    class Meta:
        ordering = ['-created_date']


class ShortQuestionMarkPointsList(admin.ModelAdmin):
    list_display = (
        'id', 'sq_english_mark_points', 'sq_chinese_mark_points',
        'sq_id', 'created_date', 'updated_date', 'sq_english_mark', 'sq_chinese_mark'
    )


class ThemeUsage(models.Model):

    theme_id = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, blank=True)
    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    user_id = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_user_id = models.ForeignKey(DeletedUsers, null=True, blank=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_date']


class ThemeUsageList(admin.ModelAdmin):
    list_display = (
        'id', 'theme_id', 'topic_id',
        'user_id', 'deleted_user_id', 'created_date', 'updated_date',
    )


admin.site.register(Theme, ThemeList)
admin.site.register(Topic, TopicList)
admin.site.register(Cards, CardList)
admin.site.register(Cardstitle, CardTitleList)
admin.site.register(Learningfocus, LearningfocusList)
admin.site.register(MC, MCList)
admin.site.register(McOptions, OptionsList)
admin.site.register(ShortQuestion, ShortQuestionList)
admin.site.register(ShortQuestionMarkPoints, ShortQuestionMarkPointsList)
admin.site.register(ThemeUsage, ThemeUsageList)
admin.site.register(UserLearningCardData, UserLearningCardDataList)
