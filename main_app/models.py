from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Note(models.Model):
  content = models.TextField(blank=False, default='')

class Reference(models.Model):
  FILETYPES = (
    ('I', 'Image'),
    ('P', 'PDF'),
    ('V', 'Video')
  )
  name = models.CharField()
  type = models.CharField(
    max_length=1,
    choices=FILETYPES,
    default =[0][0]
  )
  url = models.CharField(max_length=100)

  def __str__(self):
    return f'{self.name} is a {self.type} file'



class Collection(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField(max_length=300)
  date_created = models.DateTimeField()
  date_updated = models.DateTimeField()
  shared = models.BooleanField(default=False)
  notes = models.ManyToManyField(Note)
  references = models.ManyToManyField(Reference)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  
  def __str__(self):
    return f'{self.name} created on {self.date_created}'

