from django.contrib import admin
from . models import category , Blog


# Register your models here.

class BlogAdmin (admin.ModelAdmin):
    prepopulated_fields = {'slug':('title', )}
    list_display = ( 'category', 'author','status' ,'is_featured')
    search_fields = ('id' , 'title', 'category__category_name', 'status')
    list_editable = ('is_featured',)


admin.site.register(category)
admin.site.register(Blog, BlogAdmin)
