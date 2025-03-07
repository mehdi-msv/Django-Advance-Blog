from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

# Get the User model object
User = get_user_model()


class Post(models.Model):
    '''
    This is a class to define posts for blog app
    '''
    
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    image = models.ImageField(blank=True,null=True)
    category = models.ForeignKey("Category",on_delete=models.SET_NULL,null=True)
    title = models.CharField(max_length=256)
    content = models.TextField()
    status = models.BooleanField()
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField()
    
    def __str__(self):
        return self.title

class Category(models.Model):
    
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    