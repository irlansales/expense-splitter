# groups/models.py
# Este arquivo define os modelos (tabelas do banco de dados) do app groups.
# Em Django, cada classe que herda de models.Model vira uma tabela no banco.

from django.db import models
from django.contrib.auth.models import User


# Group representa um grupo de pessoas que dividem despesas
# Ex: "Viagem pra SP", "República", "Churrasco"
class Group(models.Model):

    # ===== CHOICES =====
    # Choices são listas de opções válidas para um campo.
    # O formato é uma lista de tuplas: (valor_no_banco, texto_para_humanos)
    # O valor_no_banco é o que fica salvo no SQLite.
    # O texto_para_humanos aparece nos formulários e no admin.
    CATEGORIA_CHOICES = [
        ('casa',      'Casa'),       # moradia, contas, aluguel
        ('viagem',    'Viagem'),     # trips, passeios
        ('casal',     'Casal'),      # despesas a dois
        ('trabalho',  'Trabalho'),   # almoços, confraternizações
        ('outro',     'Outro'),      # categoria genérica
    ]

    # Nome do grupo — obrigatório
    name = models.CharField(max_length=100)

    # Descrição opcional — TextField não tem limite de tamanho
    description = models.TextField(blank=True, null=True)

    # Categoria do grupo — escolhe entre as opções definidas acima
    # default='outro' garante que grupos antigos (que não tinham esse campo)
    # recebam automaticamente o valor 'outro' ao rodar a migração
    category = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='outro',
        verbose_name='Categoria'
    )

    # Arquivado — BooleanField guarda True ou False
    # Grupos arquivados ficam ocultos na lista principal mas não são deletados
    # default=False porque todo grupo começa ativo (não arquivado)
    archived = models.BooleanField(default=False, verbose_name='Arquivado')

    # Quem criou o grupo
    # SET_NULL — se o usuário for deletado, o grupo continua com created_by=None
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_groups'
    )

    # ManyToManyField — um grupo tem vários membros, um usuário pode estar em vários grupos
    # Django cria uma tabela intermediária automaticamente
    members = models.ManyToManyField(
        User,
        related_name='groups_member',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
