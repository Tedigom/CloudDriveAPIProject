# Generated by Django 2.1.5 on 2019-02-03 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('logID', models.AutoField(primary_key=True, serialize=False)),
                ('logUUID', models.CharField(max_length=499)),
                ('logDateTime', models.DateTimeField()),
                ('logContents', models.TextField()),
            ],
        ),
    ]
