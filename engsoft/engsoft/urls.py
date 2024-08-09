from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from login import views as li
from assembleia import views as bl

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', li.index, name='index'),
    path('login/', li.login, name='login'),
    path('logout/', li.logoff, name='logout'),
    path('cadastro/', li.cadastro, name='cadastro'),
    
    ##perfil do usuario
    path('editar_perfil/', li.editar_perfil, name='editar_perfil'),
    path('redirect/', li.user_home_redirect, name='user_home_redirect'),

    ##administradora
    path('adm/home/', li.adm_home, name='adm_home'),
    path('adm/meus_condominios/', li.adm_meus_condominios, name='adm_meus_condominios'),
    path('adm/criar_predio/', li.adm_criar_predio, name='adm_criar_predio'),
    path('adm/condominio/<int:condominio_id>/', li.adm_detalhes_condominio, name='adm_detalhes_condominio'),
    path('adm/morador/<int:morador_id>/', li.adm_detalhes_morador, name='adm_detalhes_morador'),
    path('adm/pendentes/', li.adm_pendentes, name='adm_pendentes'),
    path('adm/gerenciar_conta/<int:pk>/', li.adm_gerenciar_morador, name='adm_gerenciar_morador'),
    path('adm/moradores/', li.adm_lista_moradores, name='adm_lista_moradores'),
    path('adm/moradores/editar/<int:usuario_id>/', li.adm_editar_morador, name='adm_editar_morador'),
    path('adm/assembleia/criar/', bl.adm_criar_assembleia, name='adm_criar_assembleia'),
    
    ##moradores
    path('user/home/', li.user_home, name='user_home'),
    
    ##outros usuarios
    path('not_pessoa/home/', li.not_pessoa_home, name='not_pessoa_home'),
    
]
