from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from blogs.models import Blog
from .models import Profile
from .forms import ProfileForm
from django.core.paginator import Paginator


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=profile_user)
    published_blogs = Blog.objects.filter(author=profile_user, status='Published').order_by('-updated_at')
    published_count = published_blogs.count()

    paginator = Paginator(published_blogs, 6)
    page_number = request.GET.get('page')
    published_blogs_page = paginator.get_page(page_number)

    context = {
        'profile': profile,
        'profile_user': profile_user,
        'published_blogs': published_blogs_page,
        'published_count': published_count,
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='login')
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'accounts/edit_profile.html', context)