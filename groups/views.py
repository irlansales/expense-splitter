# groups/views.py
# Views do app groups: listar grupos, criar, detalhar, editar, arquivar,
# apagar, sair de um grupo, remover membro, e o algoritmo de simplificação de dívidas.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from decimal import Decimal   # Decimal é o tipo correto para trabalhar com dinheiro
from .models import Group
from accounts.views import criar_notificacao  # importa a função auxiliar de notificações
from expenses.models import Payment           # usado em detalhe_grupo para buscar pagamentos


# =============================================================================
# ALGORITMO DE SIMPLIFICAÇÃO DE DÍVIDAS
# =============================================================================
# Esta função recebe um grupo e calcula quem deve pagar para quem,
# minimizando o número de transferências necessárias.
#
# EXEMPLO:
#   Grupo com Ana, Bruno, Carlos. Despesas:
#   - Ana pagou R$90 (todos devem R$30 cada)
#   - Bruno pagou R$60 (todos devem R$20 cada)
#
#   Saldo líquido:
#   - Ana:    pagou 90, deve 30+20=50 → saldo = +40 (tem a receber)
#   - Bruno:  pagou 60, deve 30+20=50 → saldo = +10 (tem a receber)
#   - Carlos: pagou 0,  deve 30+20=50 → saldo = -50 (deve)
#
#   Simplificado: Carlos paga R$40 para Ana e R$10 para Bruno.
def simplificar_dividas(group):
    """
    Calcula o balanço simplificado de um grupo.
    Retorna uma lista de dicionários: [{'de': user, 'para': user, 'valor': Decimal}]
    """

    # PASSO 1: Calcular o saldo líquido de cada membro
    # saldo > 0 = tem a receber; saldo < 0 = deve; saldo = 0 = quitado
    saldos = {}
    for membro in group.members.all():
        saldos[membro] = Decimal('0')

    # Para cada despesa do grupo, somamos ao saldo de quem pagou
    for despesa in group.expenses.all():
        # Quem pagou ganha crédito do valor total
        if despesa.paid_by in saldos:
            saldos[despesa.paid_by] += despesa.amount

        # Cada split diminui o saldo de quem deve (apenas os não pagos)
        for split in despesa.splits.all():
            if not split.paid and split.user in saldos:
                saldos[split.user] -= split.amount_owed

    # PASSO 2: Separar quem tem saldo positivo (credores) e negativo (devedores)
    # Usamos listas de tuplas [user, valor] para poder modificar os valores
    credores  = [[u, v] for u, v in saldos.items() if v > Decimal('0.01')]
    devedores = [[u, v] for u, v in saldos.items() if v < Decimal('-0.01')]

    # PASSO 3: Algoritmo guloso (greedy) para minimizar transações
    # Para cada devedor, pagamos aos credores até o saldo zerar
    transacoes = []

    # Índices para percorrer as listas
    i = 0  # índice do credor atual
    j = 0  # índice do devedor atual

    while i < len(credores) and j < len(devedores):
        credor   = credores[i]    # [user, valor_a_receber] (positivo)
        devedor  = devedores[j]   # [user, valor_que_deve] (negativo)

        # O quanto pode ser transferido é o mínimo entre o que o credor espera
        # e o que o devedor deve
        valor = min(credor[1], abs(devedor[1]))

        # Registra a transação
        transacoes.append({
            'de':    devedor[0],   # quem paga
            'para':  credor[0],    # quem recebe
            'valor': valor,        # quanto transferir
        })

        # Diminui os saldos pelo valor transferido
        credor[1]  -= valor
        devedor[1] += valor  # devedor[1] é negativo, então += valor o aproxima de zero

        # Se o credor foi completamente pago, avança para o próximo credor
        if credor[1] <= Decimal('0.01'):
            i += 1

        # Se o devedor quitou sua dívida, avança para o próximo devedor
        if abs(devedor[1]) <= Decimal('0.01'):
            j += 1

    return transacoes


# =============================================================================
# LISTA DE GRUPOS
# =============================================================================
@login_required
def lista_grupos(request):
    # Busca TODOS os grupos onde o usuário logado é membro
    todos_grupos = request.user.groups_member.all()

    # Separa grupos ativos (archived=False) dos arquivados (archived=True)
    # .filter() retorna um QuerySet com os grupos que passam na condição
    grupos_ativos    = todos_grupos.filter(archived=False)
    grupos_arquivados = todos_grupos.filter(archived=True)

    return render(request, 'groups/lista_grupos.html', {
        'grupos_ativos':    grupos_ativos,
        'grupos_arquivados': grupos_arquivados,
    })


