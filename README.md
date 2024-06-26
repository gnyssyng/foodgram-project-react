![status badge](https://github.com/gnyssyng/foodgram-project-react/actions/workflows/main.yml/badge.svg)

[Ссылка на проект](https://foodie.myvnc.com/)
[Ссылка на документацию](https://foodie.myvnc.com/api/docs)
#  Foodgram
Foodgram - это социальная сеть, целью которой является создание и обмен рецеатми различных блюд.
В его функционал входит:
- возможность создания рецептов с фотографиями;
- подписка на авторов рецептов;
- создание и скачивание продуктовой корзины;
- добавление рецептов в избранное;
- и многое другое.

# Используемые технологии
Python 3, Django 3.2, Django REST Framework, Djoser, Postgres, GIT

# Как развернуть проект

Склонировать на локальный компьютер (напримере, при помощи git clone, используя SSH) и установить виртуальное окружение.
```
git clone git@github.com:gnyssyng/foodgram-project-react.git
```

В проекте также предусмотрена возможность загрузки ингредиентов при помощи скрипта.
Для этого необходимо из папки с файлом manage.py выполнить следующую команду:
```
python manage.py runscript load_data
```
Данные хранятся в data. Они предоставлены в виде CSV-файла и JSON, однако скрипт использует CSV.

## В дериктории проекта выполнить команду:
Для Linux И MacOs:

```
python3 -m venv .venv
```

Для Windows:

```
python -m venv .venv
```

## И установить зависимости из файла requirements.txt при активированном окружении
Для Linux И MacOs:

```
source .venv/bin/activate
```

Для Windows:

```
source .venv/Scripts/activate
pip install -r requirements.txt
```

# Как заполнить файл .env
## Проект используется библиотеку python-dotenv для передачи переменных окружения в исполняемый код проекта.
Для корректной работы необходимо создать файл .env и заполнить его соответсвенно. 
В проекте используются следующие переменные окружения:

```yaml
POSTGRES_DB=имя_базы_данных 
POSTGRES_USER=имя_пользователя_в_базе_данных
POSTGRES_PASSWORD=пароль_пользователя_в_базе_данных
DB_NAME=имя_базы_данных
DEBUG=булево значение для определения режима debug, записывается как False или True
ALLOWED_HOSTS=список разрешенных хостов, которые должны быть разделены пробелом.
SECRET_KEY=секретный_ключ_Django
```

Автор: Колбун Данила, gnyssyng
