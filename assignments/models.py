from django.db import models

# Create your models here.

class About (models.Model):
    about_hdng = models.CharField(max_length=50)
    about_data = models.TextField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'About'


    def __str__(self):
        return self.about_hdng  
    
class SocialLinks (models.Model):
    plateform = models.CharField(max_length=15)
    link = models.URLField(max_length=100)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.plateform