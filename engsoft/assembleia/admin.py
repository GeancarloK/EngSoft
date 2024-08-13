from django.contrib import admin
from .models import Assembleia, Registro, Requisicao, OpcaoVotacao, Votacao, Voto, Ata

# Register your models here.
admin.site.register(Assembleia)
admin.site.register(Registro)
admin.site.register(Requisicao)
admin.site.register(OpcaoVotacao)
admin.site.register(Votacao)
admin.site.register(Voto)
admin.site.register(Ata)