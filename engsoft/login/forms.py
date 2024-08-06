from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Pessoa, NotPessoa, Condominio
import re

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
    
# Formulário de Cadastro
class SignUpForm(forms.ModelForm):
    username = forms.CharField(label='Usuário', required=True)
    email = forms.EmailField(label='E-mail')
    email2 = forms.EmailField(label='Confirmar E-mail')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Confirmar Senha', widget=forms.PasswordInput, required=True)

    class Meta:
        model = NotPessoa
        fields = ['username',
                  'password',
                  'password2',
                  'email',
                  'email2',
                  'nome',
                  'cpf',
                  ]

    def clean_email2(self):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        if email and email2 and email != email2:
            raise forms.ValidationError("Os e-mails não são iguais")
        return email2

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if not password or not password2:
            raise forms.ValidationError("Deve haver uma senha")
        if password != password2:
            raise forms.ValidationError("As senhas não são iguais")
        if len(password) < 8:
            raise forms.ValidationError("A senha deve ter 8 caracteres no mínimo")
        if len(re.findall(r'\d', password)) < 2:
            raise forms.ValidationError("A senha deve ter pelo menos 2 números")
        return password2

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

    def save(self, commit=True):
        user = User.objects.create_user(username=self.cleaned_data['username'].lower(), password=self.cleaned_data['password'])
        not_pessoa = super(SignUpForm, self).save(commit=False)
        not_pessoa.usuario = user
        if commit:
            not_pessoa.save()
        return not_pessoa
