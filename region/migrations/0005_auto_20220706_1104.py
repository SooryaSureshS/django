# Generated by Django 3.2.14 on 2022-07-06 11:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('region', '0004_address_user_profile_user_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_profile',
            name='user_id',
        ),
        migrations.RemoveField(
            model_name='user_role',
            name='user_id',
        ),
        migrations.CreateModel(
            name='NewUsers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('authentication_id', models.IntegerField()),
                ('uid', models.UUIDField(blank=True, default=None, null=True, unique=True)),
                ('address_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='region.address')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('profile_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='region.user_profile')),
                ('role_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='region.user_role')),
                ('school_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='region.school')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
