from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


def validate_image_file(value):
    """Validate image file size (max 5MB) and type."""
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError('Image file size must be under 5MB.')

    # Additional validation: check content type
    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    if hasattr(value, 'content_type') and value.content_type not in allowed_types:
        raise ValidationError('Unsupported image format. Use JPEG, PNG, WebP, or GIF.')


class category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    created_At = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['category_name']

    def __str__(self):
        return self.category_name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('posts_by_category', args=[self.pk])


STATUS_CHOICES = (
    ("Draft", "Draft"),
    ("Published", "Published")
)


class Blog(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    featured_image = models.ImageField(
        upload_to='uploads/%Y/%m/%d',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif']), validate_image_file]
    )
    short_description = models.TextField(max_length=500)
    blog_body = models.TextField(max_length=2000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Draft")
    is_featured = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', blank=True, related_name='blogs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blogs', args=[self.slug])


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.blog.title}'


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('posts_by_tag', args=[self.slug])


class Like(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog')
        ordering = ['-created_at']

    def __str__(self):
        return f'Like by {self.user.username} on {self.blog.title}'