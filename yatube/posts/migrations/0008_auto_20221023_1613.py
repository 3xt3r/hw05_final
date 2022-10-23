# Generated by Django 2.2.16 on 2022-10-23 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20221022_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(help_text='Заполните комментарий', verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации'),
        ),
    ]
