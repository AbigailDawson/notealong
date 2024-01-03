from django.shortcuts import render, redirect
from .models import Collection, Note
from django.views.generic.edit import CreateView, UpdateView, DeleteView
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
  fields = ['name', 'description']
  
  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)

class CollectionUpdate(LoginRequiredMixin, UpdateView):
   model = Collection
   fields = ['name', 'description']

class CollectionDelete(LoginRequiredMixin, DeleteView):
  model = Collection
  success_url = '/collections'

class NoteCreate(LoginRequiredMixin, CreateView):
  model = Note
  fields = '__all__'

class NoteUpdate(LoginRequiredMixin, UpdateView):
   model = Note
   fields = '__all__'

class NoteDelete(LoginRequiredMixin, DeleteView):
   model = Note
   success_url = '/collections'