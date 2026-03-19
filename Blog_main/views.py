from django.http import HttpResponse
from django.shortcuts import render
from blogs.models import category , Blog
from assignments.models import About


def home(request):
    featured_Post = Blog.objects.filter(is_featured=True , status ='Published').order_by('updated_at')
    recent_post = Blog.objects.filter(is_featured = False, status ='Published')
   
   # fatch  about us

    try:
     about = About.objects.get()
    except:
     about = None  

    context = {
       'featured_Post' : featured_Post,
       'recent_post' : recent_post,
       'about' : about,
    }
    return render(request, 'home.html', context)  