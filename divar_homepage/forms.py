from django import forms

__all__ = ('ChatForm', )



class ChatForm(forms.Form):
    state = forms.CharField(widget=forms.HiddenInput(), required=True)
    message = forms.CharField(widget=forms.Textarea(), required=True)

class PhoneForm(forms.Form):
    state = forms.CharField(widget=forms.HiddenInput(), required=True)