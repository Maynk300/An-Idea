from django.shortcuts import render, redirect, get_object_or_404
from blogs.models import category, Blog
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Blog_main.forms import BlogForm


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
    context = {
        'blogs': blogs,
    }
    return render(request, 'dashboard/my_blogs.html', context)


@login_required(login_url='login')
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
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