# Generated by Django 2.1.5 on 2019-01-24 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0002_auto_20190123_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shareusers',
            name='authority',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
