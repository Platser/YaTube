from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель группы записей сообщества"""
    title = models.CharField("Название группы", max_length=200,
                             help_text="Не более 200 символов")
    slug = models.SlugField("slug для url адреса группы", unique=True)
    description = models.TextField("Описание группы")

    class Meta:
        verbose_name = "Группа записей"
        verbose_name_plural = "Группы записей"

    def __str__(self):
        """Возвращает название группы"""
        return self.title


class Post(models.Model):
    """Модель записи, создаваемой пользователем в сообществе"""
    text = models.TextField(
        'Текст записи',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name="Группа",
        help_text='Группа, к которой будет относится пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = "Запись"
        verbose_name_plural = "Записи"

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        "Дата публикации комментария",
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ('user__username', 'author__username')

    def __str__(self):
        return f'{self.user.username} follows {self.author.username}'
