from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Note(models.Model):
  content = models.TextField(blank=False, default='')

  def get_absolute_url(self):
    return reverse('detail', kwargs={'collection_id': self.id})

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
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return f'{self.name} is a {self.type} file'

class Collection(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField(max_length=300)
  date_created = models.DateTimeField(default=timezone.now)
  date_updated = models.DateTimeField(default=timezone.now)
  shared = models.BooleanField(default=False)
  notes = models.ManyToManyField(Note, default='')
  references = models.ManyToManyField(Reference, default='')
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return f'{self.name} created on {self.date_created}'

  def get_absolute_url(self):
    return reverse('detail', kwargs={'collection_id': self.id})

  def save(self, *args, **kwargs):
    self.date_updated = timezone.now()
    super().save(*args, **kwargs)

class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  collections_saved = models.ManyToManyField(Collection, default='')

  