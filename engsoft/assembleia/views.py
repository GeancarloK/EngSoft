from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.template.defaulttags import register
from .models import Votacao, Assembleia, Registro, OpcaoVotacao, Requisicao, Voto
from .forms import AssembleiaForm
from login.models import Construtora, Condominio, Pessoa
from login.views import user_home_redirect

@login_required
def permissao_construtora(request):
    try:
        Construtora.objects.get(administrador=request.user)
    except Construtora.DoesNotExist:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return user_home_redirect(request)

@login_required
def adm_criar_assembleia(request):
    permissao_construtora(request)

    if request.method == 'POST':
        form = AssembleiaForm(request.POST)
        if form.is_valid():
            assembleia = form.save(commit=False)
            try:
                construtora = Construtora.objects.get(administrador=request.user)
                assembleia.criado_por = construtora
                assembleia.save()
                messages.success(request, 'Assembleia criada com sucesso.')
                return redirect('home_assembleias')  # Redireciona para a página inicial do administrador
            except Construtora.DoesNotExist:
                messages.error(request, 'Você não tem uma construtora associada. Verifique sua conta.')
                return redirect('user_home')  # Ou qualquer outra página de erro apropriada
    else:
        form = AssembleiaForm()

    try:
        construtora = Construtora.objects.get(administrador=request.user)
        condominios = Condominio.objects.filter(construtora=construtora)
    except Construtora.DoesNotExist:
        condominios = []

    return render(request, 'adm/assembleia/criar.html', {'form': form, 'condominios': condominios})

@login_required
def adm_criar_votacao(request):
    if request.method == 'POST':
        titulo = request.POST['titulo']
        assembleia = Assembleia.objects.get(id=request.session['assembleia_id']) # Exemplo de como associar a votação a uma assembleia específica
        Votacao.objects.create(titulo=titulo, assembleia=assembleia)
        messages.success(request, 'Votação criada com sucesso.')
        return redirect('adm_home')  # Redirecionar para a página inicial do síndico ou onde você preferir

    return render(request, 'adm/assembleia/criar_votacao.html')





### SINDICO
@login_required
def permissao_sindico(request):
    if not Pessoa.objects.filter(usuario=request.user, sindico=True).exists():
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return user_home_redirect(request)
    
@login_required
def sindico_assembleias(request):
    permissao_sindico(request)
    
    pessoa = Pessoa.objects.get(usuario=request.user, sindico=True)
    condominio = pessoa.condominio
    assembleias = Assembleia.objects.filter(condominio=condominio).exclude(status='entregue')

    if not assembleias.exists():
        messages.info(request, 'Não há assembleias acontecendo no momento.')
        return render(request, 'user/assembleia/sindico.html', {'assembleias': None})
    
    return render(request, 'user/assembleia/sindico.html', {'assembleias': assembleias})

@login_required
def iniciar_assembleia(request, assembleia_id):
    permissao_sindico(request)
    assembleia = get_object_or_404(Assembleia, id=assembleia_id)
    assembleia.status = 'iniciada'
    assembleia.data_inicio = timezone.now()
    assembleia.save()
    return redirect('sindico_assembleias')

@login_required
def finalizar_assembleia(request, assembleia_id):
    permissao_sindico(request)
    assembleia = get_object_or_404(Assembleia, id=assembleia_id)
    assembleia.status = 'finalizada'
    assembleia.data_finalizacao = timezone.now()
    assembleia.save()
    return redirect('sindico_assembleias')

@login_required
def entregar_assembleia(request, assembleia_id):
    permissao_sindico(request)
    assembleia = get_object_or_404(Assembleia, id=assembleia_id)
    if request.method == 'POST':
        resumo = request.POST.get('resumo')

        detalhes_votacoes = []
        for votacao in assembleia.votos.all():
            detalhes_votacao = f"Votação: {votacao.titulo}\n"
            for opcao in votacao.opcoes_votacao.all():
                detalhes_votacao += f" - Opção: {opcao.titulo} recebeu {opcao.votos} votos\n"

            participantes = Voto.objects.filter(votacao=votacao).values_list('morador__usuario__username', flat=True).distinct()
            detalhes_votacao += "Participantes:\n" + "\n".join(participantes) + "\n"

            detalhes_votacoes.append(detalhes_votacao)

        relatorio_completo = resumo + "\n\nDetalhes das Votações:\n" + "\n".join(detalhes_votacoes)
        print(f"Relatório completo: {relatorio_completo}")

        if resumo:
            registro = Registro.objects.create(assembleia=assembleia, resumo=relatorio_completo, data_criacao=timezone.now())
            assembleia.status = 'entregue'
            assembleia.save()
            return redirect('sindico_assembleias')
        else:
            messages.error(request, "Resumo não fornecido.")
    
    return render(request, 'user/assembleia/home.html', {'assembleia': assembleia})



