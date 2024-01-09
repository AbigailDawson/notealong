from django.forms import ModelForm, Textarea
from .models import Reference, Collection, Note
from tinymce.widgets import TinyMCE

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

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = '__all__'
        widgets = {'content': TinyMCE(attrs={'cols': 20, 'rows': 16})}