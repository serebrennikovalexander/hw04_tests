from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных
        cls.author_user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post_1 = Post.objects.create(
            author=cls.author_user,
            text='Тест.',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        # Создаем клиент для автора поста
        self.author_user = PostsCreateFormTests.author_user
        self.author_client = Client()
        self.author_client.force_login(self.author_user)

    # Проверяем форму для создание поста
    def test_form_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тест' * 2,
        }
        # Отправляем POST-запрос
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username':
                        PostsCreateFormTests.author_user.username
                        }
            )
        )
        # Проверяем, что создалась запись с заданным текстом
        self.assertTrue(
            Post.objects.filter(
                text='Тест' * 2
            ).exists()
        )

    # Проверяем форму для редактирования поста
    def test_form_edit_post(self):
        """Валидная форма изменяет пост в базе данных."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тест' * 3,
        }
        # Отправляем POST-запрос
        self.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsCreateFormTests.post_1.id}
            ),
            data=form_data,
            follow=True
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что произошло изменение поста
        self.assertTrue(
            Post.objects.filter(
                text='Тест' * 3,
                id=PostsCreateFormTests.post_1.id
            ).exists()
        )
