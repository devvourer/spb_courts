# Generated by Django 4.1.2 on 2022-10-20 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jurisdiction',
            name='end_house_number',
            field=models.PositiveSmallIntegerField(default=2000, verbose_name='номер дома конца интервала'),
        ),
        migrations.AlterField(
            model_name='jurisdiction',
            name='house_number',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='номер дома, если в подсудность входят единичные дома'),
        ),
        migrations.AlterField(
            model_name='jurisdiction',
            name='start_house_number',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='номер дома начала интервала'),
        ),
    ]
