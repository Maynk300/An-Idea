from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sitemaps.views import sitemap
from .models import Blog, category, Comment, Like, Tag
from .forms import CommentForm
from .sitemaps import BlogSitemap, CategorySitemap, TagSitemap, StaticViewSitemap
from django.db.models import Q, Count, Case, When, IntegerField
from django.core.paginator import Paginator


sitemaps = {
    'blogs': BlogSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'static': StaticViewSitemap,
}


def robots_txt(request):
    """Serve robots.txt for search engine crawlers."""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /login/",
        "Disallow: /logout/",
        "Disallow: /register/",
        "Disallow: /comment/",
        "Disallow: /blogs/*/comment/",
        "Disallow: /blogs/*/like/",
        "Disallow: /blogs/search/",
        "",
        "Sitemap: " + request.build_absolute_uri('/sitemap.xml'),
    ]
    robots_content = "\n".join(lines)
    return HttpResponse(robots_content, content_type="text/plain")


def posts_by_category(request, category_id):
    posts = Blog.objects.filter(status='Published', category=category_id).order_by('-updated_at')

    Category = get_object_or_404(category, pk=category_id)

    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    context = {
        'posts': posts_page,
        'Category': Category,
    }
    return render(request, 'posts_by_category.html', context)


def posts_by_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Blog.objects.filter(status='Published', tags=tag).order_by('-updated_at')

    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    context = {
        'posts': posts_page,
        'Tag': tag,
    }
    return render(request, 'posts_by_tag.html', context)


def blogs(request, slug):
    single_blog = get_object_or_404(
        Blog.objects.select_related('category', 'author').prefetch_related('tags'),
        slug=slug,
        status='Published'
    )
    comments = single_blog.comments.select_related('author').all()
    comment_form = CommentForm()

    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = single_blog.likes.filter(user=request.user).exists()

    related_posts = _get_related_posts(single_blog)

    context = {
        'single_blog': single_blog,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_liked': user_has_liked,
        'related_posts': related_posts,
    }
    return render(request, 'blogs.html', context)


def _get_related_posts(blog):
    """Get up to 4 related published posts based on same category and shared tags."""
    blog_tags = blog.tags.all()

    if not blog_tags and not blog.category_id:
        return Blog.objects.none()

    tag_ids = list(blog_tags.values_list('id', flat=True))

    related = (
        Blog.objects.filter(status='Published')
        .exclude(pk=blog.pk)
        .select_related('category', 'author')
        .prefetch_related('tags')
    )

    if tag_ids:
        related = related.annotate(
            shared_tags_count=Count('tags', filter=Q(tags__id__in=tag_ids))
        )
    else:
        related = related.annotate(shared_tags_count=Count('tags', filter=Q(tags__id__in=[])))

    if blog.category_id:
        related = related.annotate(
            category_match=Case(
                When(category_id=blog.category_id, then=1),
                default=0,
                output_field=IntegerField(),
            )
        )
    else:
        related = related.annotate(category_match=0)

    related = related.annotate(
        relevance_score=Count('tags', filter=Q(tags__id__in=tag_ids)) * 5
        + Case(When(category_id=blog.category_id, then=10), default=0, output_field=IntegerField())
    ).order_by('-relevance_score', '-updated_at')[:4]

    return related


def search(request):
    keyword = request.GET.get("keyword")
    blogs_qs = Blog.objects.filter(
        Q(title__icontains=keyword) |
        Q(short_description__icontains=keyword) |
        Q(blog_body__icontains=keyword) |
        Q(category__category_name__icontains=keyword) |
        Q(tags__name__icontains=keyword),
        status="Published"
    ).distinct().order_by('-updated_at')

    paginator = Paginator(blogs_qs, 6)
    page_number = request.GET.get('page')
    blogs_page = paginator.get_page(page_number)

    query_params = ''
    if keyword:
        query_params = '&keyword=' + keyword

    context = {
        'blogs': blogs_page,
        'keyword': keyword,
        'query_params': query_params,
    }
    return render(request, 'search.html', context)


@login_required(login_url='login')
def add_comment(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status='Published')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        messages.error(request, 'Invalid request.')

    return redirect('blogs', slug=slug)


@login_required(login_url='login')
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.author != request.user:
        messages.error(request, 'You can only edit your own comments.')
        return redirect('blogs', slug=comment.blog.slug)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully.')
            return redirect('blogs', slug=comment.blog.slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = CommentForm(instance=comment)

    context = {
        'form': form,
        'comment': comment,
    }
    return render(request, 'blogs/edit_comment.html', context)


@login_required(login_url='login')
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.author != request.user and comment.blog.author != request.user:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('blogs', slug=comment.blog.slug)

    if request.method == 'POST':
        blog_slug = comment.blog.slug
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
        return redirect('blogs', slug=blog_slug)

    return redirect('blogs', slug=comment.blog.slug)


@login_required(login_url='login')
def like_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status='Published')

    if request.method == 'POST':
        like, created = Like.objects.get_or_create(blog=blog, user=request.user)

        if created:
            messages.success(request, 'You liked this blog.')
        else:
            like.delete()
            messages.success(request, 'You unliked this blog.')

    return redirect('blogs', slug=slug)