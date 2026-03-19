from django.shortcuts import render , redirect , get_object_or_404
from django.http import HttpResponse
from .models import Blog , category
from django.db.models import Q
# Create your views here.

def posts_by_category (request, category_id ):
    posts = Blog.objects.filter(status = 'Published', category = category_id)

 



    #                                                  use try/except when you want to any coustom action when posts are not found.


    # try:
        # Category = category.objects.get(pk=category_id)
    # except:
    #      return  redirect('home') 


    #                                                   use get_object_or_404 when you just want to show a 404 error page.



    Category = get_object_or_404(category ,  pk=category_id)




    context = {
        'posts':posts,
        'Category' : Category,

    }
    return render (request,'posts_by_category.html', context)


def blogs(request, slug):
    single_blog = get_object_or_404(Blog , slug = slug, status = 'Published' , )
    context = {
        'single_blog':single_blog
    }
    return render(request , 'blogs.html' , context)


def search(request):
    keyword = request.GET.get("keyword")
    blogs = Blog.objects.filter(Q(title__icontains=keyword) | Q(short_description__icontains=keyword) | Q(blog_body__icontains=keyword), status="Published" )
    context ={
        'blogs':blogs,
        'keyword':keyword,
    }
    return render(request , 'search.html', context)