from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Usuario(AbstractUser):
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    

class Grupo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)    
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    criado_em  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
      return self.nome


class Gasto(models.Model):
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10,decimal_places=2)
    pago_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL , null=True)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
      return self.descricao
