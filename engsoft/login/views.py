from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, update_session_auth_hash, get_user_model
from django.contrib.auth import logout
#from django.contrib.auth.models import User
#from django.views import View
from django.http import HttpResponseRedirect, JsonResponse
from .models import Construtora, Pessoa, Condominio, NotPessoa, AreaLazer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
#from django.contrib.auth import views as auth_views
from django.urls import reverse
from urllib.parse import urlencode
from django.utils import timezone
from datetime import timedelta
from .forms import PessoaForm, SignUpForm, ProfileUpdateForm, AdmMoradorForm
from assembleia.models import Assembleia, Ata, Registro

User = get_user_model()

def get_user_type(user):
    if Construtora.objects.filter(administrador=user).exists():
        return 'construtora'
    if Pessoa.objects.filter(usuario=user).exists():
        return 'pessoa'
    if NotPessoa.objects.filter(usuario=user).exists():
        return 'not_pessoa'
    return 'unknown'

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
            'cpf': format_cpf(user_model.cpf)
        })

    return render(request, 'editar_perfil.html', {
        'form': form,
        'user_type': get_user_type(request.user),
        'pessoa': user_model  # Adicionando a variável pessoa ao contexto
    })

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

def redirect_not_pessoa(request):
    message = request.GET.get('message', '')

    if message == 'Usuário criado com sucesso':
        redirect_url = 'login'
    else:
        redirect_url = choose_home(request.user) 

    if redirect_url == 'logoff':
        return redirect('logoff')

    return render(request, 'redirect_not_pessoa.html', {
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
    return render(request, 'adm/login.html', {
        'form': form,
        'user_type': get_user_type(request.user)
    })

@login_required
def adm_criar_predio(request):
    nome_predio = None
    if request.method == 'POST':
        nome_predio = request.POST.get('nome_predio')
        endereco_predio = request.POST.get('endereco_predio')
        nro_blocos = int(request.POST.get('nro_blocos', 1))  # Número de blocos
        nro_andares = int(request.POST.get('nro_andares', 1))  # Número de andares
        nro_apt = int(request.POST.get('nro_apt', 1))  # Número de apartamentos por andar
        nro_lazer = int(request.POST.get('nro_lazer', 0))  # Número de áreas de lazer
        has_acad = request.POST.get('has_acad') == 'on'  # Checkbox da academia
        has_pisc = request.POST.get('has_pisc') == 'on'  # Checkbox da piscina

        if nome_predio and endereco_predio:
            # Obter a construtora do usuário autenticado
            construtora = get_object_or_404(Construtora, administrador=request.user)
            condominio = Condominio.objects.create(
                nome=nome_predio,
                endereco=endereco_predio,
                construtora=construtora,
                nro_blocos=nro_blocos,
                nro_andares=nro_andares,
                nro_apt=nro_apt,
                nro_lazer=nro_lazer,
                has_acad=has_acad,
                has_pisc=has_pisc
            )
            
            # Criar as áreas de lazer
            for i in range(1, nro_lazer + 1):
                AreaLazer.objects.create(
                    num=i,
                    inicio=timezone.now(),
                    fim=timezone.now(),  # Definindo o mesmo horário para início e fim
                    condominio=condominio,
                    pessoa=None  # Ou use `null` se a propriedade for configurada dessa forma
                )
            
            return redirect('adm_home')

    return render(request, 'adm/criarpredio.html', {'user_type': get_user_type(request.user), 'nome_predio': nome_predio})




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
        construtora = Construtora.objects.get(administrador=request.user)
        construtora_nome = construtora.nome

        # Verifica se há pendências em algum condomínio associado à construtora
        pendencias_existentes = NotPessoa.objects.filter(
            pendencia__in=Condominio.objects.filter(construtora=construtora)
        ).exists()

        # Adiciona a informação ao contexto
        context = {
            'construtora_nome': construtora_nome,
            'construtora': construtora,
            'pendencias_existentes': pendencias_existentes,
            'user_type': get_user_type(request.user)
        }

    except Construtora.DoesNotExist:
        context = {
            'construtora_nome': "Nome da Construtora Não Encontrado",
            'construtora': construtora,
            'pendencias_existentes': False,
            'user_type': get_user_type(request.user)
        }

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
        'moradores': moradores,
        'user_type': get_user_type(request.user)
    })

def adm_detalhes_morador(request, morador_id):
    morador = get_object_or_404(Pessoa, pk=morador_id)
    return render(request, 'adm/detalhes_morador.html', {
        'morador': morador,
        'user_type': get_user_type(request.user)
    })

