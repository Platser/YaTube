import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test Group 1',
            slug='group1',
            description='Группа для тестов'
        )
        cls.group_2 = Group.objects.create(
            title='Test Group 2',
            slug='group2',
            description='Группа для тестов'
        )
        cls.author1 = User.objects.create_user(username='author1')
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
        cls.uploaded_new = SimpleUploadedFile(
            name='small_new.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostsCreateFormTests.author1)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': PostsCreateFormTests.group.pk,
            'image': PostsCreateFormTests.uploaded
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': 'author1'}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/' + PostsCreateFormTests.uploaded.name
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменияет запись в Post."""
        post = Post.objects.create(
            text='Тестовый пост 2',
            author=self.author1,
            group=PostsCreateFormTests.group,
            image='posts/' + PostsCreateFormTests.uploaded.name
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный текст',
            'group': PostsCreateFormTests.group_2.pk,
            'image': PostsCreateFormTests.uploaded_new
        }
        response = self.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.pk}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.first().text, form_data['text'])
        self.assertEqual(Post.objects.first().group,
                         PostsCreateFormTests.group_2)
        self.assertEqual(Post.objects.first().image,
                         'posts/' + PostsCreateFormTests.uploaded_new.name)
