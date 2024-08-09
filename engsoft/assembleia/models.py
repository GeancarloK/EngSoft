from django.db import models
from django.contrib.auth.models import User
from login.models import Construtora, Condominio, Pessoa

class Assembleia(models.Model):
    STATUS_CHOICES = [
        ('criada', 'Criada'),
        ('iniciada', 'Iniciada'),
        ('finalizada', 'Finalizada'),
    ]
    
    condominio = models.ForeignKey(Condominio, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_finalizacao = models.DateTimeField(null=True, blank=True)
    criado_por = models.ForeignKey(Construtora, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='criada')

    def __str__(self):
        return self.titulo

class Pauta(models.Model):
    assembleia = models.ForeignKey(Assembleia, on_delete=models.CASCADE, related_name='pautas')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Votacao(models.Model):
    pauta = models.ForeignKey(Pauta, on_delete=models.CASCADE, related_name='votacoes')
    voto_sim = models.IntegerField(default=0)
    voto_nao = models.IntegerField(default=0)
    voto_abstencao = models.IntegerField(default=0)

    def total_votos(self):
        return self.voto_sim + self.voto_nao + self.voto_abstencao

    def __str__(self):
        return f"Votação para {self.pauta.titulo}"

class Registro(models.Model):
    assembleia = models.ForeignKey(Assembleia, on_delete=models.CASCADE, related_name='registros')
    resumo = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Registro de {self.assembleia.titulo}"