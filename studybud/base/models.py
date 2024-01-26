from django.db import models
from django.contrib.auth.models import AbstractUser

# Customized User Model Start
class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default='avatar.svg')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

# # Customized User Model end

# # Create your models here.
class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True,)
    participants = models.ManyToManyField(User, blank=True, related_name="participants")    #when there is another ManyToMany or OneToMany relationship, to Spcify this relation used "related_name"
    update = models.DateTimeField(auto_now=True)
    create = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-update', '-create']   # rendering data by sorting query data
    
    def __str__(self):
        return self.name
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    update = models.DateTimeField(auto_now=True)
    create = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-update', '-create']
    
    def __str__(self):
        return self.body[0:50]      # we just want first 50 charactar, we don't want hole message
    
