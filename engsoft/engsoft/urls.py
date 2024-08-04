from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from login import views as li

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', li.index, name='index'),
    path('login/', li.login, name='login'),
    path('logout/', li.logoff, name='logout'),
    path('cadastro/', li.cadastro, name='cadastro'),

    ##administradora

    path('adm/home/', li.adm_home, name='adm_home'),
    path('adm/meus_condominios/', li.adm_meus_condominios, name='adm_meus_condominios'),
    path('adm/criar_predio/', li.adm_criar_predio, name='adm_criar_predio'),
    path('adm/condominio/<int:condominio_id>/', li.adm_detalhes_condominio, name='adm_detalhes_condominio'),
    path('adm/morador/<int:morador_id>/', li.adm_detalhes_morador, name='adm_detalhes_morador'),
    
    ##moradores
    path('user/home/', li.user_home, name='user_home'),
    
    path('not_pessoa/home/', li.not_pessoa_home, name='not_pessoa_home'),
]
