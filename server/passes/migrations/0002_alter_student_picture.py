# Generated by Django 4.2.6 on 2023-11-04 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='picture',
            field=models.CharField(max_length=60),
        ),
    ]
