# Generated by Django 4.2.6 on 2023-12-18 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passes', '0003_alter_student_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Logging',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.BigIntegerField(verbose_name='Unix time stamp of moment scan was done.')),
                ('roll_no', models.CharField(max_length=11)),
            ],
        ),
    ]
