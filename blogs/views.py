from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Blog, category, Comment, Like
from .forms import CommentForm
from django.db.models import Q

# Create your views here.

def posts_by_category(request, category_id):
    posts = Blog.objects.filter(status='Published', category=category_id)

    #                                                  use try/except when you want to any coustom action when posts are not found.

    # try:
        # Category = category.objects.get(pk=category_id)
    # except:
    #      return  redirect('home')

    #                                                   use get_object_or_404 when you just want to show a 404 error page.


    Category = get_object_or_404(category, pk=category_id)

    context = {
        'posts': posts,
        'Category': Category,

    }
    return render(request, 'posts_by_category.html', context)


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
    blogs = Blog.objects.filter(Q(title__icontains=keyword) | Q(short_description__icontains=keyword) | Q(blog_body__icontains=keyword), status="Published")
    context = {
        'blogs': blogs,
        'keyword': keyword,
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

    # Only comment author can edit
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

    # Comment author OR blog author can delete
    if comment.author != request.user and comment.blog.author != request.user:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('blogs', slug=comment.blog.slug)

    if request.method == 'POST':
        blog_slug = comment.blog.slug
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
        return redirect('blogs', slug=blog_slug)

    # If GET request, redirect back to blog
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