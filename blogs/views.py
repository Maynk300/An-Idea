from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Blog, category, Comment, Like, Tag
from .forms import CommentForm
from django.db.models import Q
from django.core.paginator import Paginator


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
    single_blog = get_object_or_404(Blog, slug=slug, status='Published')
    comments = single_blog.comments.all()
    comment_form = CommentForm()

    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = single_blog.likes.filter(user=request.user).exists()

    context = {
        'single_blog': single_blog,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_liked': user_has_liked,
    }
    return render(request, 'blogs.html', context)


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