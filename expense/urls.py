# expense/urls.py
# Arquivo principal de URLs do projeto.
# Aqui registramos TODAS as rotas do sistema, organizando por app com include().
# O Django lê esse arquivo para saber qual view chamar para cada URL.

from django.contrib import admin
from django.urls import path, include
from django.conf import settings           # importa as configurações do settings.py
from django.conf.urls.static import static  # função auxiliar para servir arquivos de mídia

urlpatterns = [
    # Painel admin gerado automaticamente pelo Django
    path('admin/', admin.site.urls),

    # Página inicial e autenticação — gerenciados pelo app accounts
    path('', include('accounts.urls')),

    # Rotas de grupos — tudo que começa com /grupos/
    path('grupos/', include('groups.urls')),

    # Rotas de despesas — tudo que começa com /despesas/
    path('despesas/', include('expenses.urls')),
]

# Em modo de desenvolvimento (DEBUG=True), Django não serve arquivos de mídia automaticamente.
# Essa linha adiciona uma rota especial para servir os uploads da pasta MEDIA_ROOT.
# Em produção, um servidor como nginx ou S3 faz isso.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
