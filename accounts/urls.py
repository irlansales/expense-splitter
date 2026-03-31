# accounts/urls.py
# Define as rotas (URLs) do app accounts.
# Cada path() mapeia uma URL para uma função view.
# O argumento name= é um apelido para a URL — permite usar {% url 'nome' %} nos templates.

from django.urls import path
from . import views

urlpatterns = [
    # Página inicial — rota vazia = raiz do site (/)
    path('', views.home, name='home'),

    # Cadastro de novo usuário
    path('cadastro/', views.cadastro, name='cadastro'),

    # Login — usamos login_view pra não conflitar com a função login do Django
    path('login/', views.login_view, name='login'),

    # Logout
    path('logout/', views.logout_view, name='logout'),

    # Perfil público de um usuário — /perfil/joao/
    # <str:username> captura qualquer texto da URL e passa como argumento 'username' para a view
    path('perfil/<str:username>/', views.perfil, name='perfil'),

    # Editar próprio perfil — /perfil/editar/
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),

    # Mudar senha — /perfil/senha/
    path('perfil/senha/', views.mudar_senha, name='mudar_senha'),

    # Lista de notificações — /notificacoes/
    path('notificacoes/', views.notificacoes, name='notificacoes'),
]
