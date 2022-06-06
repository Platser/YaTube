# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)


TODO:
    Разобраться: return redirect(request.META.get('HTTP_REFERER')) - возврат на предыдущёю страницу приводит к ошибкам во view-тестах:
        ======================================================================
        ERROR: test_subscribe_unsubscribe (posts.tests.test_views.PostsPagesTests)
        Пользователь может подписаться и отписаться на/от автора
        ----------------------------------------------------------------------
        Traceback (most recent call last):
        File "C:\projects\hw05_final\venv\lib\site-packages\django\shortcuts.py", line 148, in resolve_url
            return reverse(to, args=args, kwargs=kwargs)
        File "C:\projects\hw05_final\venv\lib\site-packages\django\urls\base.py", line 90, in reverse
            return iri_to_uri(resolver._reverse_with_prefix(view, prefix, *args, **kwargs))
        File "C:\projects\hw05_final\venv\lib\site-packages\django\urls\resolvers.py", line 673, in _reverse_with_prefix
            raise NoReverseMatch(msg)
        django.urls.exceptions.NoReverseMatch: Reverse for 'None' not found. 'None' is not a valid view function or pattern name.


Questions:

Дмитрий, добрый день!
Есть следующие воросы пр ревью:
1) Добавить cache.clear() в setUp() тестов.
   При добавлении cache.clear() любой из классов unittest, возникают ошибки  FileNotFoundError для тестойво картинки small.gif. Видимо SimpleUploadedFile и LocMemCache как-то связаны. Вместо этого использовал clear_posts_cache() из posts/views.py, которая удаляет кэш страниц "прицельно" по ключу.