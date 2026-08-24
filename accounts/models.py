from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


def validate_image_file(value):
    """Validate image file size (max 5MB) and type."""
    max_size = 5 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError('Image file size must be under 5MB.')

    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    if hasattr(value, 'content_type') and value.content_type not in allowed_types:
        raise ValidationError('Unsupported image format. Use JPEG, PNG, WebP, or GIF.')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to='profile_pics/%Y/%m/%d',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif']), validate_image_file],
        blank=True,
        null=True,
    )
    bio = models.TextField(max_length=500, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"