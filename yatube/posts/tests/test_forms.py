from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.forms import PostForm

from ..models import Group, Post, Comment

User = get_user_model()

TEST_POST_TEXT = 'Тестовый пост'
TEST_POST_TEXT_2 = 'Изменённый тестовый пост'
TEST_COMMENT = 'Тестовый комментарий'


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.file_field = SimpleUploadedFile("best_test_file.txt",
                                            b"file_content")

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
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )

        # Создание формы для проверки атрибутов
        cls.form = PostForm()

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(PostsFormsTests.user)

    def test_posts_create_post(self):
        """Запись в Post"""
        posts_count = Post.objects.count()
        form_data = {
            'text': TEST_POST_TEXT,
            'group': self.group.pk,
            'image': self.uploaded,
        }

        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        # Тестовая запись с валидной картинкой создалась
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=TEST_POST_TEXT,
                group=self.group,
                author=self.user,
                image='posts/small.gif',
            ).exists()
        )

    def test_not_valid_image(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': TEST_POST_TEXT,
            'group': self.group.pk,
            'image': self.file_field,
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверка доступности страницы создания поста после загрузки
        # невалидной картинки
        self.assertEqual(response.reason_phrase, 'OK')
        # Проверка, что тестовая запись в БД с невалидной картинкой не
        # создалась
        self.assertEqual(Post.objects.count(), posts_count)

    def test_posts_edit_post(self):
        """Редактирует запись в Post"""
        posts_count = Post.objects.count()

        form_data = {
            'text': TEST_POST_TEXT_2,
            'group': self.group.pk,
        }

        self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            Post.objects.get(pk=self.post.pk).text,
            TEST_POST_TEXT_2
        )

    def test_posts_user_creates_comment(self):
        """Проверка создания комментария через форму PostForm"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': TEST_COMMENT,
        }
        response = self.auth_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(text=TEST_COMMENT).exists()
        )
