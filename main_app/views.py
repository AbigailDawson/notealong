import uuid
import boto3
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Collection, Note, Reference
from django.db.models import Q
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import CollectionForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
import os

# Create your views here.

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

@login_required
def collections_index(request):
  all_collections = Collection.objects.filter(user=request.user)
  paginator = Paginator(all_collections, 5)  # Show 5 contacts per page.
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'collections/index.html', {
    'all_collections': all_collections,
    'page_obj': page_obj
    })

@login_required
def collections_detail(request, collection_id):
   all_collections = Collection.objects.filter(user=request.user)
   collection = Collection.objects.get(id=collection_id)
   user = request.user
   return render(request, 'collections/detail.html', {
      'collection': collection,
      'all_collections': all_collections,
      'user': user
   })

def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('home')
    else:
      error_message = 'Invalid sign up - try again'
  form = UserCreationForm()
  context = {'form': form, 'error_messaggit e': error_message}
  return render(request, 'registration/signup.html', context)

class CollectionCreate(LoginRequiredMixin, CreateView):
  model = Collection
  form_class = CollectionForm
  
  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)

class CollectionUpdate(LoginRequiredMixin, UpdateView):
  model = Collection
  form_class = CollectionForm

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
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
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

class ReferenceIndex(LoginRequiredMixin, ListView):
  model = Reference
  template_name = 'main_app/references_index.html'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['references'] = Reference.objects.filter(user=self.request.user)
    return context

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
        form.instance.url = url 
        form.instance.name = name
        form.instance.type = type
        form.instance.user = self.request.user
      except Exception as e:
        print('An error occurred uploading file to S3')
        print(e)
    response = super(ReferenceCreate, self).form_valid(form)
    collection.references.add(self.object)
    return response
  
class ReferenceUpdate(LoginRequiredMixin, UpdateView):
  model = Reference
  fields = ['name', 'type']   
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['all_collections'] = Collection.objects.filter(user=self.request.user)
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
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

@login_required 
def shared_collections_index(request):
  shared_collections = Collection.objects.filter(shared=True)
  paginator = Paginator(shared_collections, 5)  # Show 5 contacts per page.
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'shared_collections/index.html', {
    'shared_collections': shared_collections,
    'page_obj': page_obj
    })

@login_required
def shared_collections_detail(request, collection_id):
   shared_collections = Collection.objects.filter(shared=True)
   collection = Collection.objects.get(id=collection_id)
   return render(request, 'shared_collections/detail.html', {
      'collection': collection,
      'shared_collections': shared_collections,
   })

class SearchResults(LoginRequiredMixin, ListView):
  model = Collection
  template_name = 'main_app/search_results.html'
  paginate_by = 5
  
  def get_queryset(self):
    query = self.request.GET.get('q')
    type = self.request.GET.get('type')
    
    if type == 'search-user':
      print(self.request.user)
      object_list = Collection.objects.filter(Q(user=self.request.user),
        Q(name__icontains=query) | Q(description__icontains=query)
      )
    elif type == 'search-shared':
      object_list = Collection.objects.filter(Q(shared=True) and
        Q(name__icontains=query) | Q(description__icontains=query)
      )
    else:
      # Default case to include all objects if no query string is provided
      object_list = Collection.objects.all()

    return object_list
    
@login_required
def search_results_detail(request, collection_id):
  collection = Collection.objects.get(id=collection_id)
  user = request.user
  return render(request, 'search_results/detail.html', {
    'collection': collection,
    'user': user
  })
