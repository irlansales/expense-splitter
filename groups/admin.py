from django.contrib import admin
from .models import Group

# Registra o model no painel admin — permite criar/editar/deletar grupos pela interface
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    # Colunas exibidas na listagem
    list_display = ['name', 'created_by', 'created_at']
    # Campo de busca
    search_fields = ['name']
