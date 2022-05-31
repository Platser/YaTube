import datetime
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


def check_context(parrent, page, response):
    if 'context_equal' in page:
        for name, value in page['context_equal'].items():
            parrent.assertEqual(response.context[name], value)
    if 'context_is_instance' in page:
        for name, value in page['context_is_instance'].items():
            parrent.assertIsInstance(response.context[name], value)
    if 'context_query_set' in page:
        for name, value in page['context_query_set'].items():
            parrent.assertQuerysetEqual(response.context[name], value)


class PostCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')

    def setUp(self):
        self.guest_client = Client()

    def test_index_cache(self):
        post = Post.objects.create(
            text='Тестовый пост',
            author=PostCacheTest.author,
        )
        response1 = self.guest_client.get(reverse('posts:index'))
        Post.objects.filter(pk=post.pk).delete()
        response2 = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response1.content, response2.content)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Группы для тестов
        cls.group = Group.objects.create(
            title='Test Group 1',
            slug='group1',
            description='Группа для тестов'
        )
        cls.group2 = Group.objects.create(
            title='Test Group 2',
            slug='group2',
            description='Группа для тестов'
        )
        # Авторизованный пользователь для тестов
        cls.author1 = User.objects.create_user(username='author1')
        # Пост для тестов
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author1,
            group=cls.group,
            image='posts/' + cls.uploaded.name
        )
        cls.comment_form = CommentForm()
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author1,
            text='Комментарий'
        )
        cls.test_date = datetime.datetime.now().date()
        cls.pages = (
            {
                'url': reverse('posts:index'),
                'type': 'post_list',
                'context_query_set': {
                    'page_obj': [repr(cls.post)]
                },
                'template': 'posts/index.html'
            },
            {
                'url': reverse('posts:group_list', kwargs={'slug': 'group1'}),
                'context_equal': {
                    'group': cls.group
                },
                'context_query_set': {
                    'page_obj': [repr(cls.post)]
                },
                'type': 'post_list',
                'template': 'posts/group_list.html'
            },
            {
                'url': reverse(
                    'posts:profile',
                    kwargs={'username': 'author1'}
                ),
                'context_equal': {
                    'author': cls.author1
                },
                'context_query_set': {
                    'page_obj': [repr(cls.post)]
                },
                'type': 'post_list',
                'template': 'posts/profile.html'
            },
            {
                'url': reverse(
                    'posts:post_detail',
                    kwargs={'post_id': cls.post.pk}
                ),
                'context_equal': {
                    'post': cls.post,
                },
                'context_query_set': {
                    'comments': [repr(cls.comment)]
                },
                'context_is_instance': {
                    'form': CommentForm
                },
                'type': 'post_detail',
                'template': 'posts/post_detail.html'
            },
            {
                'url': reverse(
                    'posts:post_edit',
                    kwargs={'post_id': cls.post.pk}
                ),
                'context_equal': {
                    'is_edit': True,
                },
                'context_is_instance': {
                    'form': PostForm
                },
                'type': 'post_create',
                'template': 'posts/create_post.html'
            },
            {
                'url': reverse('posts:post_create'),
                'context_is_instance': {
                    'form': PostForm
                },
                'type': 'post_create',
                'template': 'posts/create_post.html'
            },
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostsPagesTests.author1)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for page in PostsPagesTests.pages:
            with self.subTest(url=page['url']):
                response = self.author_client.get(page['url'])
                self.assertTemplateUsed(response, page['template'])

    def test_post_list_context(self):
        """
        Шаблоны отображающие списки постов сформированы с правильным
        контекстом.
        """
        for page in (p for p in PostsPagesTests.pages
                     if p['type'] == 'post_list'):
            with self.subTest(url=page['url']):
                response = self.author_client.get(page['url'])
                check_context(self, page, response)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.author, PostsPagesTests.author1)
                self.assertEqual(first_object.pub_date.date(),
                                 PostsPagesTests.test_date)
                self.assertEqual(first_object.text, 'Тестовый пост')
                self.assertEqual(first_object.group, PostsPagesTests.group)
                self.assertEqual(first_object.image,
                                 'posts/' + PostsPagesTests.uploaded.name)

    def test_post_detail_context(self):
        """Шаблоны post_detail сформированы с правильным контекстом."""
        for page in (p for p in PostsPagesTests.pages
                     if p['type'] == 'post_detail'):
            with self.subTest(url=page['url']):
                response = self.author_client.get(page['url'])
                check_context(self, page, response)
                post = response.context['post']
                comment = response.context['comments'][0]
                # Проверяем контент поста
                self.assertEqual(post.author, PostsPagesTests.author1)
                self.assertEqual(post.pub_date.date(),
                                 PostsPagesTests.test_date)
                self.assertEqual(post.text, 'Тестовый пост')
                self.assertEqual(post.group, PostsPagesTests.group)
                self.assertEqual(post.image,
                                 'posts/' + PostsPagesTests.uploaded.name)
                # Прверяем контент комментария
                self.assertEqual(comment.text, PostsPagesTests.comment.text)
                self.assertEqual(comment.author,
                                 PostsPagesTests.comment.author)
                self.assertEqual(comment.post,
                                 post)
                self.assertEqual(comment.created,
                                 PostsPagesTests.comment.created)

    def test_create_and_edit_post_page_show_correct_context(self):
        """
        Шаблоны post_create и post_edit сформирован с правильным контекстом.
        """
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField
        }
        for page in (p for p in PostsPagesTests.pages
                     if p['type'] == 'post_create'):
            with self.subTest(url=page['url']):
                response = self.author_client.get(page['url'])
                check_context(self, page, response)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get('form').fields.get(
                            value)
                        self.assertIsInstance(form_field, expected)

    def test_group2_has_no_posts(self):
        """group2 не содержит постов."""
        response = self.author_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'group2'}
            )
        )
        self.assertEqual(response.context['group'], PostsPagesTests.group2)
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Группа для тестов
        cls.group_slug = 'testslug'
        group = Group.objects.create(
            title='Test Group',
            slug=cls.group_slug,
            description='Группа для тестов'
        )
        # пользователи для тестов
        author1 = User.objects.create_user(username='author1')
        author2 = User.objects.create_user(username='author2')
        # Посты для тестов
        posts = [
            Post(
                text=f'Тестовый пост №{i}',
                author=author1,
                group=group
            ) for i in range(1, 18)
        ]
        posts[-1].author = author2
        posts[-1].group = None
        posts[-2].group = None
        Post.objects.bulk_create(posts)
        cls.pages = (
            {
                'url': reverse('posts:index'),
                'posts_num': 7
            },
            {
                'url': reverse(
                    'posts:group_list',
                    kwargs={'slug': cls.group_slug}
                ),
                'posts_num': 5
            },
            {
                'url': reverse(
                    'posts:profile',
                    kwargs={'username': 'author1'}
                ),
                'posts_num': 6
            },
        )

    def setUp(self):
        self.client = Client()

    def test_paginator(self):
        for page in PaginatorViewsTest.pages:
            with self.subTest(url=page['url']):
                response = self.client.get(page['url'])
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.client.get(page['url'], {'page': '2'})
                self.assertEqual(
                    len(response.context['page_obj']),
                    page['posts_num']
                )
