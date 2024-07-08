from rest_framework import serializers
from theme.models import Theme
from theme.models import Topic
from theme.models import Cards
from theme.models import Cardstitle
from theme.models import MC
from theme.models import ShortQuestion
from theme.models import McOptions
from theme.models import Learningfocus
from theme.models import ShortQuestionMarkPoints
from theme. models import ThemeUsage
from theme. models import UserLearningCardData

from rest_framework.validators import UniqueValidator
# from django.contrib.accounts.models import user


class ThemeSerializerPut(serializers.ModelSerializer):

    class Meta:
        model = Theme
        fields = (
            'id', 'theme_english_name', 'theme_chinese_name', 'theme_image', 'theme_color', 'theme_number',
            'english_tag', 'chinese_tag', 'created_date', 'updated_date')


class ThemeSerializer(serializers.ModelSerializer):

    theme_english_name = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Theme.objects.all())])
    theme_chinese_name = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Theme.objects.all())])
    # theme_color = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Theme.objects.all())])

    def create(self, validated_data):
        last_id = None
        if not validated_data.get('id'):
            try:
                last_id = self.sequence_next()
            except:
                last_id = 1
            validated_data['theme_number'] = 'TH0'+str(last_id)
        theme = Theme(**validated_data)
        theme.save()
        return theme

    def sequence_next(self):
        if Theme.objects.all().last():
            return Theme.objects.all().last().id + 1;
        else:
            return 1
    class Meta:
        model = Theme
        fields = (
            'id', 'theme_english_name', 'theme_chinese_name', 'theme_image', 'theme_color', 'theme_number', 'english_tag',
            'chinese_tag', 'created_date', 'updated_date')


class ThemeSerializerGet(serializers.ModelSerializer):

    class Meta:
        model = Theme
        fields = (
            'id', 'theme_english_name', 'theme_chinese_name', 'theme_image', 'theme_color', 'theme_number',
            'english_tag', 'chinese_tag', 'created_date', 'updated_date')


class TopicSerializer(serializers.ModelSerializer):

    topic_chinese_name = serializers.CharField(required=True)
    topic_english_name = serializers.CharField(required=True)
    # learning_focus = serializers.CharField(required=True)

    def create(self, validated_data):
        topic = Topic(**validated_data)
        topic.save()
        # topics = Topic.objects.all()
        # seq = 1
        # for topic in topics:
        #     topic.sequence = seq
        #     topic.save()
        #     seq = seq + 1
        return topic

    class Meta:
        model = Topic
        fields = (
            'id', 'theme_id', 'topic_english_name', 'topic_chinese_name', 'learning_focus', 'created_date',
            'updated_date', 'english_tag', 'chinese_tag', 'sequence')


