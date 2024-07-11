from django.contrib.auth.models import User
from django.db import models

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
    construtora = models.OneToOneField(Construtora, on_delete=models.CASCADE, blank=True, null=True)
    class Meta:
        verbose_name_plural = 'condomínios'
    
    def __str__(self):
        return self.nome
    

class Pessoa(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    condominio = models.ForeignKey(Condominio, on_delete=models.SET_NULL, blank=True, null=True)
    nome = models.CharField(max_length=200)
    data = models.DateTimeField(auto_now_add=True)
    sindico = models.BooleanField("Síndico")
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
