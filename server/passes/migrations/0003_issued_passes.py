# Generated by Django 4.2.6 on 2023-10-30 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passes', '0002_issued_passes'),
    ]

    operations = [
        migrations.CreateModel(
            name='LunchTiming',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('opening_time', models.CharField(max_length=10)),
                ('closing_time', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'lunch_timings',
            },
        ),
        migrations.AlterModelTable(
            name='issuedpass',
            table='issued_pass',
        ),
    ]
