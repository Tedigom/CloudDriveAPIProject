# Generated by Django 2.1.5 on 2019-01-30 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0004_auto_20190130_1624'),
    ]

    operations = [
        migrations.CreateModel(
            name='FailedLog',
            fields=[
                ('logID', models.AutoField(primary_key=True, serialize=False)),
                ('logContents', models.TextField()),
            ],
        ),
    ]
