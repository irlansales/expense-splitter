# accounts/admin.py
# Registra os modelos do app accounts no painel de administração do Django.
# O painel admin fica em /admin/ e permite gerenciar dados sem escrever código.
# Para registrar, basta importar o modelo e chamar admin.site.register().

from django.contrib import admin
from .models import UserProfile, Notification


# @admin.register() é um decorator alternativo a admin.site.register()
# Ambos fazem a mesma coisa — registrar o modelo no admin.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # list_display define quais colunas aparecem na listagem do admin
    list_display = ['user', 'bio']
    # search_fields permite buscar por esses campos
    search_fields = ['user__username']  # user__username = campo username dentro de user


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'read', 'created_at']
    # list_filter adiciona filtros laterais no admin
    list_filter = ['read']
    search_fields = ['user__username', 'message']
