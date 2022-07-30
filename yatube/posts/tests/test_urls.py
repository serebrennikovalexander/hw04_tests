from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя, который будет авторизован
        cls.test_user = User.objects.create_user(username='test')
        # Создаем пользователя, который будет автором поста
        cls.author_user = User.objects.create_user(username='auth')
        # Создаем группу
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Создаем пост
        cls.post = Post.objects.create(
            author=cls.author_user,
            text='Тест.' * 20,
            group=cls.group,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.test_user = PostsURLTests.test_user
        self.test_client = Client()
        self.test_client.force_login(self.test_user)
        # Создаем клиент для автора поста
        self.author_user = PostsURLTests.author_user
        self.author_client = Client()
        self.author_client.force_login(self.author_user)
        # URL-адреса
        self.url_index = '/'
        self.url_group_list = f'/group/{PostsURLTests.group.slug}/'
        self.url_profile = f'/profile/{PostsURLTests.author_user.username}/'
        self.url_post_detail = f'/posts/{PostsURLTests.post.id}/'
        self.url_post_edit = f'/posts/{PostsURLTests.post.id}/edit/'
        self.url_post_create = '/create/'
        self.url_unexisting_page = '/unexisting_page/'

    # Проверяем доступность страниц для неавторизованного пользователя
    def test_homepage_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(self.url_index)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_list_url_exists_at_desired_location(self):
        """Страница /group/slug/ доступна любому пользователю."""
        response = self.guest_client.get(self.url_group_list)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /pfofile/username/ доступна любому пользователю."""
        response = self.guest_client.get(self.url_profile)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_url_exists_at_desired_location(self):
        """Страница /posts/post_id/ доступна любому пользователю."""
        response = self.guest_client.get(self.url_post_detail)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_not_found(self):
        """Страница /unexisting_page/ не найдена."""
        response = self.guest_client.get(self.url_unexisting_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_create_post_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.test_client.get(self.url_post_create)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем доступность страниц для автора пользователя
    def test_edit_post_url_exists_at_desired_location(self):
        """Страница /posts/post_id/edit/ доступна только автору поста."""
        response = self.author_client.get(self.url_post_edit)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы для неавторизованного пользователя
    def test_edit_post_url_redirect_anonymous_user_on_admin_login(self):
        """Страница /posts/post_id/edit/ перенаправляет анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(self.url_post_edit, follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next={self.url_post_edit}'
        )

    def test_create_post_url_redirect_anonymous_user_on_admin_login(self):
        """Страница /create/ перенаправляет анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(self.url_post_create, follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next={self.url_post_create}'
        )

    # Проверяем редирект для авторизованного пользователя, но не автора поста
    def test_edit_post_url_redirect_authorized_user(self):
        """Страница /posts/post_id/edit/ перенаправляет авторизованного
        пользователя, который не является автором поста,
        на станицу /posts/post_id/.
        """
        response = self.test_client.get(self.url_post_edit, follow=True)
        self.assertRedirects(
            response, self.url_post_detail
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Проверка происходит с помощью клиента для автора поста.
        """
        # Шаблоны по адресам
        templates_url_names = {
            self.url_index: 'posts/index.html',
            self.url_group_list: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_post_detail: 'posts/post_detail.html',
            self.url_post_edit: 'posts/create_post.html',
            self.url_post_create: 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
