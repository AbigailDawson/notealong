import uuid
import boto3
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Collection, Note, Reference
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import ReferenceForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import os

# Create your views here.

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

@login_required
def collections_index(request):
   all_collections = Collection.objects.filter(user=request.user)
   return render(request, 'collections/index.html', {'all_collections': all_collections})

@login_required
def collections_detail(request, collection_id):
   all_collections = Collection.objects.filter(user=request.user)
   collection = Collection.objects.get(id=collection_id)
   return render(request, 'collections/detail.html', {
      'collection': collection,
      'all_collections': all_collections,
   })

def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('home')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_messaggit e': error_message}
  return render(request, 'registration/signup.html', context)

class CollectionCreate(LoginRequiredMixin, CreateView):
  model = Collection
  fields = ['name', 'description', 'shared']
  
  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)

class CollectionUpdate(LoginRequiredMixin, UpdateView):
   model = Collection
   fields = ['name', 'description','shared']

class CollectionDelete(LoginRequiredMixin, DeleteView):
  model = Collection
  success_url = '/collections'

class NoteCreate(LoginRequiredMixin, CreateView):
  model = Note
  fields = '__all__'

  def get_success_url(self):
    return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['all_collections'] = Collection.objects.filter(user=self.request.user)
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
    return context
  
  def form_valid(self, form):
    collection = Collection.objects.get(id=self.kwargs['collection_id'])
    new_note = form.save(commit=False)
    new_note.save()
    collection.notes.add(new_note)
    return super().form_valid(form)

class NoteUpdate(LoginRequiredMixin, UpdateView):
  model = Note
  fields = '__all__'   
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['all_collections'] = Collection.objects.filter(user=self.request.user)
    return context
  
  def get_success_url(self):
    return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})

class NoteDelete(LoginRequiredMixin, DeleteView):
  model = Note

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['all_collections'] = Collection.objects.filter(user=self.request.user)
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
    return context
  
  def get_success_url(self):
    return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})

class ReferenceCreate(LoginRequiredMixin, CreateView):
  model = Reference
  fields = ['name', 'type']

  def get_success_url(self):
    return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['all_collections'] = Collection.objects.filter(user=self.request.user)
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
    return context

  def form_valid(self, form):
    collection = Collection.objects.get(id=self.kwargs['collection_id'])
    reference_file = self.request.FILES.get('url', None)
    if reference_file:
      s3 = boto3.client('s3')
      key = uuid.uuid4().hex[:6] + reference_file.name[reference_file.name.rfind('.'):]
      try:
        bucket = os.environ['S3_BUCKET']
        s3.upload_fileobj(reference_file, bucket, key)
        url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
        name = self.request.POST['name']
        type = self.request.POST['type']
        new_reference = Reference.objects.create(url=url, name=name, type=type)
        collection.references.add(new_reference)
      except Exception as e:
        print('An error occurred uploading file to S3')
        print(e)
    return super().form_valid(form)
  
class ReferenceUpdate(LoginRequiredMixin, UpdateView):
  model = Reference
  fields = ['name', 'type']   
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['all_collections'] = Collection.objects.filter(user=self.request.user)
    return context
  
  def get_success_url(self):
    return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})

class ReferenceDelete(LoginRequiredMixin, DeleteView):
  model = Reference  

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['all_collections'] = Collection.objects.filter(user=self.request.user)
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
    return context
  
  def get_success_url(self):
    return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})
  
def collections_index(request):
  shared_collections = Collection.objects.filter(shared=True)
  return render(request, 'collections/index.html', {'all_collections': all_collections})