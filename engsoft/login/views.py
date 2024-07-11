from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')  # Redirecione para a página principal após o login
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def criar_predio(request):
    nome_predio = None
    if request.method == 'POST':
        nome_predio = request.POST.get('nome_predio')
        endereco_predio = request.POST.get('endereco_predio')
        construtora_id = request.POST.get('construtora_id')

        if nome_predio:
            grupo, created = Group.objects.get_or_create(name=nome_predio)
            
            construtora = Construtora.objects.get(id=construtora_id)
            condominio = Condominio.objects.create(nome=nome_predio, endereco=endereco_predio, construtora=construtora)

    return render(request, 'criarpredio.html', {'nome_predio': nome_predio})

def first(request):
    return render(request, 'first.html')

@login_required
def logoff(request):
    auth_views.LogoutView.as_view()
    return redirect(first)

@login_required
def home(request):
    return render(request, 'home.html')