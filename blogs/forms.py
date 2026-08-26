from django import forms
from ckeditor.widgets import CKEditorWidget
import bleach
from .models import Blog, category, Comment, Tag


ALLOWED_TAGS = [
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'strike', 's',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'blockquote',
    'pre', 'code',
    'a',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'code': ['class'],
    'pre': ['class'],
}

ALLOWED_STYLES = []


def sanitize_html(html):
    """Sanitize HTML to prevent XSS attacks."""
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )


class BlogForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas (e.g., django, python, webdev)'
        }),
        help_text='Enter tags separated by commas. New tags will be created automatically.'
    )

    class Meta:
        model = Blog
        fields = ('title', 'category', 'featured_image', 'short_description', 'blog_body', 'status', 'is_featured')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'blog_body': CKEditorWidget(),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])

    def clean_blog_body(self):
        blog_body = self.cleaned_data.get('blog_body', '')
        return sanitize_html(blog_body)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your comment...'}),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise forms.ValidationError('Comment cannot be empty.')
        return content.strip()