def adm_criar_pessoa(request):
    if request.method == 'POST':
        form = PessoaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adm_home')
    else:
        form = PessoaForm()

    return render(request, 'adm/criar_pessoa.html', {
        'form': form,
        'user_type': get_user_type(request.user)
    })

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
            'sindico_exists': sindico_exists,
            'user_type': get_user_type(request.user)
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
    pessoa.cpf = format_cpf(pessoa.cpf)
    return render(request, 'adm/editar_morador.html', {
        'form': form,
        'pessoa': pessoa,
        'user_type': get_user_type(request.user)
    })

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
        return redirect('not_pessoa_home')
    if pessoa:
        assembleia_criada = Assembleia.objects.filter(
            condominio=pessoa.condominio, status='criada'
        ).first()  # Pega o primeiro objeto ou None

        assembleia_iniciada = Assembleia.objects.filter(
            condominio=pessoa.condominio, status='iniciada'
        ).first()

        assembleia_finalizada = Assembleia.objects.filter(
            condominio=pessoa.condominio, status='finalizada'
        ).first()
        
        # Verifica se há áreas de lazer associadas ao condomínio
        areas_lazer = AreaLazer.objects.filter(condominio=pessoa.condominio).exists()

        assembleia_entregue = Assembleia.objects.filter(
            condominio=pessoa.condominio, status='entregue'
        )

        # Verifica se há atas associadas ao condomínio através dos registros
        if assembleia_entregue is not None:
            registros = Registro.objects.filter(assembleia__in=assembleia_entregue)
            atas_existentes = Ata.objects.filter(id__in=registros.values_list('ata_id', flat=True)).exists()
        else:
            atas_existentes = False
        
    else:
        assembleia_iniciada = None
        areas_lazer = False
        atas_existentes = False

    return render(request, 'user/home.html', {
        'pessoa': pessoa,
        'assembleia_criada': assembleia_criada,
        'assembleia_finalizada': assembleia_finalizada,
        'assembleia_iniciada': assembleia_iniciada,
        'areas_lazer': areas_lazer,
        'atas_existentes': atas_existentes,
        'user_type': get_user_type(request.user)
    })

@login_required
def excluir_morador(request, pessoa_id):
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
        return redirect('not_pessoa_home')
    else:
        return redirect('not_pessoa_home')

@login_required
def atas_list(request):
    try:
        pessoa = Pessoa.objects.get(usuario=request.user)
    except Pessoa.DoesNotExist:
        return redirect('user_home')  # Redireciona se a pessoa não for encontrada

    assembleia_entregue = Assembleia.objects.filter(condominio=pessoa.condominio, status='entregue')
    
    # Captura o termo de pesquisa da query string
    termo_pesquisa = request.GET.get('search', '')

    # Filtra os registros com base no termo de pesquisa
    registros = Registro.objects.filter(
        assembleia__in=assembleia_entregue,
        ata__isnull=False
    ).filter(
        assembleia__titulo__icontains=termo_pesquisa  # Filtra pelo título da assembleia
    ).order_by('-assembleia__data_inicio')

    return render(request, 'user/assembleia/atas.html', {
        'registros': registros,
        'termo_pesquisa': termo_pesquisa  # Passa o termo de pesquisa para o template
    })

@login_required
def areas_lazer_view(request):
    try:
        pessoa = Pessoa.objects.get(usuario=request.user)
        condominio = pessoa.condominio
        is_sindico = pessoa.sindico  # Supondo que 'is_sindico' é o campo que define se a pessoa é síndico
    except Pessoa.DoesNotExist:
        # Redireciona para uma página de erro ou mostra uma mensagem se o usuário não tiver um condomínio
        return render(request, 'error.html', {'message': 'Usuário não associado a nenhum condomínio'})
    
    areas_lazer = AreaLazer.objects.filter(condominio=condominio)
    
    # Cria uma lista de dicionários para passar para o template
    areas_lazer_status = [
        {
            'num': area.num,
            'reservado': area.fim > timezone.now(),  # Verifica se está reservado e ainda é válido     
            'fim': area.fim,
            'nome_pessoa': area.pessoa.nome if area.pessoa else None,  # Supondo que 'nome_completo' é o campo que armazena o nome completo da pessoa
            'id': area.id,
            'bloqueado': area.bloqueado
        }
        for area in areas_lazer
    ]
    print(areas_lazer_status)
    return render(request, 'lazer/lista_areas.html', {
        'areas_lazer_status': areas_lazer_status,
        'is_sindico': is_sindico
    })
    
