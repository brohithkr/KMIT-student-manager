# Generated by Django 4.2.6 on 2023-10-30 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Latecomers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roll_no', models.CharField(max_length=11)),
                ('date', models.IntegerField()),
            ],
            options={
                'db_table': 'latecomers',
            },
        ),
    ]