# =============================================================================
# CRIAR GRUPO
# =============================================================================
@login_required
def criar_grupo(request):
    if request.method == 'GET':
        # Passa as choices de categoria para o template poder gerar o <select>
        return render(request, 'groups/criar_grupo.html', {
            'categoria_choices': Group.CATEGORIA_CHOICES,
        })

    if request.method == 'POST':
        name        = request.POST.get('name')
        description = request.POST.get('description')
        category    = request.POST.get('category', 'outro')

        if not name:
            messages.error(request, 'O nome do grupo é obrigatório.')
            return render(request, 'groups/criar_grupo.html', {
                'categoria_choices': Group.CATEGORIA_CHOICES,
            })

        grupo = Group.objects.create(
            name=name,
            description=description,
            category=category,
            created_by=request.user
        )

        # Adiciona o criador como membro automaticamente
        grupo.members.add(request.user)

        messages.success(request, f'Grupo "{name}" criado com sucesso!')
        return redirect('detalhe_grupo', pk=grupo.pk)


# =============================================================================
# DETALHE DO GRUPO
# =============================================================================
@login_required
def detalhe_grupo(request, pk):
    grupo = get_object_or_404(Group, pk=pk)

    # Segurança: só membros do grupo podem ver os detalhes
    if request.user not in grupo.members.all():
        messages.error(request, 'Você não é membro deste grupo.')
        return redirect('lista_grupos')

    despesas = grupo.expenses.all()

    # BALANÇO SIMPLES: quanto cada membro deve ou tem a receber
    balance = {}
    for membro in grupo.members.all():
        balance[membro] = Decimal('0')

    for despesa in despesas:
        if despesa.paid_by in balance:
            balance[despesa.paid_by] += despesa.amount
        for split in despesa.splits.all():
            if split.user in balance:
                balance[split.user] -= split.amount_owed

    # Simplifica as dívidas usando o algoritmo acima
    transacoes = simplificar_dividas(grupo)

    # ACTIVITY LOG: lista as despesas mais recentes (até 10) para mostrar atividade
    # Isso dá uma visão rápida do que aconteceu recentemente no grupo
    atividade_recente = despesas[:10]

    # Busca pagamentos manuais do grupo para incluir na atividade
    pagamentos_recentes = grupo.payments.all()[:10]

    return render(request, 'groups/detalhe_grupo.html', {
        'grupo':             grupo,
        'despesas':          despesas,
        'balance':           balance,
        'transacoes':        transacoes,       # lista simplificada de quem paga quem
        'atividade_recente': atividade_recente,
        'pagamentos_recentes': pagamentos_recentes,
    })


# =============================================================================
# ADICIONAR MEMBRO
# =============================================================================
@login_required
def adicionar_membro(request, pk):
    grupo = get_object_or_404(Group, pk=pk)

    # Só o criador pode adicionar membros
    if request.user != grupo.created_by:
        messages.error(request, 'Apenas o criador pode adicionar membros.')
        return redirect('detalhe_grupo', pk=pk)

    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            if user in grupo.members.all():
                messages.error(request, f'{username} já é membro do grupo.')
            else:
                grupo.members.add(user)
                messages.success(request, f'{username} adicionado ao grupo!')
                # Notifica o usuário adicionado
                criar_notificacao(
                    user,
                    f'Você foi adicionado ao grupo "{grupo.name}".',
                    f'/grupos/{grupo.pk}/'
                )
        except User.DoesNotExist:
            messages.error(request, f'Usuário "{username}" não encontrado.')

    return redirect('detalhe_grupo', pk=pk)


