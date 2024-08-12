from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
import re

class Construtora(models.Model):
    nome = models.CharField(max_length=200)
    endereco = models.CharField(max_length=200, default="default")
    data = models.DateTimeField(auto_now_add=True)
    administrador = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    class Meta:
        verbose_name_plural = 'construtoras'
    
    def __str__(self):
        return self.nome

class Condominio(models.Model):
    nome = models.CharField(max_length=200)
    endereco = models.CharField(max_length=200, default="default")
    data = models.DateTimeField(auto_now_add=True)
    construtora = models.ForeignKey(Construtora, on_delete=models.CASCADE, blank=True, null=True)
    nro_blocos = models.IntegerField(default=1)
    nro_andares = models.IntegerField(default=1)
    nro_apt = models.IntegerField(default=1)
    nro_lazer = models.IntegerField(default=0)
    has_acad = models.BooleanField(default=False)
    has_pisc = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'condomínios'
    
    def __str__(self):
        return self.nome

def validate_cpf(value):
    if not re.match(r'^\d{11}$', value):
        raise ValidationError('CPF deve conter exatamente 11 dígitos numéricos.')
    
def validate_bloco(value, condominio):
    if value < 1 or value > condominio.nro_blocos:
        raise ValidationError(f'Bloco deve ser entre 1 e {condominio.nro_blocos}.')

def validate_andar(value, condominio):
    if value < 1 or value > condominio.nro_andares:
        raise ValidationError(f'Andar deve ser entre 1 e {condominio.nro_andares}.')

def validate_apt(value, condominio):
    if value < 1 or value > condominio.nro_apt:
        raise ValidationError(f'Apartamento deve ser entre 1 e {condominio.nro_apt}.')

class Pessoa(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    condominio = models.ForeignKey(Condominio, on_delete=models.SET_NULL, blank=True, null=True)
    nome = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    data = models.DateTimeField(auto_now_add=True)
    cpf = models.CharField(max_length=11, validators=[validate_cpf], default = "00000000000")
    sindico = models.BooleanField("Síndico")
    bloco = models.IntegerField(default = 1)
    andar = models.IntegerField(default = 1)
    apt = models.IntegerField(default = 1)

    def clean(self):
        if self.condominio:
            if self.bloco < 1 or self.bloco > self.condominio.nro_blocos:
                raise ValidationError(f'O bloco deve estar entre 1 e {self.condominio.nro_blocos}.')
            if self.andar < 1 or self.andar > self.condominio.nro_andares:
                raise ValidationError(f'O andar deve estar entre 1 e {self.condominio.nro_andares}.')
            if self.apt < 1 or self.apt > self.condominio.nro_apt:
                raise ValidationError(f'O apartamento deve estar entre 1 e {self.condominio.nro_apt}.')
            
    class Meta:
        verbose_name_plural = 'pessoas'

    def __str__(self):
        return self.nome
    
class Relatorio(models.Model):
    titulo = models.CharField(max_length=200)
    data = models.DateTimeField(auto_now_add=True)
    texto = models.TextField()
    condominio = models.ForeignKey(Condominio, on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = 'relatorios'

    def __str__(self):
        return self.titulo
    
class NotPessoa(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    data = models.DateTimeField(auto_now_add=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    pendencia = models.ForeignKey(Condominio, on_delete=models.SET_NULL, blank=True, null=True)
    cpf = models.CharField(max_length=11, validators=[validate_cpf], default = "00000000000")
    bloco = models.IntegerField(default = 1)
    andar = models.IntegerField(default = 1)
    apt = models.IntegerField(default = 1)

    class Meta:
        verbose_name_plural = 'not_pessoas'

    def __str__(self):
        return self.nome
    


class AreaLazer(models.Model):
    num = models.IntegerField(default=0)
    condominio = models.ForeignKey('Condominio', on_delete=models.CASCADE, related_name='areas_lazer_condominio')
    pessoa = models.ForeignKey('Pessoa', on_delete=models.CASCADE, related_name='areas_lazer_pessoa', blank=True, null=True)
    inicio = models.DateTimeField(default=timezone.now)
    fim = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = 'areas de lazer'

    def __str__(self):
        return f'{self.condominio.nome} - {self.num}'
