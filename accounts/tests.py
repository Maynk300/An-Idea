from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.db import IntegrityError
from .models import Profile
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


class ProfileModelTest(TestCase):
    def test_profile_creation(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        # Profile is created automatically by signal
        profile = user.profile
        profile.bio = 'Test bio'
        profile.save()
        self.assertEqual(str(profile), "testuser's Profile")
        self.assertEqual(profile.bio, 'Test bio')

    def test_profile_one_to_one_with_user(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        profile = user.profile
        self.assertEqual(user.profile, profile)

    def test_profile_unique_per_user(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        # Profile already exists due to signal
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=user)


class ProfileSignalTest(TestCase):
    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(username='newuser', password='testpass123')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)

    def test_profile_saved_on_user_save(self):
        user = User.objects.create_user(username='newuser', password='testpass123')
        profile = user.profile
        profile.bio = 'Updated bio'
        profile.save()
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.profile.bio, 'Updated bio')


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = category.objects.create(category_name='Technology')
        self.image = create_test_image()
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

    def test_profile_view_public_accessible(self):
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_profile_view_shows_published_blogs(self):
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertContains(response, 'Published Blog')

    def test_profile_view_hides_draft_blogs(self):
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertNotContains(response, 'Draft Blog')

    def test_profile_view_404_for_nonexistent_user(self):
        response = self.client.get(reverse('profile', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)

    def test_profile_view_pagination(self):
        for i in range(10):
            Blog.objects.create(
                title=f'Blog {i}',
                slug=f'blog-{i}',
                category=self.category,
                author=self.user,
                featured_image=self.image,
                short_description='Short description',
                blog_body='Blog body content',
                status='Published'
            )
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('published_blogs' in response.context)


class EditProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.image = create_test_image()

    def test_edit_profile_requires_login(self):
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 302)

    def test_edit_own_profile_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)

    def test_edit_own_profile_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('edit_profile'), {
            'bio': 'Updated bio',
            'profile_picture': create_test_image()
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'Updated bio')
        self.assertTrue(self.user.profile.profile_picture)

    def test_edit_other_user_profile_not_possible(self):
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'].user, self.other_user)


class ProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.image = create_test_image()

    def test_valid_profile_form(self):
        from accounts.forms import ProfileForm
        form = ProfileForm(data={'bio': 'Test bio'}, files={'profile_picture': self.image}, instance=self.user.profile)
        self.assertTrue(form.is_valid(), form.errors)

    def test_profile_form_empty_bio_allowed(self):
        from accounts.forms import ProfileForm
        form = ProfileForm(data={'bio': ''}, instance=self.user.profile)
        self.assertTrue(form.is_valid())

    def test_profile_form_bio_max_length(self):
        from accounts.forms import ProfileForm
        form = ProfileForm(data={'bio': 'x' * 501}, instance=self.user.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('bio', form.errors)

    def test_profile_form_rejects_large_image(self):
        from accounts.forms import ProfileForm
        large_image = create_test_image(size=(5000, 5000))
        large_image.size = 6 * 1024 * 1024
        form = ProfileForm(data={'bio': 'Test bio'}, files={'profile_picture': large_image}, instance=self.user.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('profile_picture', form.errors)

    def test_profile_form_rejects_invalid_format(self):
        from accounts.forms import ProfileForm
        image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        image.save(buffer, format='BMP')
        buffer.seek(0)
        invalid_image = SimpleUploadedFile('test.bmp', buffer.read(), content_type='image/bmp')
        form = ProfileForm(data={'bio': 'Test bio'}, files={'profile_picture': invalid_image}, instance=self.user.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('profile_picture', form.errors)


class AccountsURLsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_profile_url(self):
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_url_requires_login(self):
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 302)

    def test_edit_profile_url_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)