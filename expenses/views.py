# expenses/views.py
# Views do app expenses: criar, editar, apagar despesas,
# marcar splits como pagos, registrar pagamentos manuais e ver histórico.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone   # para pegar a data/hora atual com fuso horário
from decimal import Decimal, InvalidOperation
from groups.models import Group
from .models import Expense, ExpenseSplit, Payment
from accounts.views import criar_notificacao


# =============================================================================
# CRIAR DESPESA
# =============================================================================
@login_required
def criar_despesa(request, group_pk):
    # Busca o grupo — 404 se não existir
    grupo = get_object_or_404(Group, pk=group_pk)

    # Só membros do grupo podem adicionar despesas
    if request.user not in grupo.members.all():
        messages.error(request, 'Você não é membro deste grupo.')
        return redirect('lista_grupos')

    membros = grupo.members.all()

    if request.method == 'GET':
        return render(request, 'expenses/criar_despesa.html', {
            'grupo': grupo,
            'membros': membros,
            'categoria_choices': Expense.CATEGORIA_CHOICES,
        })

    if request.method == 'POST':
        description = request.POST.get('description')
        amount_str  = request.POST.get('amount')
        split_type  = request.POST.get('split_type', 'igual')
        category    = request.POST.get('category', 'outro')
        date_str    = request.POST.get('date')
        notes       = request.POST.get('notes', '')

        # Validação: campos obrigatórios
        if not description or not amount_str:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return render(request, 'expenses/criar_despesa.html', {
                'grupo': grupo, 'membros': membros,
                'categoria_choices': Expense.CATEGORIA_CHOICES,
            })

        # Converte o valor para Decimal de forma segura
        # InvalidOperation é lançado se o texto não for um número válido
        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            messages.error(request, 'Valor inválido.')
            return render(request, 'expenses/criar_despesa.html', {
                'grupo': grupo, 'membros': membros,
                'categoria_choices': Expense.CATEGORIA_CHOICES,
            })

        # Monta os kwargs da despesa
        kwargs_despesa = {
            'description': description,
            'amount': amount,
            'category': category,
            'paid_by': request.user,
            'group': grupo,
            'notes': notes,
        }
        # Se o usuário preencheu uma data personalizada, usa ela
        if date_str:
            kwargs_despesa['date'] = date_str

        # Cria a despesa no banco
        despesa = Expense.objects.create(**kwargs_despesa)

        # Cria os splits conforme o tipo escolhido
        if split_type == 'igual':
            total_membros    = membros.count()
            valor_por_pessoa = (amount / total_membros).quantize(Decimal('0.01'))

            for membro in membros:
                ExpenseSplit.objects.create(
                    expense=despesa,
                    user=membro,
                    amount_owed=valor_por_pessoa
                )

        elif split_type == 'manual':
            total_splits = Decimal('0')
            splits_data  = []

            for membro in membros:
                # Campo no formulário: split_<id_do_usuario>
                valor_str = request.POST.get(f'split_{membro.pk}', '0')
                try:
                    valor = Decimal(valor_str) if valor_str else Decimal('0')
                except InvalidOperation:
                    valor = Decimal('0')
                splits_data.append((membro, valor))
                total_splits += valor

            # Valida se a soma bate com o total (tolerância de 1 centavo)
            if abs(total_splits - amount) > Decimal('0.01'):
                messages.error(request, f'A soma das partes (R${total_splits}) não é igual ao total (R${amount}).')
                despesa.delete()
                return render(request, 'expenses/criar_despesa.html', {
                    'grupo': grupo, 'membros': membros,
                    'categoria_choices': Expense.CATEGORIA_CHOICES,
                })

            for membro, valor in splits_data:
                ExpenseSplit.objects.create(
                    expense=despesa,
                    user=membro,
                    amount_owed=valor
                )

        # Notifica todos os membros do grupo (exceto quem adicionou)
        for membro in membros:
            if membro != request.user:
                criar_notificacao(
                    membro,
                    f'{request.user.username} adicionou "{description}" (R${amount}) em {grupo.name}',
                    f'/despesas/{despesa.pk}/'
                )

        messages.success(request, f'Despesa "{description}" adicionada!')
        return redirect('detalhe_grupo', pk=group_pk)


# =============================================================================
# DETALHE DA DESPESA
# =============================================================================
@login_required
def detalhe_despesa(request, pk):
    despesa = get_object_or_404(Expense, pk=pk)

    if request.user not in despesa.group.members.all():
        messages.error(request, 'Acesso negado.')
        return redirect('lista_grupos')

    splits = despesa.splits.all()

    return render(request, 'expenses/detalhe_despesa.html', {
        'despesa': despesa,
        'splits':  splits,
    })


