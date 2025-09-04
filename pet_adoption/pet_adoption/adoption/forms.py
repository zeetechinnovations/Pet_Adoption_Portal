from django import forms
from .models import Pet, Message

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'breed', 'age', 'vaccination_status', 'photo', 'pet_type', 'location']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']