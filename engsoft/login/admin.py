from django.contrib import admin
from login.models import Condominio, Pessoa, Relatorio, Construtora, NotPessoa

# Register your models here.
admin.site.register(Construtora)
admin.site.register(Pessoa)
admin.site.register(Condominio)
admin.site.register(Relatorio)
admin.site.register(NotPessoa)