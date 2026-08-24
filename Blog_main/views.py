from django.shortcuts import render, redirect
from django.contrib import messages
from blogs.models import category, Blog
from assignments.models import About
from .forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.core.paginator import Paginator


def home(request):
    featured_Post = Blog.objects.filter(is_featured=True, status='Published').order_by('updated_at')
    recent_post = Blog.objects.filter(is_featured=False, status='Published').order_by('-updated_at')

    # Paginate recent posts
    paginator = Paginator(recent_post, 6)
    page_number = request.GET.get('page')
    recent_post_page = paginator.get_page(page_number)

    # fetch about us
    try:
        about = About.objects.get()
    except About.DoesNotExist:
        about = None

    context = {
        'featured_Post': featured_Post,
        'recent_post': recent_post_page,
        'about': about,
    }
    return render(request, 'home.html', context)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'register.html', context)


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    form = AuthenticationForm()

    context = {
        'form': form
    }
    return render(request, 'login.html', context)


def logout(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')