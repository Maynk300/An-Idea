from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.db import IntegrityError
from .models import Blog, category, Comment, Tag, Like
from .forms import BlogForm, CommentForm
from io import BytesIO
from PIL import Image


def create_test_image(name='test.jpg', size=(100, 100), format='JPEG'):
    """Create a test image file."""
    image = Image.new('RGB', size, color='red')
    buffer = BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type=f'image/{format.lower()}')


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        cat = category.objects.create(category_name='Technology')
        self.assertEqual(str(cat), 'Technology')
        self.assertEqual(cat.category_name, 'Technology')

    def test_category_unique_name(self):
        category.objects.create(category_name='Technology')
        with self.assertRaises(IntegrityError):
            category.objects.create(category_name='Technology')

    def test_category_ordering(self):
        category.objects.create(category_name='Zebra')
        category.objects.create(category_name='Apple')
        cats = list(category.objects.all())
        self.assertEqual(cats[0].category_name, 'Apple')
        self.assertEqual(cats[1].category_name, 'Zebra')


class TagModelTest(TestCase):
    def test_tag_creation(self):
        tag = Tag.objects.create(name='Django', slug='django')
        self.assertEqual(str(tag), 'Django')
        self.assertEqual(tag.name, 'Django')
        self.assertEqual(tag.slug, 'django')

    def test_tag_unique_name(self):
        Tag.objects.create(name='Django', slug='django')
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name='Django', slug='django-2')

    def test_tag_unique_slug(self):
        Tag.objects.create(name='Django', slug='django')
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name='Python', slug='django')

    def test_tag_ordering(self):
        Tag.objects.create(name='Zebra', slug='zebra')
        Tag.objects.create(name='Apple', slug='apple')
        tags = list(Tag.objects.all())
        self.assertEqual(tags[0].name, 'Apple')
        self.assertEqual(tags[1].name, 'Zebra')


class BlogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = category.objects.create(category_name='Technology')
        self.image = create_test_image()

    def test_blog_creation(self):
        blog = Blog.objects.create(
            title='Test Blog',
            slug='test-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Published'
        )
        self.assertEqual(str(blog), 'Test Blog')
        self.assertEqual(blog.status, 'Published')
        self.assertEqual(blog.author, self.user)

    def test_blog_default_status_draft(self):
        blog = Blog.objects.create(
            title='Draft Blog',
            slug='draft-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content'
        )
        self.assertEqual(blog.status, 'Draft')

    def test_blog_slug_unique(self):
        Blog.objects.create(
            title='Test Blog',
            slug='test-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content'
        )
        with self.assertRaises(IntegrityError):
            Blog.objects.create(
                title='Another Blog',
                slug='test-blog',
                category=self.category,
                author=self.user,
                featured_image=self.image,
                short_description='Short description',
                blog_body='Blog body content'
            )

    def test_blog_tags_relationship(self):
        blog = Blog.objects.create(
            title='Test Blog',
            slug='test-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content'
        )
        tag1 = Tag.objects.create(name='Django', slug='django')
        tag2 = Tag.objects.create(name='Python', slug='python')
        blog.tags.add(tag1, tag2)
        self.assertEqual(blog.tags.count(), 2)
        self.assertIn(tag1, blog.tags.all())
        self.assertIn(tag2, blog.tags.all())

    def test_blog_related_name_comments(self):
        blog = Blog.objects.create(
            title='Test Blog',
            slug='test-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content'
        )
        comment = Comment.objects.create(blog=blog, author=self.user, content='Test comment')
        self.assertEqual(blog.comments.count(), 1)
        self.assertEqual(blog.comments.first(), comment)

    def test_blog_related_name_likes(self):
        blog = Blog.objects.create(
            title='Test Blog',
            slug='test-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content'
        )
        like = Like.objects.create(blog=blog, user=self.user)
        self.assertEqual(blog.likes.count(), 1)
        self.assertEqual(blog.likes.first(), like)


class CommentModelTest(TestCase):
    def setUp(self):
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

    def test_comment_creation(self):
        comment = Comment.objects.create(blog=self.blog, author=self.user, content='Test comment')
        self.assertEqual(str(comment), f'Comment by {self.user.username} on {self.blog.title}')
        self.assertEqual(comment.content, 'Test comment')

    def test_comment_ordering(self):
        Comment.objects.create(blog=self.blog, author=self.user, content='First comment')
        Comment.objects.create(blog=self.blog, author=self.user, content='Second comment')
        comments = list(self.blog.comments.all())
        self.assertEqual(comments[0].content, 'Second comment')
        self.assertEqual(comments[1].content, 'First comment')