# =============================================================================
# EDITAR GRUPO
# =============================================================================
@login_required
def editar_grupo(request, pk):
    grupo = get_object_or_404(Group, pk=pk)

    # Só o criador pode editar
    if request.user != grupo.created_by:
        messages.error(request, 'Apenas o criador pode editar o grupo.')
        return redirect('detalhe_grupo', pk=pk)

    if request.method == 'GET':
        return render(request, 'groups/editar_grupo.html', {
            'grupo': grupo,
            'categoria_choices': Group.CATEGORIA_CHOICES,
        })

    if request.method == 'POST':
        name        = request.POST.get('name')
        description = request.POST.get('description', '')
        category    = request.POST.get('category', 'outro')

        if not name:
            messages.error(request, 'O nome do grupo é obrigatório.')
            return render(request, 'groups/editar_grupo.html', {
                'grupo': grupo,
                'categoria_choices': Group.CATEGORIA_CHOICES,
            })

        # Atualiza os campos do grupo
        grupo.name        = name
        grupo.description = description
        grupo.category    = category
        grupo.save()  # salva no banco

        messages.success(request, 'Grupo atualizado!')
        return redirect('detalhe_grupo', pk=pk)


# =============================================================================
# APAGAR GRUPO
# =============================================================================
@login_required
def apagar_grupo(request, pk):
    grupo = get_object_or_404(Group, pk=pk)

    # Só o criador pode deletar, e apenas via POST (não via GET)
    if request.user != grupo.created_by:
        messages.error(request, 'Apenas o criador pode apagar o grupo.')
        return redirect('detalhe_grupo', pk=pk)

    # Só aceitamos POST para operações destrutivas
    # Isso evita que links simples (GET) possam apagar dados acidentalmente
    if request.method == 'POST':
        nome = grupo.name   # guarda o nome antes de deletar para usar na mensagem
        grupo.delete()      # .delete() remove o objeto e todos os relacionados (CASCADE)
        messages.success(request, f'Grupo "{nome}" apagado.')
        return redirect('lista_grupos')

    # Se alguém tentar via GET, volta para o detalhe
    return redirect('detalhe_grupo', pk=pk)


# =============================================================================
# ARQUIVAR / DESARQUIVAR GRUPO
# =============================================================================
@login_required
def arquivar_grupo(request, pk):
    grupo = get_object_or_404(Group, pk=pk)

    if request.user != grupo.created_by:
        messages.error(request, 'Apenas o criador pode arquivar o grupo.')
        return redirect('detalhe_grupo', pk=pk)

    if request.method == 'POST':
        # Inverte o estado: se estava arquivado, desarquiva; se estava ativo, arquiva
        # O operador 'not' inverte um booleano: not True = False, not False = True
        grupo.archived = not grupo.archived
        grupo.save()

        status = 'arquivado' if grupo.archived else 'reativado'
        messages.success(request, f'Grupo {status} com sucesso.')

    return redirect('detalhe_grupo', pk=pk)


# =============================================================================
# SAIR DO GRUPO
# =============================================================================
@login_required
def sair_grupo(request, pk):
    grupo = get_object_or_404(Group, pk=pk)

    if request.user not in grupo.members.all():
        messages.error(request, 'Você não é membro deste grupo.')
        return redirect('lista_grupos')

    # O criador não pode sair sem transferir a criação ou deletar o grupo
    if request.user == grupo.created_by:
        messages.error(request, 'O criador não pode sair do grupo. Apague-o se desejar.')
        return redirect('detalhe_grupo', pk=pk)

    if request.method == 'POST':
        # .remove() desfaz a relação ManyToMany sem deletar o usuário ou o grupo
        grupo.members.remove(request.user)
        messages.success(request, f'Você saiu do grupo "{grupo.name}".')
        return redirect('lista_grupos')

    return redirect('detalhe_grupo', pk=pk)


# =============================================================================
# REMOVER MEMBRO (pelo criador)
# =============================================================================
@login_required
def remover_membro(request, pk, user_pk):
    grupo    = get_object_or_404(Group, pk=pk)
    usuario  = get_object_or_404(User, pk=user_pk)

    # Só o criador pode remover membros
    if request.user != grupo.created_by:
        messages.error(request, 'Apenas o criador pode remover membros.')
        return redirect('detalhe_grupo', pk=pk)

    # Não pode remover a si mesmo por essa rota
    if usuario == request.user:
        messages.error(request, 'Use "Sair do grupo" para se remover.')
        return redirect('detalhe_grupo', pk=pk)

    if request.method == 'POST':
        grupo.members.remove(usuario)
        messages.success(request, f'{usuario.username} removido do grupo.')

    return redirect('detalhe_grupo', pk=pk)
