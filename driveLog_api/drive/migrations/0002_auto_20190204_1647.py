# Generated by Django 2.1.5 on 2019-02-04 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='logUUID',
        ),
        migrations.AddField(
            model_name='log',
            name='completion',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
