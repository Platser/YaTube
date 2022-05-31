from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test Group',
            slug='testslug',
            description='Группа для тестов'
        )
        cls.author = User.objects.create_user(username='author')
        cls.not_author = User.objects.create_user(username='not_author')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
        )
        cls.guest_urls = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
        }
        cls.author_urls = {
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
        }
        cls.authorized_urls = {
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/comment/': None,
        }
        cls.not_guest_urls = {**cls.author_urls, **cls.authorized_urls}
        cls.all_urls = {
            **cls.guest_urls,
            **cls.author_urls,
            **cls.authorized_urls,
        }

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(PostsURLTests.author)
        self.not_author_client = Client()
        self.not_author_client.force_login(PostsURLTests.not_author)

    # Проверяем доступность страниц
    def test_url_guest_access(self):
        for address in PostsURLTests.guest_urls.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_not_author_cant_edit(self):
        for address in PostsURLTests.author_urls.keys():
            with self.subTest(address=address):
                response = self.not_author_client.get(address)
                self.assertRedirects(
                    response,
                    (f'/posts/{PostsURLTests.post.pk}/')
                )

    def test_guest_redirect_to_login(self):
        for address in PostsURLTests.not_guest_urls.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(
                    response,
                    (f'/auth/login/?next={address}')
                )

    # Проверяем используемые шаблоны страниц
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        for address, template in PostsURLTests.all_urls.items():
            if template is not None:
                with self.subTest(address=address):
                    response = self.author_client.get(address)
                    self.assertTemplateUsed(response, template)
