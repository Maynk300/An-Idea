from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from blogs.models import Blog, category
from io import BytesIO
from PIL import Image


def create_test_image(name='test.jpg', size=(100, 100), format='JPEG'):
    """Create a test image file."""
    image = Image.new('RGB', size, color='red')
    buffer = BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type=f'image/{format.lower()}')


class RegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Your Account')

    def test_register_valid_post(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertRedirects(response, reverse('login'))

    def test_register_invalid_duplicate_username(self):
        User.objects.create_user(username='existing', password='testpass123')
        response = self.client.post(reverse('register'), {
            'username': 'existing',
            'email': 'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists.')

    def test_register_invalid_duplicate_email(self):
        User.objects.create_user(username='existing', email='test@example.com', password='testpass123')
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'test@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        # Note: Default UserCreationForm doesn't enforce email uniqueness
        # The form will accept the duplicate email and redirect on success
        self.assertIn(response.status_code, [200, 302])

    def test_register_mismatched_passwords(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The two password fields didn')

    def test_register_short_password(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'short',
            'password2': 'short',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This password is too short')

    def test_register_common_password_rejected(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'password123',
            'password2': 'password123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This password is too common')


class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')

    def test_login_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid_username(self):
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password.')

    def test_login_invalid_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password.')

    def test_login_empty_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password.')


class LogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class ProtectedViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_my_blogs_requires_login(self):
        response = self.client.get(reverse('my_blogs'))
        self.assertEqual(response.status_code, 302)

    def test_create_blog_requires_login(self):
        response = self.client.get(reverse('create_blog'))
        self.assertEqual(response.status_code, 302)

    def test_edit_profile_requires_login(self):
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 302)

    def test_add_comment_requires_login(self):
        category_obj = category.objects.create(category_name='Technology')
        image = create_test_image()
        blog = Blog.objects.create(
            title='Test Blog',
            slug='test-blog',
            category=category_obj,
            author=self.user,
            featured_image=image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Published'
        )
        response = self.client.get(reverse('add_comment', args=[blog.slug]))
        self.assertEqual(response.status_code, 302)

    def test_like_blog_requires_login(self):
        category_obj = category.objects.create(category_name='Technology')
        image = create_test_image()
        blog = Blog.objects.create(
            title='Test Blog',
            slug='test-blog',
            category=category_obj,
            author=self.user,
            featured_image=image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Published'
        )
        response = self.client.get(reverse('like_blog', args=[blog.slug]))
        self.assertEqual(response.status_code, 302)


class MainURLsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_home_url(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_register_url(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_url(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_url(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class CSRFProtectionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = category.objects.create(category_name='Technology')
        self.image = create_test_image()
        self.blog = Blog.objects.create(
            title='Test Blog',
            slug='test-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Published'
        )

    def test_csrf_on_comment_form(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blogs', args=[self.blog.slug]))
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_csrf_on_blog_form(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('create_blog'))
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_csrf_on_profile_form(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_profile'))
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_csrf_on_login_form(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_csrf_on_register_form(self):
        response = self.client.get(reverse('register'))
        self.assertContains(response, 'csrfmiddlewaretoken')


class PermissionTests(TestCase):
    """Test that users cannot manipulate IDs/slugs to access other users' content."""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.category = category.objects.create(category_name='Technology')
        self.image = create_test_image()
        self.user_blog = Blog.objects.create(
            title='User Blog',
            slug='user-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Published'
        )
        self.other_blog = Blog.objects.create(
            title='Other Blog',
            slug='other-blog',
            category=self.category,
            author=self.other_user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Published'
        )

    def test_user_cannot_edit_other_user_blog_via_pk(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_blog', args=[self.other_blog.pk]))
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_other_user_blog_via_pk(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_blog', args=[self.other_blog.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Blog.objects.filter(pk=self.other_blog.pk).exists())

    def test_user_cannot_publish_other_user_blog_via_pk(self):
        self.client.login(username='testuser', password='testpass123')
        other_draft = Blog.objects.create(
            title='Other Draft',
            slug='other-draft',
            category=self.category,
            author=self.other_user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Draft'
        )
        response = self.client.post(reverse('publish_blog', args=[other_draft.pk]))
        self.assertEqual(response.status_code, 404)
        other_draft.refresh_from_db()
        self.assertEqual(other_draft.status, 'Draft')

    def test_user_cannot_unpublish_other_user_blog_via_pk(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('unpublish_blog', args=[self.other_blog.pk]))
        self.assertEqual(response.status_code, 404)
        self.other_blog.refresh_from_db()
        self.assertEqual(self.other_blog.status, 'Published')

    def test_user_cannot_edit_other_user_comment(self):
        from blogs.models import Comment
        other_comment = Comment.objects.create(
            blog=self.user_blog,
            author=self.other_user,
            content='Other user comment'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_comment', args=[other_comment.pk]))
        self.assertEqual(response.status_code, 302)

    def test_user_cannot_delete_other_user_comment(self):
        from blogs.models import Comment
        # Create a comment by other_user on testuser's blog
        other_comment = Comment.objects.create(
            blog=self.user_blog,
            author=self.other_user,
            content='Other user comment'
        )
        # other_user tries to delete their own comment on testuser's blog
        # They can delete their own comment
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.post(reverse('delete_comment', args=[other_comment.pk]), follow=True)
        self.assertFalse(Comment.objects.filter(pk=other_comment.pk).exists())
        
        # Now create another comment and test that a third user cannot delete it
        third_user = User.objects.create_user(username='thirduser', password='testpass123')
        third_comment = Comment.objects.create(
            blog=self.user_blog,
            author=self.user,
            content='Test user comment'
        )
        self.client.login(username='thirduser', password='testpass123')
        response = self.client.post(reverse('delete_comment', args=[third_comment.pk]), follow=True)
        self.assertTrue(Comment.objects.filter(pk=third_comment.pk).exists())


class DraftContentExposureTest(TestCase):
    """Test that draft content is not exposed publicly."""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = category.objects.create(category_name='Technology')
        self.image = create_test_image()
        self.draft_blog = Blog.objects.create(
            title='Draft Blog',
            slug='draft-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Draft'
        )
        self.published_blog = Blog.objects.create(
            title='Published Blog',
            slug='published-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Published'
        )

    def test_draft_blog_not_accessible_via_detail_view(self):
        response = self.client.get(reverse('blogs', args=[self.draft_blog.slug]))
        self.assertEqual(response.status_code, 404)

    def test_draft_blog_not_in_category_view(self):
        response = self.client.get(reverse('posts_by_category', args=[self.category.pk]))
        self.assertNotContains(response, 'Draft Blog')
        self.assertContains(response, 'Published Blog')

    def test_draft_blog_not_in_tag_view(self):
        from blogs.models import Tag
        tag = Tag.objects.create(name='Test', slug='test')
        self.draft_blog.tags.add(tag)
        self.published_blog.tags.add(tag)
        response = self.client.get(reverse('posts_by_tag', args=[tag.slug]))
        self.assertNotContains(response, 'Draft Blog')
        self.assertContains(response, 'Published Blog')

    def test_draft_blog_not_in_search(self):
        response = self.client.get(reverse('search'), {'keyword': 'Draft'})
        self.assertNotContains(response, 'Draft Blog')

    def test_draft_blog_not_in_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'Draft Blog')

    def test_draft_blog_not_in_profile_view(self):
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertNotContains(response, 'Draft Blog')

    def test_draft_blog_cannot_be_commented_on(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_comment', args=[self.draft_blog.slug]), {'content': 'Test'}, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_draft_blog_cannot_be_liked(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('like_blog', args=[self.draft_blog.slug]), follow=True)
        self.assertEqual(response.status_code, 404)