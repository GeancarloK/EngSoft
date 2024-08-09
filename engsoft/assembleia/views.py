from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assembleia
from .forms import AssembleiaForm
from login.models import Construtora, Condominio
from login.views import user_home_redirect

@login_required
def permissao_construtora(request):
    if not Construtora.objects.filter(administrador=request.user).exists():
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return user_home_redirect(request)

@login_required
def adm_criar_assembleia(request):
    permissao_construtora(request)

    if request.method == 'POST':
        form = AssembleiaForm(request.POST)
        if form.is_valid():
            assembleia = form.save(commit=False)
            construtora = Construtora.objects.get(administrador=request.user)
            assembleia.criado_por = construtora
            assembleia.save()
            messages.success(request, 'Assembleia criada com sucesso.')
            return user_home_redirect(request)
    else:
        form = AssembleiaForm(user=request.user)

    construtora = Construtora.objects.get(administrador=request.user)
    condominios = Condominio.objects.filter(construtora=construtora)

    return render(request, 'adm/assembleia/criar.html', {'form': form, 'condominios': condominios})