class LikeModelTest(TestCase):
    def setUp(self):
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

    def test_like_creation(self):
        like = Like.objects.create(blog=self.blog, user=self.user)
        self.assertEqual(str(like), f'Like by {self.user.username} on {self.blog.title}')

    def test_unique_like_per_user_per_blog(self):
        Like.objects.create(blog=self.blog, user=self.user)
        with self.assertRaises(IntegrityError):
            Like.objects.create(blog=self.blog, user=self.user)

    def test_multiple_users_can_like_same_blog(self):
        user2 = User.objects.create_user(username='testuser2', password='testpass123')
        Like.objects.create(blog=self.blog, user=self.user)
        Like.objects.create(blog=self.blog, user=user2)
        self.assertEqual(self.blog.likes.count(), 2)


class BlogFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = category.objects.create(category_name='Technology')
        self.image = create_test_image()

    def test_valid_blog_form(self):
        form_data = {
            'title': 'Test Blog',
            'category': self.category.pk,
            'short_description': 'Short description',
            'blog_body': '<p>Blog body content</p>',
            'status': 'Published',
            'is_featured': False,
            'tags': 'django, python'
        }
        form = BlogForm(data=form_data, files={'featured_image': self.image})
        self.assertTrue(form.is_valid(), form.errors)

    def test_blog_form_missing_required_fields(self):
        form_data = {
            'title': '',
            'category': '',
            'short_description': '',
            'blog_body': '',
        }
        form = BlogForm(data=form_data, files={'featured_image': self.image})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('category', form.errors)
        self.assertIn('short_description', form.errors)
        self.assertIn('blog_body', form.errors)

    def test_blog_form_sanitizes_html(self):
        form_data = {
            'title': 'Test Blog',
            'category': self.category.pk,
            'short_description': 'Short description',
            'blog_body': '<script>alert("xss")</script><p>Safe content</p>',
            'status': 'Published',
            'is_featured': False,
            'tags': 'django, python'
        }
        form = BlogForm(data=form_data, files={'featured_image': self.image})
        self.assertTrue(form.is_valid())
        self.assertNotIn('<script>', form.cleaned_data['blog_body'])
        self.assertIn('<p>Safe content</p>', form.cleaned_data['blog_body'])

    def test_blog_form_allows_approved_tags(self):
        form_data = {
            'title': 'Test Blog',
            'category': self.category.pk,
            'short_description': 'Short description',
            'blog_body': '<p>Paragraph</p><strong>Bold</strong><em>Italic</em><a href="http://example.com">Link</a>',
            'status': 'Published',
            'is_featured': False,
            'tags': 'django, python'
        }
        form = BlogForm(data=form_data, files={'featured_image': self.image})
        self.assertTrue(form.is_valid())
        self.assertIn('<p>Paragraph</p>', form.cleaned_data['blog_body'])
        self.assertIn('<strong>Bold</strong>', form.cleaned_data['blog_body'])
        self.assertIn('<em>Italic</em>', form.cleaned_data['blog_body'])
        self.assertIn('href="http://example.com"', form.cleaned_data['blog_body'])

    def test_blog_form_strips_disallowed_attributes(self):
        form_data = {
            'title': 'Test Blog',
            'category': self.category.pk,
            'short_description': 'Short description',
            'blog_body': '<p onclick="alert(1)">Content</p>',
            'status': 'Published',
            'is_featured': False,
            'tags': 'django, python'
        }
        form = BlogForm(data=form_data, files={'featured_image': self.image})
        self.assertTrue(form.is_valid())
        self.assertNotIn('onclick', form.cleaned_data['blog_body'])

    def test_blog_form_initial_tags_on_edit(self):
        blog = Blog.objects.create(
            title='Test Blog',
            slug='test-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content'
        )
        tag1 = Tag.objects.create(name='Django', slug='django')
        tag2 = Tag.objects.create(name='Python', slug='python')
        blog.tags.add(tag1, tag2)

        form = BlogForm(instance=blog)
        self.assertIn('Django', form.fields['tags'].initial)
        self.assertIn('Python', form.fields['tags'].initial)


class CommentFormTest(TestCase):
    def test_valid_comment_form(self):
        form_data = {'content': 'This is a valid comment'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_comment_rejected(self):
        form_data = {'content': ''}
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_whitespace_only_comment_rejected(self):
        form_data = {'content': '   '}
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_comment_content_stripped(self):
        form_data = {'content': '  Valid comment  '}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['content'], 'Valid comment')


