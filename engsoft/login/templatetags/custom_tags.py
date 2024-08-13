from django import template
from django.contrib.auth.models import User
from login.models import Pessoa, NotPessoa, Construtora

register = template.Library()

@register.simple_tag
def get_user_type(user):
    if user.is_authenticated:
        try:
            Construtora.objects.get(administrador=user)
            return 'construtora'
        except Construtora.DoesNotExist:
            pass
        
        try:
            Pessoa.objects.get(usuario=user)
            return 'pessoa'
        except Pessoa.DoesNotExist:
            pass
        
        try:
            NotPessoa.objects.get(usuario=user)
            return 'not_pessoa'
        except NotPessoa.DoesNotExist:
            pass
    
    return 'none'
