from django.forms import ModelForm, CharField
from ckeditor.widgets import CKEditorWidget
from .models import Reference

class ReferenceForm(ModelForm):
    class Meta:
        model = Reference
        fields = ['name', 'type']