import csv

from api.models import Ingredient

MODELS_PATHS = {
    Ingredient: 'data/ingredients.csv',
}

FIELDS = ()


def key_to_id(key):
    '''Добавляет префикс _id для ключей словаря со внешним ключом.'''
    return f'{key}_id' if (key in FIELDS) and not key.endswith('id') else key


def value_to_int(key, value):
    '''Переводит ключи словаря в целочисленное значение.'''
    return int(value) if key in FIELDS else value


def run():
    '''Импортирует данные из csv файлов в базу данных.'''
    for model in MODELS_PATHS:
        model.objects.all().delete()
        with open(MODELS_PATHS[model], encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                new_row = {
                    key_to_id(key):
                    value_to_int(key, value) for key, value in row.items()
                }
                print(new_row)
                model.objects.get_or_create(**new_row)
