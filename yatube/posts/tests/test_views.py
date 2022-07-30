from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя, который будет автором постов
        cls.author_user = User.objects.create_user(username='auth')
        # Создаем 2 группы
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug_1',
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug_2',
            description='Тестовое описание 2',
        )
        # Создаем 2 поста с первой группой
        cls.post_1 = Post.objects.create(
            author=cls.author_user,
            text='Тест.',
            group=cls.group_1,
        )
        cls.post_2 = Post.objects.create(
            author=cls.author_user,
            text='Тест.'*2,
            group=cls.group_1,
        )
        # Создаем пост с второй группой
        cls.post_3 = Post.objects.create(
            author=cls.author_user,
            text='Тест.'*3,
            group=cls.group_2,
        )

    def setUp(self):
        # Создаем клиент для автора поста
        self.author_user = PostsPagesTests.author_user
        self.author_client = Client()
        self.author_client.force_login(self.author_user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse(
                'posts:index'): (
                'posts/index.html'
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsPagesTests.group_1.slug}): (
                'posts/group_list.html'
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostsPagesTests.author_user.username}): (
                'posts/profile.html'
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsPagesTests.post_1.id}): (
                'posts/post_detail.html'
            ),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsPagesTests.post_1.id}): (
                'posts/create_post.html'
            ),
            reverse('posts:post_create'): (
                'posts/create_post.html'
            ),
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка контекста страницы /
    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        # Проверка количества постов на странице
        self.assertEqual(len(response.context['page_obj']), 3)

    # Проверяем, что словарь context страницы index для первого
    # элемент содержит ожидаемые значения
    def test_home_page_show_correct_fields_in_post(self):
        """Шаблон home сформирован с правильным контекстом
        для первого тестового поста.
        """
        response = self.author_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        # Первый пост имеет номер 3 так как создан позже первых двух
        self.assertEqual(task_text_0, PostsPagesTests.post_3.text)
        self.assertEqual(task_author_0, PostsPagesTests.post_3.author)
        self.assertEqual(task_group_0, PostsPagesTests.post_3.group)

    # Проверка контекста страницы /group/slug/
    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        # Запрос к странице первой группы
        response = self.author_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostsPagesTests.group_1.slug}
                    )
            )
        # Первый пост на странице группы имеет номер 2
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group
        self.assertIn('page_obj', response.context)
        self.assertIn('group', response.context)
        # Провекра количества постов на странице
        # У первой группы должно быть 2 поста
        self.assertEqual(len(response.context['page_obj']), 2)
        # Провекра, что у первого поста правильная группа
        self.assertEqual(post_group_0, PostsPagesTests.group_1)

    # Проверка контекста страницы /pfofile/username/
    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:profile',
                    kwargs={'username': PostsPagesTests.author_user.username}
                    )
            )
        # Первый пост на странице пользователя имеет номер 3
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        self.assertIn('page_obj', response.context)
        self.assertIn('author', response.context)
        self.assertIn('number_of_posts', response.context)
        # Провекра количества постов на странице
        # У автора должно быть 3 поста
        self.assertEqual(len(response.context['page_obj']), 3)
        # Провекра, что у первого поста правильный автор
        self.assertEqual(post_author_0, PostsPagesTests.author_user)

    # Проверка контекста страницы /posts/post_id/
    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostsPagesTests.post_1.id}
                    )
            )
        self.assertIn('post', response.context)
        self.assertIn('title', response.context)
        self.assertIn('number_of_posts', response.context)
        # Провекра, что у поста правильный id
        self.assertEqual(
            response.context['post'].id, PostsPagesTests.post_1.id
        )

    # Проверка контекста страницы /posts/post_id/edit/
    def test_post_edit_show_correct_context(self):
        """Шаблон create_post для редактирования поста
        сформирован с правильным контекстом.
        """
        response = self.author_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostsPagesTests.post_1.id}
                    )
            )
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertEqual(
            response.context['post'].id, PostsPagesTests.post_1.id
        )

    # Проверка контекста страницы /create/
    def test_post_create_show_correct_context(self):
        """Шаблон create_post для создания поста
        сформирован с правильным контекстом.
        """
        response = self.author_client.get(
            reverse('posts:post_create')
            )
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    # Дополнительная проверка при создании поста
    def test_post_create_test(self):
        """При создании поста он попадает на
         главну страницу и на страницу группы.
        """
        post_4 = Post.objects.create(
            author=PostsPagesTests.author_user,
            text='Тест.'*4,
            group=PostsPagesTests.group_1,
        )
        # Провекра, что пост оказался на главной странице
        response_1 = self.author_client.get(reverse('posts:index'))
        self.assertEqual(len(response_1.context['page_obj']), 4)
        # Провекра, что первый пост на странице это пост номер 4
        first_object_1 = response_1.context['page_obj'][0]
        self.assertEqual(first_object_1.id, post_4.id)
        # Провекра, что пост оказался на странице группы
        response_2 = self.author_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostsPagesTests.group_1.slug}
                    )
            )
        self.assertEqual(len(response_2.context['page_obj']), 3)
        # Провекра, что первый пост на странице это пост номер 4
        first_object_2 = response_2.context['page_obj'][0]
        self.assertEqual(first_object_2.id, post_4.id)
        # Провекра, что пост оказался в профайле пользователя
        response_3 = self.author_client.get(
            reverse('posts:profile',
                    kwargs={'username': PostsPagesTests.author_user.username}
                    )
            )
        self.assertEqual(len(response_3.context['page_obj']), 4)
        # Провекра, что первый пост на странице это пост номер 4
        first_object_3 = response_3.context['page_obj'][0]
        self.assertEqual(first_object_3.id, post_4.id)
        # Проверка, что пост не попал в группу,
        # для которой не был предназначен
        response_4 = self.author_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostsPagesTests.group_2.slug}
                    )
            )
        # Проверка, что пост не появился на странице второй группы
        self.assertEqual(len(response_4.context['page_obj']), 1)


# Тестирование паджинатора
class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя, который будет автором всех поста
        cls.author_user = User.objects.create_user(username='auth')
        # Создаем группу для всех постов
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Создаем 15 постов
        for i in range(15):
            Post.objects.create(
                author=cls.author_user,
                text='Тест.'*20,
                group=cls.group,
            )

    def setUp(self):
        # Создаем клиент для автора поста
        self.author_user = PaginatorViewsTest.author_user
        self.author_client = Client()
        self.author_client.force_login(self.author_user)

    # Проверяем страницу /
    def test_index_first_page_contains_ten_records(self):
        response = self.author_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_five_records(self):
        # Проверка: на второй странице должно быть пять постов.
        response = self.author_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    # Проверяем страницу /group/slug/
    def test_group_list_first_page_contains_ten_records(self):
        response = self.author_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PaginatorViewsTest.group.slug}
                    )
            )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_five_records(self):
        # Проверка: на второй странице должно быть пять постов.
        response = self.author_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PaginatorViewsTest.group.slug}
                    )
            + '?page=2'
            )
        self.assertEqual(len(response.context['page_obj']), 5)

    # Проверяем страницу /pfofile/username/
    def test_profile_first_page_contains_ten_records(self):
        response = self.author_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.author_user.username}
                )
            )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_five_records(self):
        # Проверка: на второй странице должно быть пять постов.
        response = self.author_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.author_user.username}
                )
            + '?page=2'
            )
        self.assertEqual(len(response.context['page_obj']), 5)
