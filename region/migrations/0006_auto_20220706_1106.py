# Generated by Django 3.2.14 on 2022-07-06 11:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('region', '0005_auto_20220706_1104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newusers',
            name='authentication_id',
        ),
        migrations.RemoveField(
            model_name='newusers',
            name='profile_id',
        ),
        migrations.RemoveField(
            model_name='newusers',
            name='role_id',
        ),
        migrations.RemoveField(
            model_name='newusers',
            name='school_id',
        ),
    ]