@login_required
def reservar_area_lazer(request):
    if request.method == 'POST':
        try:
            pessoa = Pessoa.objects.get(usuario=request.user)
        except Pessoa.DoesNotExist:
            return redirect('error')  # Redireciona para uma página de erro

        area_num = request.POST.get('area_num')
        numero = int(request.POST.get('numero'))

        try:
            area = AreaLazer.objects.get(num=area_num, condominio=pessoa.condominio)
        except AreaLazer.DoesNotExist:
            return redirect('error')  # Redireciona para uma página de erro

        if area.pessoa is None or area.fim <= timezone.now():
            # Calcula o horário de término como o horário atual mais o número de horas fornecido
            fim = timezone.now() + timezone.timedelta(hours=numero)
            # Atualiza a área de lazer com o horário de término e o usuário atual
            area.pessoa = pessoa
            area.inicio = timezone.now()
            area.fim = timezone.now() + timezone.timedelta(hours=numero)
            area.save()
        else:
            # Aqui você pode adicionar uma lógica para tratar a situação em que a área já está reservada
            pass

        return redirect('areas_lazer_list')  # Redireciona de volta para a lista de áreas de lazer

    # Para GET ou outros métodos, você pode simplesmente renderizar o template
    areas_lazer = AreaLazer.objects.filter(condominio__pessoa__usuario=request.user)
    areas_lazer_status = [
        {
            'num': area.num,
            'reservado': area.pessoa is not None and area.fim > timezone.now(),
            'fim': area.fim,
            
        }
        for area in areas_lazer
    ]
    
    return render(request, 'lazer/reservar_area.html', {
        'areas_lazer_status': areas_lazer_status
    })

@login_required
def finalizar_reserva(request):
    if request.method == 'POST':
        area_id = request.POST.get('area_id')

        if area_id:
            try:
                area = AreaLazer.objects.get(id=area_id)
                if area.pessoa and area.pessoa.usuario == request.user:
                    area.fim = timezone.now()
                    area.pessoa = None
                    area.save()
                    messages.success(request, 'Reserva finalizada com sucesso.')
                else:
                    messages.error(request, 'Você não tem permissão para finalizar esta reserva.')
            except AreaLazer.DoesNotExist:
                messages.error(request, 'Área de lazer não encontrada.')
        else:
            messages.error(request, 'ID da área de lazer não fornecido.')
    
    return redirect('areas_lazer_list')

@login_required
def bloquear_area_lazer(request, area_id):
    # Verifica se o usuário tem um objeto Pessoa associado e se é síndico
    if not hasattr(request.user, 'pessoa') or not request.user.pessoa.sindico:
        return redirect('user_home')  # Redireciona se o usuário não for síndico

    area = get_object_or_404(AreaLazer, id=area_id)
    area.bloqueado = True
    area.save()

    # Redireciona após o bloqueio
    return redirect(request.META.get('HTTP_REFERER', 'user_home'))

@login_required
def desbloquear_area_lazer(request, area_id):
    # Verifica se o usuário tem um objeto Pessoa associado e se é síndico
    if not hasattr(request.user, 'pessoa') or not request.user.pessoa.sindico:
        return redirect('user_home')  # Redireciona se o usuário não for síndico

    area = get_object_or_404(AreaLazer, id=area_id)
    area.bloqueado = False
    area.save()

    # Redireciona após o desbloqueio
    return redirect(request.META.get('HTTP_REFERER', 'user_home'))

@login_required
def not_pessoa_home(request):
    try:
        not_pessoa = NotPessoa.objects.get(usuario=request.user)
    except NotPessoa.DoesNotExist:
        return redirect('user_home_redirect')
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
                'pendencia': not_pessoa.pendencia,
                'user_type': get_user_type(request.user)
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
        'pendencia': not_pessoa.pendencia,
        'user_type': get_user_type(request.user)
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

    return render(request, 'adm/pendentes.html', {
        'pending_registrations': pending_registrations,
        'user_type': get_user_type(request.user)
    })

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
    not_pessoa.cpf = format_cpf(not_pessoa.cpf)
    return render(request, 'adm/gerenciar_conta.html', {
        'not_pessoa': not_pessoa,
        'user_type': get_user_type(request.user)
    })

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


def format_cpf(value):
    """
    Formata um CPF no formato 123.456.789-01.
    """
    if not value:
        return value
    value = str(value)
    if len(value) == 11:
        return f"{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}"
    return value


### RESERVA
