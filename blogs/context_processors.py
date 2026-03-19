
from .models import category
from assignments.models import SocialLinks

def get_categories(request):
    categories = category.objects.all()
    return dict (categories=categories)

def get_social(request):
    social = SocialLinks.objects.all()
    return dict (social = social)