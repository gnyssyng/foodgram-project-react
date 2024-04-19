# Generated by Django 3.2.16 on 2024-03-31 12:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_auto_20240330_1409'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-id']},
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0, 'Неккореткное количество ингредиента.Количество должно быть больше 0.')], verbose_name='Количество'),
        ),
    ]
