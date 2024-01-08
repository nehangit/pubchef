from django.db import models
from django.contrib.auth.models import AbstractUser
import string, random

def item_image_path(instance, filename):
    name, ext = filename.split('.')
    filename = ''.join(random.choices(string.ascii_lowercase, k=7))
    return f"itemimages/{filename}.{ext}".format(filename=filename)

def profilepic_image_path(instance, filename):
    name, ext = filename.split('.')
    filename = ''.join(random.choices(string.ascii_lowercase, k=7))
    return f"profilepics/{filename}.{ext}".format(filename=filename)
# Create your models here.
# Add verbose names and help text

class User(AbstractUser):
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    def __str__(self):
        return f"{self.email}"

class Chef(models.Model):
    cuisine = models.CharField(max_length=50)
    profilepic = models.ImageField(upload_to=profilepic_image_path, default='profilepics/default.jpg')
    meanrating = models.DecimalField(max_digits=2, decimal_places=1)
    bio = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    working = models.BooleanField()

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Item(models.Model): # add a count attribute? can use default field to make optional
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    chef = models.ForeignKey(Chef, on_delete=models.CASCADE)
    available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"

# create a table of ratings, with chef and rating attribute 1 to many

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=item_image_path)

    def __str__(self):
        return self.image.url
"""
class ChefImage(models.Model):
    chef = models.OneToOneField(Chef, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=chef_image_path)

    def __str__(self):
        return self.image.url4
"""