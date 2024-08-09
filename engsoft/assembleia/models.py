from django.db import models
from django.contrib.auth.models import User
from login.models import Construtora, Condominio, Pessoa

class Assembleia(models.Model):
    STATUS_CHOICES = [
        ('criada', 'Criada'),
        ('iniciada', 'Iniciada'),
        ('finalizada', 'Finalizada'),
        ('entregue', 'Entregue'),
    ]
    
    condominio = models.ForeignKey(Condominio, on_delete=models.CASCADE) 
    titulo = models.CharField(max_length=200)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_finalizacao = models.DateTimeField(null=True, blank=True)
    criado_por = models.ForeignKey(Construtora, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='criada')

    def __str__(self):
        return self.titulo

class Requisicao(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.CharField(max_length=2000)
    assembleia = models.ForeignKey(Assembleia, on_delete=models.CASCADE, related_name='requisicoes')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class OpcaoVotacao(models.Model):
    titulo = models.CharField(max_length=200)
    votacao = models.ForeignKey('Votacao', on_delete=models.CASCADE, related_name='opcoes_votacao')
    votos = models.IntegerField(default=0)  

    def __str__(self):
        return self.titulo

class Votacao(models.Model):
    titulo = models.CharField(max_length=200)
    assembleia = models.ForeignKey(Assembleia, on_delete=models.CASCADE, related_name='votos')
    opcoes = models.ManyToManyField(OpcaoVotacao, related_name='votacoes')

    def __str__(self):
        return self.titulo

class Voto(models.Model):
    votacao = models.ForeignKey(Votacao, on_delete=models.CASCADE, related_name='votos')
    morador = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    opcao = models.ForeignKey(OpcaoVotacao, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('votacao', 'morador')

    def __str__(self):
        return f"{self.morador} votou em {self.opcao.titulo} na votação {self.votacao.titulo}"

class Registro(models.Model):
    assembleia = models.ForeignKey(Assembleia, on_delete=models.CASCADE, related_name='registros')
    resumo = models.TextField()
    data_criacao = models.DateTimeField(null=True, blank=True)
    data_finalizacao = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Registro de {self.assembleia.titulo}"