

from django.urls import path
from . import views

urlpatterns = [
    path('<int:category_id>/', views.posts_by_category, name='posts_by_category'),
    path('<slug:slug>/like/', views.like_blog, name='like_blog'),
]