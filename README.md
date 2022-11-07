# YaTube
## Революционная социальная сеть следующего поколения

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

YaTube - web-приложение реализующее социальную сеть, позволяющее пользователям вести дневники, подписываться друг на друга и оставлять комментарии.

### Возможности
* Регистрация, аутентификация и управление учётной записью
* Создание записей (постов) пользователя с возможностью загрузки изображения
* Создания комментарием к постам пользователей
* Подписка на записи выбранных авторов
* Реализованы кеширование и паджинация

### Технологии
* Python 3.7
* Django 2.2.16
* SQLite

### Как запустить проект
Склонировать из репозитория, затем перейти в каталог:

```
git clone git@github.com:Platser/YaTube.git
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate (или .\venv\scripts\activate для Windows)
```
Обновить pip:
```
python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Перейти в директорию с manage.py:
```
cd yatube
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
