from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


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

    # Проверяем доступность страниц для неавторизованного пользователя
    def test_homepage_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_list_url_exists_at_desired_location(self):
        """Страница /group/slug/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsURLTests.group.slug}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /pfofile/username/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostsURLTests.author_user.username}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_url_exists_at_desired_location(self):
        """Страница /posts/post_id/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsURLTests.post.id}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_not_found(self):
        """Страница /unexisting_page/ не найдена."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_create_post_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.test_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем доступность страниц для автора пользователя
    def test_edit_post_url_exists_at_desired_location(self):
        """Страница /posts/post_id/edit/ доступна только автору поста."""
        response = self.author_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLTests.post.id}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы для неавторизованного пользователя
    def test_edit_post_url_redirect_anonymous_user_on_admin_login(self):
        """Страница /posts/post_id/edit/ перенаправляет анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLTests.post.id}
            ), follow=True
        )
        self.assertRedirects(
            response,
            (reverse('users:login')
             + "?next="
             + reverse('posts:post_edit',
                       kwargs={'post_id': PostsURLTests.post.id}
                       )
             )
        )

    def test_create_post_url_redirect_anonymous_user_on_admin_login(self):
        """Страница /create/ перенаправляет анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            reverse('posts:post_create'),
            follow=True
        )
        self.assertRedirects(
            response,
            (reverse('users:login')
             + "?next="
             + reverse('posts:post_create')
             )
        )

    # Проверяем редирект для авторизованного пользователя, но не автора поста
    def test_edit_post_url_redirect_authorized_user(self):
        """Страница /posts/post_id/edit/ перенаправляет авторизованного
        пользователя, который не является автором поста,
        на станицу /posts/post_id/.
        """
        response = self.test_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLTests.post.id}
            ), follow=True
        )
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': PostsURLTests.post.id}
                              )
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Проверка происходит с помощью клиента для автора поста.
        """
        # Шаблоны по адресам
        templates_url_names = {
            reverse(
                'posts:index'): (
                'posts/index.html'
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsURLTests.group.slug}): (
                'posts/group_list.html'
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostsURLTests.author_user.username}): (
                'posts/profile.html'
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsURLTests.post.id}): (
                'posts/post_detail.html'
            ),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLTests.post.id}): (
                'posts/create_post.html'
            ),
            reverse('posts:post_create'): (
                'posts/create_post.html'
            ),
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