@login_required
def criar_votacao(request, assembleia_id):
    assembleia = get_object_or_404(Assembleia, id=assembleia_id)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        opcoes = request.POST.getlist('opcao')

        if titulo and len(opcoes) >= 2:
            votacao = Votacao.objects.create(titulo=titulo, assembleia=assembleia)
            
            for opcao in opcoes:
                opcao = opcao.strip()
                if opcao:  # Verifica se a opção não está vazia
                    OpcaoVotacao.objects.create(titulo=opcao, votacao=votacao)

            return redirect('sindico_assembleias')
        else:
            # Se menos de 2 opções, adicione uma mensagem de erro
            error_message = 'Você deve fornecer pelo menos duas opções.'
            return render(request, 'user/assembleia/votacao/criar.html', {'assembleia': assembleia, 'error_message': error_message})

    return render(request, 'user/assembleia/votacao/criar.html', {'assembleia': assembleia})

@login_required
def entrar_assembleia(request, assembleia_id):
    assembleia = get_object_or_404(Assembleia, id=assembleia_id)

    # Adicione a lógica necessária para a página da assembleia
    return render(request, 'user/assembleia/morador.html', {'assembleia': assembleia})

@login_required
def home_assembleias(request):
    permissao_construtora(request)
    
    try:
        construtora = Construtora.objects.get(administrador=request.user)
    except Construtora.DoesNotExist:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('user_home')  # Ajuste a URL para onde você quer redirecionar

    condominios = Condominio.objects.filter(construtora=construtora)
    assembleias = Assembleia.objects.filter(
        condominio__in=condominios
    ).select_related('criado_por').prefetch_related('registros')

    # Filtrando assembleias por status
    criada_assembleias = assembleias.filter(status='criada').order_by('data_criacao')
    iniciada_assembleias = assembleias.filter(status='iniciada').order_by('data_criacao')
    finalizada_assembleias = assembleias.filter(status='finalizada').order_by('data_criacao')
    entregue_assembleias = assembleias.filter(status='entregue').order_by('data_criacao')
    
    context = {
        'criada_assembleias': criada_assembleias,
        'iniciada_assembleias': iniciada_assembleias,
        'finalizada_assembleias': finalizada_assembleias,
        'entregue_assembleias': entregue_assembleias,
    }
    return render(request, 'adm/assembleia/home.html', context)



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

###MORADOR
@login_required
def user_assembleias(request):
    try:
        pessoa = Pessoa.objects.get(usuario=request.user)
        assembleias = Assembleia.objects.filter(condominio=pessoa.condominio, status='iniciada')

        votos_existentes = {}
        for assembleia in assembleias:
            votacoes = Votacao.objects.filter(assembleia=assembleia)
            for votacao in votacoes:
                votos = Voto.objects.filter(votacao=votacao, morador=pessoa)
                votos_existentes[votacao.id] = votos.values_list('opcao_id', flat=True).first()

        if request.method == 'POST':
            action = request.POST.get('action')
            assembleia_id = request.POST.get('assembleia_id')
            print("Assembleia ID recebido:", assembleia_id)  # Verifique o ID aqui

            try:
                assembleia = Assembleia.objects.get(id=assembleia_id)
            except Assembleia.DoesNotExist:
                messages.error(request, 'A assembleia selecionada não existe.')
                return redirect('user_assembleias')

            if action == 'fazer_requisicao':
                context = {
                    'assembleias': assembleias,
                    'pessoa': pessoa,
                    'votos_existentes': votos_existentes,
                    'form_mostrar': True,
                }
                return render(request, 'user/assembleia/morador.html', context)
                
            elif action == 'enviar_requisicao':
                titulo = request.POST.get('titulo')
                descricao = request.POST.get('descricao')

                Requisicao.objects.create(
                    titulo=titulo,
                    descricao=descricao,
                    assembleia=assembleia,
                )

                messages.success(request, 'Requisição feita com sucesso!')
                return redirect('user_assembleias')
                
            elif action == 'cancelar_form':
                return redirect('user_assembleias')

        context = {
            'assembleias': assembleias,
            'pessoa': pessoa,
            'votos_existentes': votos_existentes,
        }
        return render(request, 'user/assembleia/morador.html', context)

    except Pessoa.DoesNotExist:
        messages.error(request, 'Você não está associado a nenhum condomínio.')
        return redirect('user_home_redirect')



@login_required
def user_votar(request):
    if request.method == 'POST':
        votacao_id = request.POST.get('votacao_id')
        opcao_id = request.POST.get('opcao_id')

        if not opcao_id:
            messages.error(request, 'Por favor, selecione uma opção antes de votar.')
            return redirect('user_assembleias')

        votacao = Votacao.objects.get(id=votacao_id)
        opcao = OpcaoVotacao.objects.get(id=opcao_id)
        pessoa = Pessoa.objects.get(usuario=request.user)

        voto, created = Voto.objects.get_or_create(
            votacao=votacao,
            morador=pessoa,
            defaults={'opcao': opcao}
        )

        if not created:
            messages.error(request, 'Você já votou nesta votação.')
        else:
            opcao.votos += 1
            opcao.save()
            messages.success(request, 'Voto registrado com sucesso!')

        return redirect('user_assembleias')

