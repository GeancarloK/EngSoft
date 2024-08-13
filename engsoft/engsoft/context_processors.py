from login.models import Construtora, Pessoa, NotPessoa

def user_type_processor(request):
    user_type = 'guest'
    if request.user.is_authenticated:
        if Construtora.objects.filter(administrador=request.user).exists():
            user_type = 'construtora'
        elif Pessoa.objects.filter(usuario=request.user).exists():
            user_type = 'pessoa'
        elif NotPessoa.objects.filter(usuario=request.user).exists():
            user_type = 'not_pessoa'
        else:
            user_type = 'unknown'
    return {'user_type': user_type}
