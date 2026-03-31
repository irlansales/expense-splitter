# groups/urls.py
# Define todas as rotas do app groups.
# Cada path() conecta uma URL a uma função view.

from django.urls import path
from . import views

urlpatterns = [
    # Lista grupos ativos e arquivados — /grupos/
    path('', views.lista_grupos, name='lista_grupos'),

    # Criar novo grupo — /grupos/novo/
    path('novo/', views.criar_grupo, name='criar_grupo'),

    # Detalhe de um grupo — /grupos/3/
    # <int:pk> captura um número inteiro da URL e passa como argumento 'pk'
    path('<int:pk>/', views.detalhe_grupo, name='detalhe_grupo'),

    # Editar grupo — /grupos/3/editar/
    path('<int:pk>/editar/', views.editar_grupo, name='editar_grupo'),

    # Apagar grupo — /grupos/3/apagar/ (só aceita POST)
    path('<int:pk>/apagar/', views.apagar_grupo, name='apagar_grupo'),

    # Arquivar/desarquivar grupo — /grupos/3/arquivar/ (só aceita POST)
    path('<int:pk>/arquivar/', views.arquivar_grupo, name='arquivar_grupo'),

    # Sair do grupo — /grupos/3/sair/ (só aceita POST)
    path('<int:pk>/sair/', views.sair_grupo, name='sair_grupo'),

    # Adicionar membro — /grupos/3/adicionar-membro/
    path('<int:pk>/adicionar-membro/', views.adicionar_membro, name='adicionar_membro'),

    # Remover membro específico — /grupos/3/remover-membro/7/
    # <int:user_pk> é o id do usuário a ser removido
    path('<int:pk>/remover-membro/<int:user_pk>/', views.remover_membro, name='remover_membro'),
]
