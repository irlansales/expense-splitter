# accounts/models.py
# Define os modelos do app accounts: UserProfile e Notification.
# Esses modelos ESTENDEM o sistema de usuários padrão do Django (auth.User),
# adicionando informações extras sem modificar o modelo User original.

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save  # sinal disparado após salvar um objeto
from django.dispatch import receiver              # decorator que "ouve" um sinal


# ===== USER PROFILE =====
# Armazena informações extras sobre um usuário além do que o Django já tem
# (o User padrão já tem: username, email, password, first_name, last_name).
# UserProfile é um "extensão lateral" — um-para-um com User.
class UserProfile(models.Model):

    # OneToOneField = relação um-para-um
    # Cada usuário tem exatamente um perfil, e cada perfil pertence a um único usuário.
    # on_delete=CASCADE → se o User for deletado, o UserProfile vai junto
    # related_name='profile' → user.profile acessa o perfil do usuário
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Avatar — foto de perfil
    # ImageField requer a biblioteca Pillow instalada (pip install Pillow).
    # upload_to='avatars/' define a subpasta dentro de MEDIA_ROOT onde as imagens são salvas.
    # blank=True / null=True → campo opcional — o usuário pode não ter foto
    #
    # NOTA IMPORTANTE: Para usar ImageField você precisa:
    # 1. pip install Pillow
    # 2. Definir MEDIA_ROOT e MEDIA_URL no settings.py
    # 3. Configurar urls.py para servir arquivos de mídia no desenvolvimento
    # Por simplicidade, deixamos o campo aqui mas ele é opcional (blank/null).
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Avatar'
    )

    # Bio — texto livre sobre o usuário
    bio = models.TextField(blank=True, null=True, verbose_name='Sobre mim')

    def __str__(self):
        # Retorna algo amigável quando precisamos imprimir o objeto
        return f'Perfil de {self.user.username}'

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'


# ===== SIGNAL: auto-criar perfil quando um usuário é criado =====
#
# Signals (sinais) são um sistema de eventos do Django.
# post_save é disparado DEPOIS que qualquer objeto é salvo no banco.
# Usamos @receiver para "escutar" esse sinal apenas para o modelo User.
#
# Por que usar signal aqui?
# Porque queremos que TODA vez que alguém criar um User (seja via cadastro,
# via admin, via código), o perfil seja criado automaticamente.
# Sem o signal, precisaríamos lembrar de chamar UserProfile.objects.create()
# em todo lugar que cria usuários — o signal garante que isso nunca seja esquecido.
@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    # sender = o model que disparou o sinal (User)
    # instance = o objeto User que foi salvo
    # created = True se foi CRIAÇÃO, False se foi UPDATE
    # **kwargs = outros argumentos que o Django passa (ignoramos com **)

    if created:
        # Só criamos o perfil quando o User foi CRIADO (não em updates)
        UserProfile.objects.create(user=instance)


# ===== NOTIFICATION =====
# Armazena notificações para cada usuário.
# Ex: "João adicionou uma despesa no grupo Viagem SP"
# As notificações ficam salvas no banco e podem ser marcadas como lidas.
class Notification(models.Model):

    # Para qual usuário é essa notificação
    # related_name='notifications' → user.notifications.all() lista as notificações do usuário
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    # Texto da notificação — ex: "Maria adicionou 'Almoço' no grupo República"
    message = models.CharField(max_length=300)

    # Se já foi lida — começa como False (não lida)
    # Isso permite mostrar um contador de notificações não lidas na navbar
    read = models.BooleanField(default=False)

    # Quando foi criada — preenchida automaticamente
    created_at = models.DateTimeField(auto_now_add=True)

    # Link opcional para onde a notificação aponta
    # Ex: '/despesas/5/' — ao clicar, o usuário vai para aquela despesa
    # blank=True → pode ficar em branco
    link = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'Notif para {self.user.username}: {self.message[:50]}'

    class Meta:
        # Mais recentes primeiro
        ordering = ['-created_at']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
