import uuid
import boto3
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Collection, Note, Reference, Profile
from django.db.models import Q, signals
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import CollectionForm, NoteForm, ReferenceForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
import os

# Create your views here.

def home(request):
  if request.user.is_authenticated:
    return redirect('index')
  else:
    return render(request, 'home.html')

@login_required
def collections_index(request):
  all_collections = Collection.objects.filter(user=request.user)
  user = request.user

  sort_by = request.GET.get('sort_by', 'date_created')  # default to date_created
  if sort_by == 'date_created':
    all_collections = all_collections.order_by('-date_created')
  elif sort_by == 'date_updated':
    all_collections = all_collections.order_by('-date_updated')

  paginator = Paginator(all_collections, 5)  # 5 collections per page
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'collections/index.html', {
    'all_collections': page_obj, # pass in the paginated list
    'user': user,
    'page_obj': page_obj,
    'sort_by': sort_by,
    })

@login_required
def collections_detail(request, collection_id):
  all_collections = Collection.objects.filter(user=request.user)
  collection = Collection.objects.get(id=collection_id)
  user_references = Reference.objects.filter(user=request.user)
  user = request.user

  id_list = collection.references.all().values_list('id')
  excluded_references = user_references.exclude(id__in=id_list)

  sort_by = request.GET.get('sort_by', 'date_created') 
  if sort_by == 'date_created':
    all_collections = all_collections.order_by('-date_created')
  elif sort_by == 'date_updated':
    all_collections = all_collections.order_by('-date_updated')

  paginator = Paginator(all_collections, 5)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'collections/detail.html', {
    'collection': collection,
    'all_collections': page_obj, 
    'user': user,
    'page_obj': page_obj,
    'sort_by': sort_by,
    'excluded_references': excluded_references
    })

def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      Profile.objects.create(user=user)
      login(request, user)
      return redirect('home')
    else:
      error_message = 'Invalid sign up - try again'
  form = UserCreationForm()
  
  context = {'form': form, 'error_message': error_message}
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
  form_class = NoteForm

  def get_success_url(self):
    return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['page_obj'] = Collection.objects.filter(user=self.request.user)
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
    return context
  
  def form_valid(self, form):
    collection = Collection.objects.get(id=self.kwargs['collection_id'])
    new_note = form.save(commit=False)
    new_note.save()
    collection.notes.add(new_note)
    collection.save()
    return super().form_valid(form)

class NoteUpdate(LoginRequiredMixin, UpdateView):
  model = Note
  form_class = NoteForm
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['page_obj'] = Collection.objects.filter(user=self.request.user)
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
    return context
  
  def form_valid(self, form):
    collection = Collection.objects.get(id=self.kwargs['collection_id'])
    collection.save()
    return super().form_valid(form)
  
  def get_success_url(self):
    return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})

class NoteDelete(LoginRequiredMixin, DeleteView):
  model = Note

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['all_collections'] = Collection.objects.filter(user=self.request.user)
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
    return context
  
  def form_valid(self, form):
    collection = Collection.objects.get(id=self.kwargs['collection_id'])
    collection.save()
    return super().form_valid(form)
  
  def get_success_url(self):
    return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})

class ReferenceIndex(LoginRequiredMixin, ListView):
  model = Reference
  ref_form = ReferenceForm
  template_name = 'main_app/references_index.html'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['references'] = Reference.objects.filter(user=self.request.user)
    context['ref_form'] = ReferenceForm()
    return context

class ReferenceCreate(LoginRequiredMixin, CreateView):
  model = Reference
  fields = ['name', 'type']

  def get_success_url(self):
    if self.kwargs:
      return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})
    else:
      return reverse('references_index')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['page_obj'] = Collection.objects.filter(user=self.request.user)
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
    return context

  def form_valid(self, form):
    
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

    if self.kwargs.get('collection_id'):
      collection = Collection.objects.get(id=self.kwargs['collection_id']) 
      collection.references.add(self.object)
      collection.save()
    else:
      return response

    return response
  
class ReferenceUpdate(LoginRequiredMixin, UpdateView):
  model = Reference
  fields = ['name', 'type']

  def get_context_data(self, **kwargs): 
    context = super().get_context_data(**kwargs)
    context['page_obj'] = Collection.objects.filter(user=self.request.user)
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
    return context
  
  def form_valid(self, form):
    collection = Collection.objects.get(id=self.kwargs['collection_id'])
    collection.save()
    return super().form_valid(form)

  def get_success_url(self):
    return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})


class ReferencePageUpdate(LoginRequiredMixin,UpdateView):
  model =  Reference
  fields = ['name','type']
  template_name = 'main_app/references_update.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['references'] = Reference.objects.filter(user=self.request.user)
    return context
  
  def form_valid(self, form):
    collection = Collection.objects.get(id=self.kwargs['collection_id'])
    collection.save()
    return super().form_valid(form)
 
  def get_success_url(self):
    return reverse('references_index')


class ReferenceDelete(LoginRequiredMixin, DeleteView):
  model = Reference  

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['all_collections'] = Collection.objects.filter(user=self.request.user)
    context['collection'] = Collection.objects.get(id=self.kwargs['collection_id'])
    return context
  
  def form_valid(self, form):
    collection = Collection.objects.get(id=self.kwargs['collection_id'])
    collection.save()
    return super().form_valid(form)
  
  def get_success_url(self):
    return reverse('detail', kwargs={'collection_id':self.kwargs.get('collection_id')})
  
