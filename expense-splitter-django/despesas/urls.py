from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),


    path("biblioteca/", views.index, name='index'),


    path("biblioteca/livros2", views.livros, name='livros'),

    path("biblioteca/detalhe/<int:numero>/", views.detalhe_livro, name='detalhe'),


    path("biblioteca/perfil/", views.perfil, name='perfil'),

    path("biblioteca/autores/", views.autores, name='autores')
]