class TopicSerializerGet(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = (
            'id', 'theme_id', 'topic_english_name', 'topic_chinese_name', 'learning_focus', 'created_date',
            'updated_date')


class LearningFocusSerializer(serializers.ModelSerializer):

    english = serializers.CharField(required=True)
    chinese = serializers.CharField(required=True)

    # learning_focus = serializers.CharField(required=True)

    def create(self, validated_data):
        topic = Learningfocus(**validated_data)
        topic.save()
        return topic

    class Meta:
        model = Learningfocus
        fields = (
            'id', 'english','chinese','topic_id', 'created_date', 'updated_date')


class LearningFocusSerializerUpdate(serializers.ModelSerializer):

    class Meta:
        model = Learningfocus
        fields = (
            'id', 'english','chinese','topic_id', 'created_date', 'updated_date')


class CardsSerializer(serializers.ModelSerializer):

    # card_content = serializers.CharField(required=True)
    # card_english_topic = serializers.CharField(required=True)
    # card_chinese_topic = serializers.CharField(required=True)
    # card_hints = serializers.CharField(required=True)

    def create(self, validated_data):
        last_id = None
        try:
            last_id = self.sequence_next()
        except:
            last_id = 1
        validated_data['card_number'] = 'CA0' + str(last_id)
        cards = Cards(**validated_data)
        cards.save()
        return cards

    def sequence_next(self):
        if Cards.objects.all().last():
            return Cards.objects.latest('id').id + 1;
        else:
            return 1

    class Meta:
        model = Cards
        fields = (
            'id', 'card_title_id', 'card_english_summary_title',
            'card_chinese_summary_title',
            'card_english_summary',
            'card_chinese_summary',
            'created_date', 'updated_date')


class CardsSerializerGet(serializers.ModelSerializer):

    class Meta:
        model = Cards
        fields = (
            'id', 'card_title_id', 'card_english_summary_title',
            'card_chinese_summary_title', 'card_english_summary',
            'card_chinese_summary',
            'created_date', 'updated_date')


class CardstitleSerializer(serializers.ModelSerializer):

    # card_content = serializers.CharField(required=True)
    # card_english_topic = serializers.CharField(required=True)
    # card_chinese_topic = serializers.CharField(required=True)
    # card_hints = serializers.CharField(required=True)

    def create(self, validated_data):
        last_id = None
        try:
            last_id = self.sequence_next()
        except:
            last_id = 1
        validated_data['card_title_number'] = 'CT0' + str(last_id)
        cardstitle = Cardstitle(**validated_data)
        cardstitle.save()
        return cardstitle

    def sequence_next(self):
        if Cardstitle.objects.all().last():
            return Cardstitle.objects.latest('id').id + 1;
        else:
            return 1

    class Meta:
        model = Cardstitle
        fields = (
            'id', 'topic_id', 'theme_id', 'card_english_title',
            'card_chinese_title', 'card_english_subtitle',
            'card_thumbnail_background', 'card_full_background',
            'card_chinese_subtitle', 'card_title_number',
            'created_date', 'updated_date')


class CardstitleSerializerGet(serializers.ModelSerializer):

    class Meta:
        model = Cardstitle
        fields = (
            'id', 'topic_id', 'theme_id', 'card_english_title', 'card_chinese_title', 'card_english_subtitle',
            'card_chinese_subtitle', 'card_title_number',
            'created_date', 'updated_date')


class CardstitleSerializerUpdate(serializers.ModelSerializer):
    # topic_id = serializers.IntegerField(required=False)
    # theme_id = serializers.IntegerField(required=False)
    card_thumbnail_background = serializers.ImageField(required=False)
    card_full_background = serializers.ImageField(required=False)

    class Meta:
        model = Cardstitle
        fields = (
            'id', 'topic_id', 'theme_id', 'card_thumbnail_background', 'card_full_background')


class TopicSerializerUpdate(serializers.ModelSerializer):

    # topic_chinese_name = serializers.CharField(required=True)
    # topic_english_name = serializers.CharField(required=True)
    # learning_focus = serializers.CharField(required=True)

    def create(self, validated_data):
        topic = Topic(**validated_data)
        topic.save()
        # topics = Topic.objects.all()
        # seq = 1
        # for topic in topics:
        #     topic.sequence = seq
        #     topic.save()
        #     seq = seq + 1

        return topic

    class Meta:
        model = Topic
        fields = (
            'id', 'theme_id', 'topic_english_name', 'topic_chinese_name', 'learning_focus', 'created_date',
            'updated_date')


class MCSerializer(serializers.ModelSerializer):

    class Meta:
        model = MC
        fields = (
            'id', 'theme_id', 'topic_id', 'learning_focus_id',
            'mc_english_source_ref', 'mc_chinese_source_ref',
            'mc_english_source_details', 'mc_chinese_source_details',
            'mc_english_question', 'mc_chinese_question',
            'mc_english_question_bookmark', 'mc_chinese_question_bookmark',
            'answer', 'mark', 'total_mark', 'no_of_respondents',
            'created_date', 'updated_date')


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = McOptions
        fields = (
            'id', 'mc_english_options',
            'mc_chinese_options', 'mc_answer_index',
            'mc_id', 'created_date', 'updated_date')


class SQSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShortQuestion
        fields = '__all__'


class MarkPointsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShortQuestionMarkPoints
        fields = '__all__'


class ThemeUsage(serializers.ModelSerializer):

    class Meta:
        model = ThemeUsage
        fields = '__all__'


class UserLearningCardDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLearningCardData
        fields = '__all__'
