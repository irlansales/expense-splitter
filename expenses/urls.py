# expenses/urls.py
# Define todas as rotas do app expenses.

from django.urls import path
from . import views

urlpatterns = [
    # Criar despesa em um grupo — /despesas/3/nova/
    path('<int:group_pk>/nova/', views.criar_despesa, name='criar_despesa'),

    # Detalhe de uma despesa — /despesas/5/
    path('<int:pk>/', views.detalhe_despesa, name='detalhe_despesa'),

    # Editar despesa — /despesas/5/editar/
    path('<int:pk>/editar/', views.editar_despesa, name='editar_despesa'),

    # Apagar despesa — /despesas/5/apagar/ (só aceita POST)
    path('<int:pk>/apagar/', views.apagar_despesa, name='apagar_despesa'),

    # Marcar split como pago/não pago — /despesas/split/12/pagar/
    path('split/<int:split_pk>/pagar/', views.marcar_pago, name='marcar_pago'),

    # Registrar pagamento manual entre membros — /despesas/grupo/3/pagar/
    path('grupo/<int:group_pk>/pagar/', views.registrar_pagamento, name='registrar_pagamento'),

    # Histórico de pagamentos de um grupo — /despesas/grupo/3/historico/
    path('grupo/<int:group_pk>/historico/', views.historico_pagamentos, name='historico_pagamentos'),
]
