# Generated by Django 4.2.6 on 2023-10-30 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IssuedPass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roll_no', models.CharField(max_length=11)),
                ('issues_date', models.IntegerField(verbose_name='Unix time stamp of issued date.')),
                ('valid_till', models.IntegerField(verbose_name='Unix time stamp of expiry date.')),
                ('pass_type', models.CharField(choices=[('one_time', 'one_time'), ('daily', 'daily'), ('alumni', 'alumni')], max_length=10)),
            ],
        ),
    ]
