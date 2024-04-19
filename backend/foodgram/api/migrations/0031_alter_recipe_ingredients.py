# Generated by Django 3.2.16 on 2024-04-08 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_auto_20240331_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='ingredients', through='api.IngredientInRecipe', to='api.Ingredient'),
        ),
    ]