class ReferencePageDelete(LoginRequiredMixin, DeleteView):
  model = Reference
  template_name = 'main_app/reference_page_confirm_delete.html'

  def get_success_url(self):
    return reverse('references_index')
  
@login_required
def assoc_ref(request, collection_id):
  selected_ref = request.POST.get('selected_ref')
  Collection.objects.get(id=collection_id).references.add(selected_ref)
  return redirect('detail', collection_id=collection_id)
  
@login_required
def unassoc_ref(request, collection_id, reference_id):
  Collection.objects.get(id=collection_id).references.remove(reference_id)
  return redirect('detail', collection_id=collection_id)

@login_required 
def shared_collections_index(request):
  shared_collections = Collection.objects.filter(shared=True)

  sort_by = request.GET.get('sort_by', 'date_created') 
  if sort_by == 'date_created':
    shared_collections = shared_collections.order_by('-date_created')
  elif sort_by == 'date_updated':
    shared_collections = shared_collections.order_by('-date_updated')

  paginator = Paginator(shared_collections, 5)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'shared_collections/index.html', {
    'shared_collections': page_obj, 
    'page_obj': page_obj,
    'sort_by': sort_by,
    })

@login_required
def shared_collections_detail(request, collection_id):
  shared_collections = Collection.objects.filter(shared=True)
  collection = Collection.objects.get(id=collection_id)
  user_references = Reference.objects.filter(user=request.user)
  user = request.user

  id_list = collection.references.all().values_list('id')
  excluded_references = user_references.exclude(id__in=id_list)

  user_profile = Profile.objects.get(user=request.user)
  collections_saved = user_profile.collections_saved.all()

  sort_by = request.GET.get('sort_by', 'date_created') 
  if sort_by == 'date_created':
    shared_collections = shared_collections.order_by('-date_created')
  elif sort_by == 'date_updated':
    shared_collections = shared_collections.order_by('-date_updated')

  paginator = Paginator(shared_collections, 5)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'shared_collections/detail.html', {
    'collection': collection,
    'shared_collections': page_obj, 
    'collections_saved': collections_saved, 
    'user_profile': user_profile,
    'page_obj': page_obj,
    'sort_by': sort_by,
    'user': user,
    'excluded_references': excluded_references
    })

class SearchResults(LoginRequiredMixin, ListView):
  model = Collection
  template_name = 'main_app/search_results.html'
  paginate_by = 5
  
  def get_queryset(self):
    query = self.request.GET.get('q')
    type = self.request.GET.get('type')
    sort_by = self.request.GET.get('sort_by', 'date_created')
    
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

    if sort_by == 'date_created':
      object_list = object_list.order_by('-date_created')
    elif sort_by == 'date_updated':
      object_list = object_list.order_by('-date_updated')
    return object_list
    
@login_required
def search_results_detail(request, collection_id):
  collection = Collection.objects.get(id=collection_id)
  user_references = Reference.objects.filter(user=request.user)
  user = request.user

  id_list = collection.references.all().values_list('id')
  excluded_references = user_references.exclude(id__in=id_list)
  
  return render(request, 'search_results/detail.html', {
    'collection': collection,
    'user': user,
    'excluded_references': excluded_references
  })

@login_required
def saved_collections_index(request):

  user_profile = Profile.objects.get(user=request.user)
  collections_saved = user_profile.collections_saved.all().order_by('-date_created')
  
  user = request.user

  sort_by = request.GET.get('sort_by', 'date_created')
  if sort_by == 'date_created':
    collections_saved = collections_saved.order_by('-date_created')
  elif sort_by == 'date_updated':
    collections_saved = collections_saved.order_by('-date_updated')

  paginator = Paginator(collections_saved, 5)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)

  return render(request, 'saved_collections/index.html', {
    'collections_saved': page_obj,
    'user': user,
    'page_obj': page_obj,
    'sort_by': sort_by,
    })

@login_required
def saved_collections_detail(request, collection_id):
  user = request.user
  user_profile = Profile.objects.get(user=request.user)
  collections_saved = user_profile.collections_saved.all().order_by('-date_created')
  collection = user_profile.collections_saved.get(id=collection_id)

  sort_by = request.GET.get('sort_by', 'date_created') 
  if sort_by == 'date_created':
    collections_saved = collections_saved.order_by('-date_created')
  elif sort_by == 'date_updated':
    collections_saved = collections_saved.order_by('-date_updated')

  paginator = Paginator(collections_saved, 5)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'saved_collections/detail.html', {
    'collection': collection,
    'saved_collections': page_obj, 
    'user': user,
    'page_obj': page_obj,
    'sort_by': sort_by,
    })

@login_required
def saved_collections_add(request, collection_id):
  user_profile = Profile.objects.get(user=request.user)
  collection = Collection.objects.get(id=collection_id)
  user_profile.collections_saved.add(collection)
  user_profile.save()
  
  return redirect('shared_collections_detail',collection_id=collection_id)

@login_required
def saved_collections_remove(request, collection_id):
  user_profile = Profile.objects.get(user=request.user)
  collection = Collection.objects.get(id=collection_id)
  user_profile.collections_saved.remove(collection)
  user_profile.save()
  
  return redirect('shared_collections_detail',collection_id=collection_id)