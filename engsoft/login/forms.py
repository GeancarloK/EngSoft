from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Pessoa, NotPessoa, Condominio

# Funções de validação
def validate_bloco(bloco, condominio):
    if bloco < 1 or bloco > condominio.nro_blocos:
        raise ValidationError(f'O bloco deve estar entre 1 e {condominio.nro_blocos}.')

def validate_andar(andar, condominio):
    if andar < 1 or andar > condominio.nro_andares:
        raise ValidationError(f'O andar deve estar entre 1 e {condominio.nro_andares}.')

def validate_apt(apt, condominio):
    if apt < 1 or apt > condominio.nro_apt:
        raise ValidationError(f'O apartamento deve estar entre 1 e {condominio.nro_apt}.')

# Formulário de Login
class MeuLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nome de usuário', 
        max_length=254, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Senha', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

# Formulário Pessoa
class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = ['nome', 'cpf', 'condominio', 'sindico', 'bloco', 'andar', 'apt']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'condominio': forms.Select(attrs={'class': 'form-control'}),
            'sindico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bloco': forms.NumberInput(attrs={'class': 'form-control'}),
            'andar': forms.NumberInput(attrs={'class': 'form-control'}),
            'apt': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        condominio = cleaned_data.get('condominio')
        bloco = cleaned_data.get('bloco')
        andar = cleaned_data.get('andar')
        apt = cleaned_data.get('apt')

        if condominio:
            if bloco is not None:
                validate_bloco(bloco, condominio)
            if andar is not None:
                validate_andar(andar, condominio)
            if apt is not None:
                validate_apt(apt, condominio)

        return cleaned_data

# Formulário de Registro de Usuário
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmar Senha')

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('As senhas não coincidem.')

        return cleaned_data

# Formulário NotPessoa
class NotPessoaForm(forms.ModelForm):
    class Meta:
        model = NotPessoa
        fields = ['nome', 'email', 'cpf', 'bloco', 'andar', 'apt', 'pendencia']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'bloco': forms.NumberInput(attrs={'class': 'form-control'}),
            'andar': forms.NumberInput(attrs={'class': 'form-control'}),
            'apt': forms.NumberInput(attrs={'class': 'form-control'}),
            'pendencia': forms.Select(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        condominio = cleaned_data.get('pendencia')
        bloco = cleaned_data.get('bloco')
        andar = cleaned_data.get('andar')
        apt = cleaned_data.get('apt')

        if condominio:
            if bloco is not None:
                validate_bloco(bloco, condominio)
            if andar is not None:
                validate_andar(andar, condominio)
            if apt is not None:
                validate_apt(apt, condominio)

        return cleaned_data
