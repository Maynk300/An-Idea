"""
URL configuration for Blog_main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from blogs import views as BlogsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home , name='home'),
    path('category/',include('blogs.urls') ),
    path('blogs/<slug:slug>/', BlogsView.blogs , name='blogs'),
    path('blogs/<slug:slug>/comment/', BlogsView.add_comment , name='add_comment'),
    path('blogs/<slug:slug>/like/', BlogsView.like_blog , name='like_blog'),
    path('blogs/search/',BlogsView.search, name='search'),
    path('register/', views.register, name='register'),
    path('login/',views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('comment/<int:comment_id>/edit/', BlogsView.edit_comment , name='edit_comment'),
    path('comment/<int:comment_id>/delete/', BlogsView.delete_comment , name='delete_comment'),

# Dashboards
    
    path('dashboard/',include('dashboards.urls')),

# Accounts
    
    path('', include('accounts.urls')),


] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
