# Generated by Django 3.2.14 on 2022-07-06 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_rename_user_newuser'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NewUser',
        ),
    ]