# =============================================================================
# EDITAR DESPESA
# =============================================================================
@login_required
def editar_despesa(request, pk):
    despesa = get_object_or_404(Expense, pk=pk)

    # Só quem pagou ou o criador do grupo pode editar
    pode_editar = (request.user == despesa.paid_by or
                   request.user == despesa.group.created_by)
    if not pode_editar:
        messages.error(request, 'Você não tem permissão para editar esta despesa.')
        return redirect('detalhe_despesa', pk=pk)

    if request.method == 'GET':
        return render(request, 'expenses/editar_despesa.html', {
            'despesa': despesa,
            'categoria_choices': Expense.CATEGORIA_CHOICES,
        })

    if request.method == 'POST':
        description = request.POST.get('description')
        amount_str  = request.POST.get('amount')
        category    = request.POST.get('category', despesa.category)
        date_str    = request.POST.get('date')
        notes       = request.POST.get('notes', '')

        try:
            amount = Decimal(amount_str)
        except (InvalidOperation, TypeError):
            messages.error(request, 'Valor inválido.')
            return render(request, 'expenses/editar_despesa.html', {
                'despesa': despesa,
                'categoria_choices': Expense.CATEGORIA_CHOICES,
            })

        # Atualiza os campos da despesa
        # save() grava as alterações no banco
        despesa.description = description
        despesa.amount      = amount
        despesa.category    = category
        despesa.notes       = notes
        if date_str:
            despesa.date = date_str
        despesa.save()

        messages.success(request, 'Despesa atualizada.')
        return redirect('detalhe_despesa', pk=pk)


# =============================================================================
# APAGAR DESPESA
# =============================================================================
@login_required
def apagar_despesa(request, pk):
    despesa = get_object_or_404(Expense, pk=pk)

    pode_apagar = (request.user == despesa.paid_by or
                   request.user == despesa.group.created_by)
    if not pode_apagar:
        messages.error(request, 'Você não tem permissão para apagar esta despesa.')
        return redirect('detalhe_despesa', pk=pk)

    # Só aceita POST — impede apagar acidentalmente por GET
    if request.method == 'POST':
        group_pk = despesa.group.pk
        nome     = despesa.description
        # delete() remove o objeto e tudo relacionado (CASCADE nos splits)
        despesa.delete()
        messages.success(request, f'Despesa "{nome}" removida.')
        return redirect('detalhe_grupo', pk=group_pk)

    return redirect('detalhe_despesa', pk=pk)


# =============================================================================
# MARCAR SPLIT COMO PAGO / NÃO PAGO
# =============================================================================
@login_required
def marcar_pago(request, split_pk):
    split = get_object_or_404(ExpenseSplit, pk=split_pk)

    # Só o próprio usuário pode marcar seu split como pago
    if request.user != split.user and request.user != split.expense.group.created_by:
        messages.error(request, 'Sem permissão.')
        return redirect('detalhe_despesa', pk=split.expense.pk)

    if request.method == 'POST':
        # Toggle: inverte o estado atual
        split.paid = not split.paid
        # Se marcou como pago, registra quando. Se desmarcou, apaga a data.
        split.paid_at = timezone.now() if split.paid else None
        split.save()

        # Notifica o pagador da despesa quando alguém marca como pago
        if split.paid and split.user != split.expense.paid_by:
            criar_notificacao(
                split.expense.paid_by,
                f'{split.user.username} marcou a parte dele como paga em "{split.expense.description}"',
                f'/despesas/{split.expense.pk}/'
            )

    return redirect('detalhe_despesa', pk=split.expense.pk)


# =============================================================================
# REGISTRAR PAGAMENTO MANUAL
# =============================================================================
@login_required
def registrar_pagamento(request, group_pk):
    grupo = get_object_or_404(Group, pk=group_pk)

    if request.user not in grupo.members.all():
        messages.error(request, 'Você não é membro deste grupo.')
        return redirect('lista_grupos')

    # Remove o próprio usuário da lista — não pode pagar pra si mesmo
    outros_membros = grupo.members.exclude(pk=request.user.pk)

    if request.method == 'GET':
        return render(request, 'expenses/registrar_pagamento.html', {
            'grupo':          grupo,
            'outros_membros': outros_membros,
        })

    if request.method == 'POST':
        to_user_pk = request.POST.get('to_user')
        amount_str = request.POST.get('amount')
        notes      = request.POST.get('notes', '')

        try:
            to_user = User.objects.get(pk=to_user_pk)
            amount  = Decimal(amount_str)
        except (User.DoesNotExist, InvalidOperation, TypeError):
            messages.error(request, 'Dados inválidos.')
            return render(request, 'expenses/registrar_pagamento.html', {
                'grupo': grupo, 'outros_membros': outros_membros,
            })

        # Cria o registro de pagamento
        Payment.objects.create(
            from_user=request.user,
            to_user=to_user,
            group=grupo,
            amount=amount,
            notes=notes
        )

        # Notifica quem recebeu
        criar_notificacao(
            to_user,
            f'{request.user.username} registrou um pagamento de R${amount} para você em {grupo.name}',
            f'/grupos/{grupo.pk}/'
        )

        messages.success(request, f'Pagamento de R${amount} para {to_user.username} registrado!')
        return redirect('detalhe_grupo', pk=group_pk)


# =============================================================================
# HISTÓRICO DE PAGAMENTOS
# =============================================================================
@login_required
def historico_pagamentos(request, group_pk):
    grupo = get_object_or_404(Group, pk=group_pk)

    if request.user not in grupo.members.all():
        messages.error(request, 'Acesso negado.')
        return redirect('lista_grupos')

    # Busca todos os pagamentos do grupo — já ordenados por data (definido no model)
    pagamentos = grupo.payments.all()

    return render(request, 'expenses/historico_pagamentos.html', {
        'grupo':     grupo,
        'pagamentos': pagamentos,
    })
