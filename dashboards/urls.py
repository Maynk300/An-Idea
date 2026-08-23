

from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('categories/', views.categories, name='categories'),
    path('blogs/', views.my_blogs, name='my_blogs'),
    path('blogs/create/', views.create_blog, name='create_blog'),
    path('blogs/edit/<int:pk>/', views.edit_blog, name='edit_blog'),
    path('blogs/delete/<int:pk>/', views.delete_blog, name='delete_blog'),
    path('blogs/publish/<int:pk>/', views.publish_blog, name='publish_blog'),
    path('blogs/unpublish/<int:pk>/', views.unpublish_blog, name='unpublish_blog'),
]