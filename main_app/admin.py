from django.contrib import admin
from .models import Collection, Reference, Note

# Register your models here.
admin.site.register(Collection)
admin.site.register(Reference)
admin.site.register(Note)