class PostsByCategoryViewTest(TestCase):
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

    def test_posts_by_category_returns_200(self):
        response = self.client.get(reverse('posts_by_category', args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)

    def test_posts_by_category_shows_only_published(self):
        response = self.client.get(reverse('posts_by_category', args=[self.category.pk]))
        self.assertContains(response, 'Published Blog')
        self.assertNotContains(response, 'Draft Blog')

    def test_posts_by_category_404_for_invalid_category(self):
        response = self.client.get(reverse('posts_by_category', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_posts_by_category_pagination(self):
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
        response = self.client.get(reverse('posts_by_category', args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(hasattr(response.context['posts'], 'paginator'))


class PostsByTagViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = category.objects.create(category_name='Technology')
        self.image = create_test_image()
        self.tag = Tag.objects.create(name='Django', slug='django')
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
        self.published_blog.tags.add(self.tag)
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
        self.draft_blog.tags.add(self.tag)

    def test_posts_by_tag_returns_200(self):
        response = self.client.get(reverse('posts_by_tag', args=[self.tag.slug]))
        self.assertEqual(response.status_code, 200)

    def test_posts_by_tag_shows_only_published(self):
        response = self.client.get(reverse('posts_by_tag', args=[self.tag.slug]))
        self.assertContains(response, 'Published Blog')
        self.assertNotContains(response, 'Draft Blog')

    def test_posts_by_tag_404_for_invalid_tag(self):
        response = self.client.get(reverse('posts_by_tag', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)


class BlogDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
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

    def test_blog_detail_returns_200_for_published(self):
        response = self.client.get(reverse('blogs', args=[self.published_blog.slug]))
        self.assertEqual(response.status_code, 200)

    def test_blog_detail_404_for_draft(self):
        response = self.client.get(reverse('blogs', args=[self.draft_blog.slug]))
        self.assertEqual(response.status_code, 404)

    def test_blog_detail_404_for_nonexistent(self):
        response = self.client.get(reverse('blogs', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)

    def test_blog_detail_shows_comments(self):
        Comment.objects.create(blog=self.published_blog, author=self.user, content='Test comment')
        response = self.client.get(reverse('blogs', args=[self.published_blog.slug]))
        self.assertContains(response, 'Test comment')

    def test_blog_detail_shows_comment_form_for_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blogs', args=[self.published_blog.slug]))
        self.assertContains(response, 'Write your comment')

    def test_blog_detail_hides_comment_form_for_anonymous(self):
        response = self.client.get(reverse('blogs', args=[self.published_blog.slug]))
        self.assertNotContains(response, 'Write your comment')

    def test_blog_detail_shows_related_posts(self):
        category2 = category.objects.create(category_name='Science')
        related_blog = Blog.objects.create(
            title='Related Blog',
            slug='related-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Published'
        )
        response = self.client.get(reverse('blogs', args=[self.published_blog.slug]))
        self.assertContains(response, 'Related Blog')


class SearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = category.objects.create(category_name='Technology')
        self.image = create_test_image()
        self.tag = Tag.objects.create(name='Django', slug='django')
        self.blog1 = Blog.objects.create(
            title='Django Tutorial',
            slug='django-tutorial',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Learn Django',
            blog_body='Django is a web framework',
            status='Published'
        )
        self.blog1.tags.add(self.tag)
        self.blog2 = Blog.objects.create(
            title='Python Guide',
            slug='python-guide',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Learn Python',
            blog_body='Python is a programming language',
            status='Published'
        )
        self.draft_blog = Blog.objects.create(
            title='Draft Post',
            slug='draft-post',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Draft content',
            blog_body='This is a draft',
            status='Draft'
        )

    def test_search_returns_200(self):
        response = self.client.get(reverse('search'), {'keyword': 'Django'})
        self.assertEqual(response.status_code, 200)

    def test_search_by_title(self):
        response = self.client.get(reverse('search'), {'keyword': 'Django'})
        self.assertContains(response, 'Django Tutorial')
        self.assertNotContains(response, 'Python Guide')

    def test_search_by_short_description(self):
        response = self.client.get(reverse('search'), {'keyword': 'Learn Python'})
        self.assertContains(response, 'Python Guide')

    def test_search_by_blog_body(self):
        response = self.client.get(reverse('search'), {'keyword': 'web framework'})
        self.assertContains(response, 'Django Tutorial')

    def test_search_by_category_name(self):
        response = self.client.get(reverse('search'), {'keyword': 'Technology'})
        self.assertContains(response, 'Django Tutorial')
        self.assertContains(response, 'Python Guide')

    def test_search_by_tag_name(self):
        response = self.client.get(reverse('search'), {'keyword': 'Django'})
        self.assertContains(response, 'Django Tutorial')

    def test_search_excludes_draft_blogs(self):
        response = self.client.get(reverse('search'), {'keyword': 'Draft'})
        self.assertNotContains(response, 'Draft Post')

    def test_search_empty_keyword(self):
        response = self.client.get(reverse('search'), {'keyword': ''})
        self.assertEqual(response.status_code, 200)

    def test_search_no_results(self):
        response = self.client.get(reverse('search'), {'keyword': 'Nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Django Tutorial')

    def test_search_pagination(self):
        for i in range(10):
            Blog.objects.create(
                title=f'Django Blog {i}',
                slug=f'django-blog-{i}',
                category=self.category,
                author=self.user,
                featured_image=self.image,
                short_description='Short description',
                blog_body='Blog body content',
                status='Published'
            )
        response = self.client.get(reverse('search'), {'keyword': 'Django'})
        self.assertEqual(response.status_code, 200)


class AddCommentViewTest(TestCase):
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

    def test_add_comment_authenticated_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('add_comment', args=[self.published_blog.slug]),
            {'content': 'Test comment'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(content='Test comment').exists())

    def test_add_comment_anonymous_user_redirects_to_login(self):
        response = self.client.post(
            reverse('add_comment', args=[self.published_blog.slug]),
            {'content': 'Test comment'},
            follow=True
        )
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("add_comment", args=[self.published_blog.slug])}')
        self.assertFalse(Comment.objects.filter(content='Test comment').exists())

    def test_add_comment_empty_content_rejected(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('add_comment', args=[self.published_blog.slug]),
            {'content': ''},
            follow=True
        )
        self.assertFalse(Comment.objects.filter(content='').exists())

    def test_add_comment_to_draft_blog_404(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('add_comment', args=[self.draft_blog.slug]),
            {'content': 'Test comment'},
            follow=True
        )
        self.assertEqual(response.status_code, 404)

    def test_add_comment_invalid_method(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('add_comment', args=[self.published_blog.slug]))
        self.assertEqual(response.status_code, 302)


class EditCommentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.category = category.objects.create(category_name='Technology')
        self.image = create_test_image()
        self.blog = Blog.objects.create(
            title='Published Blog',
            slug='published-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Published'
        )
        self.comment = Comment.objects.create(blog=self.blog, author=self.user, content='Original comment')

    def test_edit_comment_owner(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_comment', args=[self.comment.pk]))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('edit_comment', args=[self.comment.pk]),
            {'content': 'Updated comment'},
            follow=True
        )
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment')

    def test_edit_comment_non_owner_denied(self):
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('edit_comment', args=[self.comment.pk]))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(
            reverse('edit_comment', args=[self.comment.pk]),
            {'content': 'Updated comment'},
            follow=True
        )
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Original comment')

    def test_edit_comment_empty_content_rejected(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('edit_comment', args=[self.comment.pk]),
            {'content': ''},
            follow=True
        )
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Original comment')


class DeleteCommentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.category = category.objects.create(category_name='Technology')
        self.image = create_test_image()
        self.blog = Blog.objects.create(
            title='Published Blog',
            slug='published-blog',
            category=self.category,
            author=self.user,
            featured_image=self.image,
            short_description='Short description',
            blog_body='Blog body content',
            status='Published'
        )
        self.comment = Comment.objects.create(blog=self.blog, author=self.user, content='Test comment')
        self.comment_by_other = Comment.objects.create(blog=self.blog, author=self.other_user, content='Other comment')

    def test_delete_comment_owner(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_comment', args=[self.comment.pk]), follow=True)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_delete_comment_blog_author_can_delete_others_comments(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_comment', args=[self.comment_by_other.pk]), follow=True)
        self.assertFalse(Comment.objects.filter(pk=self.comment_by_other.pk).exists())

    def test_delete_comment_other_user_denied(self):
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.post(reverse('delete_comment', args=[self.comment.pk]), follow=True)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_delete_comment_anonymous_redirects_to_login(self):
        response = self.client.post(reverse('delete_comment', args=[self.comment.pk]), follow=True)
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("delete_comment", args=[self.comment.pk])}')
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())


class LikeBlogViewTest(TestCase):
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

    def test_like_blog_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('like_blog', args=[self.published_blog.slug]), follow=True)
        self.assertTrue(Like.objects.filter(blog=self.published_blog, user=self.user).exists())

    def test_unlike_blog(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('like_blog', args=[self.published_blog.slug]), follow=True)
        response = self.client.post(reverse('like_blog', args=[self.published_blog.slug]), follow=True)
        self.assertFalse(Like.objects.filter(blog=self.published_blog, user=self.user).exists())

    def test_like_blog_anonymous_redirects_to_login(self):
        response = self.client.post(reverse('like_blog', args=[self.published_blog.slug]), follow=True)
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("like_blog", args=[self.published_blog.slug])}')
        self.assertFalse(Like.objects.filter(blog=self.published_blog).exists())

    def test_like_draft_blog_404(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('like_blog', args=[self.draft_blog.slug]), follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Like.objects.filter(blog=self.draft_blog).exists())

    def test_duplicate_like_prevented(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('like_blog', args=[self.published_blog.slug]), follow=True)
        # First POST creates the like
        self.assertEqual(Like.objects.filter(blog=self.published_blog, user=self.user).count(), 1)
        # Second POST removes the like (unlike)
        self.client.post(reverse('like_blog', args=[self.published_blog.slug]), follow=True)
        self.assertEqual(Like.objects.filter(blog=self.published_blog, user=self.user).count(), 0)


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = category.objects.create(category_name='Technology')
        self.image = create_test_image()
        for i in range(10):
            Blog.objects.create(
                title=f'Blog {i}',
                slug=f'blog-{i}',
                category=self.category,
                author=self.user,
                featured_image=self.image,
                short_description='Short description',
                blog_body='Blog body content',
                status='Published',
                is_featured=(i == 0)
            )

    def test_home_returns_200(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_shows_featured_post(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Blog 0')

    def test_home_pagination(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('recent_post' in response.context)


class BlogURLsTest(TestCase):
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

    def test_home_url(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_posts_by_category_url(self):
        response = self.client.get(reverse('posts_by_category', args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)

    def test_posts_by_tag_url(self):
        tag = Tag.objects.create(name='Django', slug='django')
        self.blog.tags.add(tag)
        response = self.client.get(reverse('posts_by_tag', args=[tag.slug]))
        self.assertEqual(response.status_code, 200)

    def test_blog_detail_url(self):
        response = self.client.get(reverse('blogs', args=[self.blog.slug]))
        self.assertEqual(response.status_code, 200)

    def test_search_url(self):
        response = self.client.get(reverse('search'), {'keyword': 'test'})
        self.assertEqual(response.status_code, 200)

    def test_add_comment_url_requires_login(self):
        response = self.client.get(reverse('add_comment', args=[self.blog.slug]))
        self.assertEqual(response.status_code, 302)

    def test_like_blog_url_requires_login(self):
        response = self.client.get(reverse('like_blog', args=[self.blog.slug]))
        self.assertEqual(response.status_code, 302)


class SanitizationTest(TestCase):
    def test_sanitize_removes_scripts(self):
        from blogs.forms import sanitize_html
        html = '<script>alert("xss")</script><p>Safe</p>'
        result = sanitize_html(html)
        self.assertNotIn('<script>', result)
        self.assertIn('<p>Safe</p>', result)

    def test_sanitize_removes_event_handlers(self):
        from blogs.forms import sanitize_html
        html = '<p onclick="alert(1)">Content</p>'
        result = sanitize_html(html)
        self.assertNotIn('onclick', result)

    def test_sanitize_allows_safe_tags(self):
        from blogs.forms import sanitize_html
        html = '<p>Text</p><strong>Bold</strong><a href="http://example.com">Link</a>'
        result = sanitize_html(html)
        self.assertIn('<p>Text</p>', result)
        self.assertIn('<strong>Bold</strong>', result)
        self.assertIn('href="http://example.com"', result)

    def test_sanitize_allows_code_and_pre(self):
        from blogs.forms import sanitize_html
        html = '<pre><code class="language-python">print("hello")</code></pre>'
        result = sanitize_html(html)
        self.assertIn('<pre>', result)
        self.assertIn('<code', result)
        self.assertIn('class="language-python"', result)

    def test_sanitize_strips_disallowed_tags(self):
        from blogs.forms import sanitize_html
        html = '<div>Content</div><span>More</span>'
        result = sanitize_html(html)
        self.assertNotIn('<div>', result)
        self.assertNotIn('<span>', result)
        self.assertIn('Content', result)
        self.assertIn('More', result)