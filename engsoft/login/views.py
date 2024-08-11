from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, update_session_auth_hash, get_user_model
from django.contrib.auth import logout
#from django.contrib.auth.models import User
#from django.views import View
from django.http import HttpResponseRedirect, JsonResponse
from .models import Construtora, Pessoa, Condominio, NotPessoa
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
#from django.contrib.auth import views as auth_views
from django.urls import reverse
from urllib.parse import urlencode
from . import views
from .forms import PessoaForm, SignUpForm, ProfileUpdateForm, AdmMoradorForm
from assembleia.models import Assembleia

#import json

User = get_user_model()

def prototipo(request):
    return render(request, 'prototipo.html')

def index(request):
    return render(request, 'index.html')

@login_required
def logoff(request):
    logout(request)
    return redirect('index')

def cadastro(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Após o cadastro, faça login do usuário e redirecione
            auth_login(request, user.usuario)

            query_params = urlencode({'message': 'Usuário criado com sucesso'})
            return redirect(f"{reverse('user_home_redirect')}?{query_params}")
    else:
        form = SignUpForm()
    return render(request, 'cadastro.html', {'form': form})

@login_required
def editar_perfil(request):
    user = request.user
    if hasattr(user, 'pessoa'):
        user_model = user.pessoa
    elif hasattr(user, 'notpessoa'):
        user_model = user.notpessoa
    else:
        return redirect('logoff')

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']

            if not user.check_password(current_password):
                form.add_error('current_password', 'Senha atual incorreta.')
            else:
                # Update user details
                user_model.nome = form.cleaned_data['name']
                user_model.email = form.cleaned_data['email']
                user_model.cpf = form.cleaned_data['cpf']

                if new_password:
                    user.set_password(new_password)
                    update_session_auth_hash(request, user)

                user_model.save()
                # Construir a URL com parâmetros
                query_params = urlencode({'message': 'Perfil atualizado com sucesso'})
                return redirect(f"{reverse('user_home_redirect')}?{query_params}")
    else:
        form = ProfileUpdateForm(initial={
            'name': user_model.nome,
            'email': user_model.email,
            'cpf': user_model.cpf
        })

    return render(request, 'editar_perfil.html', {'form': form})

def user_home_redirect(request):
    message = request.GET.get('message', '')

    if message == 'Usuário criado com sucesso':
        redirect_url = 'login'
    else:
        redirect_url = choose_home(request.user) 

    if redirect_url == 'logoff':
        return redirect('logoff')

    return render(request, 'user_home_redirect.html', {
        'message': message,
        'redirect_url': redirect_url
    })

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

def tornar_sindico(request, pessoa_id):
    pessoa = get_object_or_404(Pessoa, id=pessoa_id)
    
    if pessoa.sindico:
        messages.error(request, "A pessoa já é Síndico.")
        return redirect('adm_lista_moradores')

    condominio = pessoa.condominio
    sindico_atual = Pessoa.objects.filter(condominio=condominio, sindico=True).first()

    if sindico_atual and sindico_atual != pessoa:
        sindico_atual.sindico = False
        sindico_atual.save()

    pessoa.sindico = True
    pessoa.save()

    messages.success(request, "A pessoa foi promovida a Síndico com sucesso.")
    return redirect('adm_lista_moradores')


@login_required
def adm_home(request):
    try:
        # Obtém a construtora associada ao usuário
        construtora = Construtora.objects.get(administrador=request.user)
        construtora_nome = construtora.nome

        # Verifica se há pendências em algum condomínio associado à construtora
        pendencias_existentes = NotPessoa.objects.filter(
            pendencia__in=Condominio.objects.filter(construtora=construtora)
        ).exists()

        # Adiciona a informação ao contexto
        context = {
            'construtora_nome': construtora_nome,
            'pendencias_existentes': pendencias_existentes,
        }

    except Construtora.DoesNotExist:
        context = {'construtora_nome': "Nome da Construtora Não Encontrado", 'pendencias_existentes': False}

    return render(request, 'adm/home.html', context)


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

@login_required
def adm_lista_moradores(request):
    construtora = Construtora.objects.get(administrador=request.user)
    condominios = Condominio.objects.filter(construtora=construtora)
    
    context = {}
    for condominio in condominios:
        pessoas = Pessoa.objects.filter(condominio=condominio).order_by('nome')
        sindico_exists = pessoas.filter(sindico=True).exists()
        context[condominio] = {
            'pessoas': pessoas,
            'sindico_exists': sindico_exists
        }

    return render(request, 'adm/lista_moradores.html', {'context': context})

@login_required
def adm_editar_morador(request, usuario_id):
    pessoa = get_object_or_404(Pessoa, id=usuario_id)
    
    if request.method == 'POST':
        form = AdmMoradorForm(request.POST, instance=pessoa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informações alteradas com sucesso!')
    else:
        form = AdmMoradorForm(instance=pessoa)
    
    return render(request, 'adm/editar_morador.html', {'form': form, 'pessoa': pessoa})

@login_required
def transformar_para_notpessoa(request, pessoa_id):
    if request.method == 'POST':
        pessoa = get_object_or_404(Pessoa, id=pessoa_id)
        
        # Criar o NotPessoa com os dados do Pessoa
        not_pessoa = NotPessoa(
            nome=pessoa.nome,
            email=pessoa.email,
            usuario=pessoa.usuario,
            cpf=pessoa.cpf,

        )
        not_pessoa.save()
        
        # Deletar o objeto Pessoa
        pessoa.delete()
        
        # Redirecionar para a lista de moradores ou onde for apropriado
        return redirect('adm_lista_moradores')
    else:
        return redirect('adm_lista_moradores')









### MORADOR
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            redirect_url = choose_home(user)
            return redirect(redirect_url)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def choose_home(user):
    if Construtora.objects.filter(administrador=user).exists():
        return 'adm_home'
    try:
        pessoa = Pessoa.objects.get(usuario=user)
        if pessoa.condominio:
            return 'user_home'
    except Pessoa.DoesNotExist:
        pass
    if NotPessoa.objects.filter(usuario=user).exists():
        return 'not_pessoa_home'
    
    return 'logoff'

@login_required
def user_home(request):
    try:
        pessoa = Pessoa.objects.get(usuario=request.user)
    except Pessoa.DoesNotExist:
        pessoa = None

    if pessoa:
        # Verifica se há assembleia iniciada no condomínio do morador
        assembleia_iniciada = Assembleia.objects.filter(
            condominio=pessoa.condominio, status='iniciada'
        ).first()  # Pega o primeiro objeto ou None
    else:
        assembleia_iniciada = None

    return render(request, 'user/home.html', {
        'pessoa': pessoa,
        'assembleia_iniciada': assembleia_iniciada,
    })

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
def adm_gerenciar_morador(request, pk):
    not_pessoa = get_object_or_404(NotPessoa, pk=pk)
    
    if request.method == 'POST':
        if 'aprovar' in request.POST:
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
            messages.success(request, f'O morador {not_pessoa.nome} foi aprovado com sucesso.')
            return redirect('adm_pendentes')

        if 'negar' in request.POST:
            not_pessoa.pendencia = None
            not_pessoa.save()
            messages.info(request, f'A requisição de {not_pessoa.nome} foi negada.')
            return redirect('adm_pendentes')
    
    return render(request, 'adm/gerenciar_conta.html', {'not_pessoa': not_pessoa})

@login_required
def excluir_requisicao(request, not_pessoa_id):
    if request.method == 'POST':
        not_pessoa = get_object_or_404(NotPessoa, id=not_pessoa_id)

        not_pessoa.pendencia = None
        not_pessoa.bloco = 1
        not_pessoa.andar = 1
        not_pessoa.apt = 1
        not_pessoa.save()
        
        # Redirecionar para a página desejada após exclusão
    return redirect('not_pessoa_home')  # ou qualquer URL apropriada
