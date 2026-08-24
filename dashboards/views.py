from django.shortcuts import render, redirect, get_object_or_404
from blogs.models import category, Blog, Tag
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from blogs.forms import BlogForm
from django.core.paginator import Paginator
from django.utils.text import slugify


@login_required(login_url='login')
def dashboard(request):
    category_count = category.objects.all().count()
    blog_count = Blog.objects.all().count()

    context = {
        'category_count': category_count,
        'blog_count': blog_count,
    }
    return render(request, 'dashboard/dashboards.html', context)


@login_required(login_url='login')
def categories(request):
    category_count = category.objects.all().count()
    blog_count = Blog.objects.all().count()

    context = {
        'category_count': category_count,
        'blog_count': blog_count,
    }
    return render(request, 'dashboard/categories.html', context)


@login_required(login_url='login')
def my_blogs(request):
    blogs = Blog.objects.filter(author=request.user).order_by('-updated_at')

    paginator = Paginator(blogs, 10)
    page_number = request.GET.get('page')
    blogs_page = paginator.get_page(page_number)

    context = {
        'blogs': blogs_page,
    }
    return render(request, 'dashboard/my_blogs.html', context)


def _process_tags(tag_string):
    """Parse comma-separated tag string and return list of Tag objects."""
    if not tag_string:
        return []
    tag_names = [name.strip() for name in tag_string.split(',') if name.strip()]
    tags = []
    for name in tag_names:
        slug = slugify(name)
        tag, _ = Tag.objects.get_or_create(name=name, defaults={'slug': slug})
        tags.append(tag)
    return tags


@login_required(login_url='login')
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            # Handle tags
            tag_string = form.cleaned_data.get('tags', '')
            tags = _process_tags(tag_string)
            blog.tags.set(tags)
            messages.success(request, 'Blog created successfully.')
            return redirect('my_blogs')
    else:
        form = BlogForm()
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'dashboard/blog_form.html', context)


@login_required(login_url='login')
def edit_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk, author=request.user)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            # Handle tags
            tag_string = form.cleaned_data.get('tags', '')
            tags = _process_tags(tag_string)
            blog.tags.set(tags)
            messages.success(request, 'Blog updated successfully.')
            return redirect('my_blogs')
    else:
        form = BlogForm(instance=blog)
    context = {
        'form': form,
        'action': 'Edit',
        'blog': blog,
    }
    return render(request, 'dashboard/blog_form.html', context)


@login_required(login_url='login')
def delete_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk, author=request.user)
    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog deleted successfully.')
        return redirect('my_blogs')
    context = {
        'blog': blog,
    }
    return render(request, 'dashboard/blog_confirm_delete.html', context)


@login_required(login_url='login')
def publish_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk, author=request.user)
    blog.status = 'Published'
    blog.save()
    messages.success(request, 'Blog published successfully.')
    return redirect('my_blogs')


@login_required(login_url='login')
def unpublish_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk, author=request.user)
    blog.status = 'Draft'
    blog.save()
    messages.success(request, 'Blog unpublished successfully.')
    return redirect('my_blogs')