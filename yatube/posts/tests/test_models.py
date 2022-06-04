from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Описание тестовой группы'
        )

    def test_str(self):
        """Проверяем, что у модели корректно работает __str__."""
        group = GroupModelTest.group
        self.assertEqual(str(group), 'Тестовая группа')

    def test_meta(self):
        group = GroupModelTest.group
        self.assertEqual(group._meta.verbose_name.title(), 'Группа Записей')
        self.assertEqual(group._meta.verbose_name_plural.title(),
                         'Группы Записей')

    def test_field_verbose_name(self):
        fields_dict = {
            'title': 'Название группы',
            'slug': 'slug для url адреса группы',
            'description': 'Описание группы',
        }
        group = GroupModelTest.group
        for field_name, verbose_name in fields_dict.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    group._meta.get_field(field_name).verbose_name,
                    verbose_name
                )

    def test_field_help_text(self):
        fields_dict = {
            'title': 'Не более 200 символов',
        }
        group = GroupModelTest.group
        for field_name, help_text in fields_dict.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    group._meta.get_field(field_name).help_text,
                    help_text
                )


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Описание тестовой группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост ' + '.' * 100,
            group=cls.group
        )

    def test_str(self):
        """Проверяем, что у модели корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(str(post), post.text[:15])

    def test_meta(self):
        post = PostModelTest.post
        self.assertEqual(post._meta.verbose_name.title(),
                         'Запись')
        self.assertEqual(post._meta.verbose_name_plural.title(),
                         'Записи')

    def test_field_verbose_name(self):
        fields_dict = {
            'text': 'Текст записи',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        post = PostModelTest.post
        for field_name, verbose_name in fields_dict.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    post._meta.get_field(field_name).verbose_name,
                    verbose_name
                )

    def test_field_help_text(self):
        fields_dict = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относится пост',
        }
        post = PostModelTest.post
        for field_name, help_text in fields_dict.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    post._meta.get_field(field_name).help_text,
                    help_text
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Описание тестовой группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост ' + '.' * 100,
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Комментарий'
        )

    def test_str(self):
        """Проверяем, что у модели корректно работает __str__."""
        comment = CommentModelTest.comment
        self.assertEqual(str(comment), comment.text[:15])

    def test_meta(self):
        comment = CommentModelTest.comment
        self.assertEqual(comment._meta.verbose_name.title(),
                         'Комментарий')
        self.assertEqual(comment._meta.verbose_name_plural.title(),
                         'Комментарии')

    def test_field_verbose_name(self):
        fields_dict = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата публикации комментария',
        }
        comment = CommentModelTest.comment
        for field_name, verbose_name in fields_dict.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    comment._meta.get_field(field_name).verbose_name,
                    verbose_name
                )

    def test_field_help_text(self):
        fields_dict = {
            'text': 'Введите текст комментария',
        }
        comment = CommentModelTest.comment
        for field_name, help_text in fields_dict.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    comment._meta.get_field(field_name).help_text,
                    help_text
                )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='reader')
        cls.author = User.objects.create_user(username='writer')
        cls.follow = Follow.objects.create(user=cls.user, author=cls.author)

    def test_str(self):
        self.assertEqual(str(FollowModelTest.follow), 'reader follows writer')
