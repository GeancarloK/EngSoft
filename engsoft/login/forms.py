from django import forms
from django.contrib.auth.forms import AuthenticationForm

class MeuLoginForm(AuthenticationForm):
    username = forms.CharField(label='Nome de usuário', max_length=254, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
