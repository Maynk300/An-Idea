from django.shortcuts import render , redirect , get_object_or_404
from django.http import HttpResponse
from .models import Blog , category
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
