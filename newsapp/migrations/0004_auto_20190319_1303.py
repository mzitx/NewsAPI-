# Generated by Django 2.1.7 on 2019-03-19 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsapp', '0003_news_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
