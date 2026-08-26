from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Blog, category, Tag


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Blog.objects.filter(status='Published').select_related('category', 'author').prefetch_related('tags')

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6

    def items(self):
        return category.objects.all()

    def lastmod(self, obj):
        return obj.updated_At


class TagSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Tag.objects.all()

    def lastmod(self, obj):
        return obj.created_at


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['home', 'search']

    def location(self, item):
        return reverse(item)