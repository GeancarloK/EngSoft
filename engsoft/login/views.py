from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User
from django.views import View
from django.http import HttpResponse, JsonResponse
from .models import Construtora, Pessoa, Condominio, NotPessoa
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from . import views
from .forms import PessoaForm, SignUpForm, RequestForm
import json


def index(request):
    return render(request, 'index.html')

@login_required
def logoff(request):
    auth_views.LogoutView.as_view()
    return redirect(index)

def cadastro(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
        else:
            print(form.errors) #debug
    else:
        form = SignUpForm()
    return render(request, 'cadastro.html', {'form': form})

### ADMINISTRADORA

def adm_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            
            # Verificar se o usuário tem uma construtora associada
            if not Construtora.objects.filter(administrador=user).exists():
                return redirect('index')  # Redireciona para a página index se não houver construtora
            
            return redirect('adm_home')
    else:
        form = AuthenticationForm()
    return render(request, 'adm/login.html', {'form': form})

@login_required
def adm_criar_predio(request):
    nome_predio = None
    if request.method == 'POST':
        nome_predio = request.POST.get('nome_predio')
        endereco_predio = request.POST.get('endereco_predio')

        if nome_predio and endereco_predio:
            # Obter a construtora do usuário autenticado
            construtora = get_object_or_404(Construtora, administrador=request.user)
            condominio = Condominio.objects.create(
                nome=nome_predio,
                endereco=endereco_predio,
                construtora=construtora
            )
            return redirect('adm_home')

    return render(request, 'adm/criarpredio.html')



@login_required
def adm_meus_condominios(request):
    # Obter a construtora associada ao usuário autenticado
    try:
        construtora = Construtora.objects.get(administrador=request.user)
    except Construtora.DoesNotExist:
        # Se não encontrar a construtora, você pode redirecionar ou exibir uma mensagem de erro
        construtora = None

    # Filtrar condomínios pela construtora
    condominios = Condominio.objects.filter(construtora=construtora).order_by('nome')

    # Passar os condomínios para o template
    context = {'condominios': condominios}
    return render(request, 'adm/meus_condominios.html', context)


@login_required
def adm_home(request):
    try:
        # Obtém a construtora associada ao usuário
        construtora = Construtora.objects.get(administrador=request.user)
        construtora_nome = construtora.nome
    except Construtora.DoesNotExist:
        construtora_nome = "Nome da Construtora Não Encontrado"

    return render(request, 'adm/home.html', {'construtora_nome': construtora_nome})

def adm_detalhes_condominio(request, condominio_id):
    condominio = get_object_or_404(Condominio, id=condominio_id)
    moradores = Pessoa.objects.filter(condominio=condominio)

    if request.method == 'POST':
        sindico_id = request.POST.get('sindico_id')
        for morador in moradores:
            morador.sindico = (morador.id == int(sindico_id))
            morador.save()

    return render(request, 'adm/detalhes_condominio.html', {
        'condominio': condominio,
        'moradores': moradores
    })

def adm_detalhes_morador(request, morador_id):
    morador = get_object_or_404(Pessoa, pk=morador_id)
    return render(request, 'adm/detalhes_morador.html', {'morador': morador})

def adm_criar_pessoa(request):
    if request.method == 'POST':
        form = PessoaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adm_home')
    else:
        form = PessoaForm()

    return render(request, 'adm/criar_pessoa.html', {'form': form})








### MORADOR
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # Verifica se o usuário está associado a uma construtora
            if Construtora.objects.filter(administrador=user).exists():
                return redirect('adm_home')
            # Verifica se o usuário está associado a um objeto Pessoa
            elif Pessoa.objects.filter(usuario=user).exists():
                return redirect('user_home')
            # Verifica se o usuário está associado a um objeto NotPessoa
            else:
                return redirect('not_pessoa_home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def user_home(request):
    try:
        pessoa = Pessoa.objects.get(usuario=request.user)
    except Pessoa.DoesNotExist:
        pessoa = None

    return render(request, 'user/home.html', {'pessoa': pessoa})

@login_required
def not_pessoa_home(request):
    not_pessoa = get_object_or_404(NotPessoa, usuario=request.user)
    condominios = Condominio.objects.all()

    if request.method == 'POST':
        print(request.POST)
        condominio_id = request.POST.get('condominio')
        print(f"Condomínio ID: {condominio_id}")
        if not condominio_id:
            error_message = "Por favor, selecione um condomínio."
            return render(request, 'not_pessoa/home.html', {
                'not_pessoa': not_pessoa,
                'condominios': condominios,
                'error_message': error_message,
                'pendencia': not_pessoa.pendencia 
            })

        bloco = request.POST.get('bloco')
        andar = request.POST.get('andar')
        apt = request.POST.get('apt')

        try:
            condominio = Condominio.objects.get(id=condominio_id)
        except Condominio.DoesNotExist:
            error_message = "Condomínio selecionado não encontrado."
            return render(request, 'not_pessoa/home.html', {
                'not_pessoa': not_pessoa,
                'condominios': condominios,
                'error_message': error_message,
                'pendencia': not_pessoa.pendencia 
            })

        # Validar bloco, andar e apartamento
        max_blocos = condominio.nro_blocos
        max_andares = condominio.nro_andares
        max_apartamentos = condominio.nro_apt

        if not (1 <= int(bloco) <= max_blocos and 1 <= int(andar) <= max_andares and 1 <= int(apt) <= max_apartamentos):
            error_message = "Os valores selecionados estão fora do intervalo permitido."
            return render(request, 'not_pessoa/home.html', {
                'not_pessoa': not_pessoa,
                'condominios': condominios,
                'error_message': error_message,
                'pendencia': not_pessoa.pendencia
            })

        not_pessoa.pendencia = condominio
        not_pessoa.bloco = bloco
        not_pessoa.andar = andar
        not_pessoa.apt = apt
        not_pessoa.save()

        return redirect('not_pessoa_home')

    return render(request, 'not_pessoa/home.html', {
        'not_pessoa': not_pessoa,
        'condominios': condominios,
        'pendencia': not_pessoa.pendencia
    })

def detalhes_condominio(request, condominio_id):
    condominio = get_object_or_404(Condominio, pk=condominio_id)
    data = {
        'num_blocos': condominio.num_blocos,
        'num_andares': condominio.num_andares,
        'num_apartamentos': condominio.num_apartamentos
    }
    return JsonResponse(data)








### APROVAÇÃO
@login_required
def adm_pendentes(request):
    construtora = get_object_or_404(Construtora, administrador=request.user)
    # Filtrar os NotPessoas cujos condomínios pertencem à construtora do administrador
    pending_registrations = NotPessoa.objects.filter(pendencia__construtora=construtora)

    return render(request, 'adm/pendentes.html', {'pending_registrations': pending_registrations})

@login_required
def adm_aprovar_morador(request, pk):
    not_pessoa = get_object_or_404(NotPessoa, pk=pk)
    if request.method == 'POST':
        Pessoa.objects.create(
            usuario=not_pessoa.usuario,
            nome=not_pessoa.nome,
            email=not_pessoa.email,
            cpf=not_pessoa.cpf,
            bloco=not_pessoa.bloco,
            andar=not_pessoa.andar,
            apt=not_pessoa.apt,
            condominio=not_pessoa.pendencia,
            sindico=False 
        )
        not_pessoa.delete()
        return redirect('adm_pendentes')

    return render(request, 'adm/aprovar_morador.html', {'not_pessoa': not_pessoa})
