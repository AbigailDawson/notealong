from django.forms import ModelForm, Textarea
from ckeditor.widgets import CKEditorWidget
from .models import Reference, Collection

class CollectionForm(ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'shared']
        widgets = {
            'description': Textarea(attrs={
                'rows': 5,
                'cols': 20
            })
        }

class ReferenceForm(ModelForm):
    class Meta:
        model = Reference
        fields = ['name', 'type']