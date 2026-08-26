
from .models import category
from assignments.models import SocialLinks


def get_categories(request):
    categories = category.objects.all()
    return dict(categories=categories)


def get_social(request):
    social = SocialLinks.objects.all()
    return dict(social=social)


def get_canonical_url(request):
    """Add canonical URL to context for SEO."""
    # Build absolute URL for the current page
    canonical_url = request.build_absolute_uri(request.path)
    return dict(canonical_url=canonical_url)