from django.contrib import admin
from login.models import Condominio, Pessoa, Construtora, NotPessoa, AreaLazer

# Register your models here.
admin.site.register(Construtora)
admin.site.register(Pessoa)
admin.site.register(Condominio)
admin.site.register(NotPessoa)
admin.site.register(AreaLazer)