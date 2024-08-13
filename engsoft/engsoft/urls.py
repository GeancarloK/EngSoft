from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from login import views as li
from assembleia import views as bl

urlpatterns = [
    path('admin/', admin.site.urls),

    ##temporário
    path('prototipo/', li.prototipo, name='prototipo'),

    path('', li.index, name='index'),
    path('login/', li.login, name='login'),
    path('logout/', li.logoff, name='logout'),
    path('cadastro/', li.cadastro, name='cadastro'),
    
    ##perfil do usuario
    path('editar_perfil/', li.editar_perfil, name='editar_perfil'),
    path('redirect/', li.user_home_redirect, name='user_home_redirect'),
    path('redirect_not_pessoa/', li.redirect_not_pessoa, name='redirect_not_pessoa'),

    ##administradora
    path('adm/home/', li.adm_home, name='adm_home'),
    path('adm/meus_condominios/', li.adm_meus_condominios, name='adm_meus_condominios'),
    path('adm/criar_predio/', li.adm_criar_predio, name='adm_criar_predio'),
    path('adm/condominio/<int:condominio_id>/', li.adm_detalhes_condominio, name='adm_detalhes_condominio'),
    path('adm/morador/<int:morador_id>/', li.adm_detalhes_morador, name='adm_detalhes_morador'),
    path('adm/pendentes/', li.adm_pendentes, name='adm_pendentes'),
    path('adm/gerenciar_conta/<int:pk>/', li.adm_gerenciar_morador, name='adm_gerenciar_morador'),
    path('adm/moradores/', li.adm_lista_moradores, name='adm_lista_moradores'),
    path('adm/moradores/sindico/<int:pessoa_id>', li.tornar_sindico, name='adm_tornar_sindico'),
    path('adm/moradores/editar/<int:usuario_id>/', li.adm_editar_morador, name='adm_editar_morador'),
    path('adm/morador/transformar/<int:pessoa_id>/', li.transformar_para_notpessoa, name='transformar_para_notpessoa'),
    path('adm/assembleia/', bl.home_assembleias, name='home_assembleias'),
    path('adm/assembleia/<int:condominio_id>/', bl.home_assembleias_condominio, name='home_assembleias_condominio'),
    path('adm/assembleia/criar/', bl.adm_criar_assembleia, name='adm_criar_assembleia'),
    path('adm/assembleia/criar/<int:condominio_id>/', bl.criar_assembleia_id, name='adm_criar_assembleia'),
    path('adm/enviar_ata/<int:assembleia_id>/', bl.enviar_ata, name='enviar_ata'),
    
    ##moradores
    path('user/home/', li.user_home, name='user_home'),
    path('user/assembleias/', bl.user_assembleias, name='user_assembleias'),
    path('user/assembleias/votar/', bl.user_votar, name='user_votar'),
    path('user/areas-lazer/', li.areas_lazer_view, name='areas_lazer_list'),
    path('user/reservar-area-lazer/', li.reservar_area_lazer, name='reservar_area_lazer'),
    path('user/finalizar-reserva/', li.finalizar_reserva, name='finalizar_reserva'),
    path('user/atas/', li.atas_list, name='atas_list'),
    path('user/excluir/<int:pessoa_id>/', li.excluir_morador, name='excluir_morador'),

    ##sindico
    path('user/assembleia/sindico/', bl.sindico_assembleias, name='sindico_assembleias'),
    path('user/assembleia/iniciar/<int:assembleia_id>/', bl.iniciar_assembleia, name='iniciar_assembleia'),
    path('user/assembleia/finalizar/<int:assembleia_id>/', bl.finalizar_assembleia, name='finalizar_assembleia'),
    path('user/assembleia/entregar/<int:assembleia_id>/', bl.entregar_assembleia, name='entregar_assembleia'),
    path('user/assembleia/votacao/criar/<int:assembleia_id>/', bl.criar_votacao, name='criar_votacao'),
    path('user/entrar_assembleia/<int:assembleia_id>/', bl.entrar_assembleia, name='entrar_assembleia'),
    path('user/areas-lazer/bloquear/<int:area_id>/', li.bloquear_area_lazer, name='bloquear_area_lazer'),
    path('user/areas-lazer/desbloquear/<int:area_id>/', li.desbloquear_area_lazer, name='desbloquear_area_lazer'),
    
    
    ##outros usuarios
    path('not_pessoa/home/', li.not_pessoa_home, name='not_pessoa_home'),
    path('excluir-requisicao/<int:not_pessoa_id>/', li.excluir_requisicao, name='excluir_requisicao'),
    
]
