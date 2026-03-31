# expenses/models.py
# Define os modelos do app expenses: Expense, ExpenseSplit e Payment.
# Cada classe = uma tabela no banco de dados SQLite.

from django.db import models
from django.contrib.auth.models import User
from datetime import date  # importamos date para usar como valor padrão no campo date


# ===== EXPENSE =====
# Representa uma despesa dentro de um grupo.
# Ex: "Pizza R$90 — João pagou, dividido entre 3 pessoas"
class Expense(models.Model):

    # Categorias de despesa — tuplas (valor_banco, texto_legível)
    CATEGORIA_CHOICES = [
        ('alimentacao', 'Alimentação'),   # restaurantes, supermercado
        ('transporte',  'Transporte'),    # uber, gasolina, passagem
        ('moradia',     'Moradia'),       # aluguel, contas
        ('lazer',       'Lazer'),         # shows, passeios, jogos
        ('saude',       'Saúde'),         # farmácia, médico
        ('outro',       'Outro'),         # qualquer coisa que não se encaixa
    ]

    # Descrição da despesa — ex: "Pizza", "Uber"
    description = models.CharField(max_length=200)

    # Valor total — DecimalField é o tipo correto para dinheiro
    # max_digits=10 → até 10 dígitos no total (ex: 99999999.99)
    # decimal_places=2 → sempre 2 casas decimais
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Categoria da despesa — usa as opções definidas acima
    # blank=True permite deixar em branco no formulário (campo opcional)
    category = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='outro',
        verbose_name='Categoria'
    )

    # Data da despesa — o usuário pode definir uma data personalizada
    # Antes era auto_now_add (preenchida automaticamente no momento da criação).
    # Agora é DateField(default=date.today) — por padrão usa a data de hoje,
    # mas o usuário pode mudar para registrar despesas passadas.
    # date.today é uma função — Django a chama no momento de criar cada objeto
    date = models.DateField(default=date.today, verbose_name='Data')

    # Observações opcionais — campo livre para notar qualquer coisa
    # blank=True → pode ficar vazio no formulário
    # null=True → pode ser NULL no banco (ausência total de valor)
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )

    # Quem pagou — ForeignKey cria uma chave estrangeira para User
    # related_name permite acessar user.paid_expenses.all()
    paid_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='paid_expenses'
    )

    # Em qual grupo essa despesa pertence
    # String 'groups.Group' porque o model está em outro app
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='expenses'
    )

    def __str__(self):
        return f'{self.description} — R${self.amount}'

    class Meta:
        # Ordena do mais recente para o mais antigo
        ordering = ['-date']
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'


# ===== EXPENSE SPLIT =====
# Representa a parte de cada pessoa em uma despesa.
# Ex: despesa de R$90 — João deve R$30, Maria deve R$60
class ExpenseSplit(models.Model):

    # Qual despesa — CASCADE: se a despesa for deletada, o split some também
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name='splits'
    )

    # Qual usuário deve esse valor
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='splits'
    )

    # Quanto esse usuário deve nessa despesa
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)

    # Se já pagou ou não — True = quitado, False = pendente
    paid = models.BooleanField(default=False)

    # Quando foi marcado como pago — null/blank porque começa sem data
    # DateTimeField guarda data E hora (ao contrário de DateField que guarda só data)
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Pago em'
    )

    def __str__(self):
        return f'{self.user.username} deve R${self.amount_owed} em "{self.expense.description}"'

    class Meta:
        verbose_name = 'Divisão'
        verbose_name_plural = 'Divisões'


# ===== PAYMENT =====
# Registra um pagamento manual entre dois membros de um grupo.
# Ex: "Carlos pagou R$50 para Ana no grupo Viagem SP"
# Isso é diferente de ExpenseSplit.paid — aqui registramos a transferência real de dinheiro.
class Payment(models.Model):

    # Quem está pagando — "de quem" sai o dinheiro
    # related_name='payments_made' → user.payments_made.all() lista o que ele pagou
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments_made',
        verbose_name='De'
    )

    # Quem está recebendo — "para quem" vai o dinheiro
    # related_name='payments_received' → user.payments_received.all() lista o que ele recebeu
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments_received',
        verbose_name='Para'
    )

    # Em qual grupo esse pagamento aconteceu
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Grupo'
    )

    # Valor pago
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor'
    )

    # Data/hora do pagamento — preenchida automaticamente quando o objeto é criado
    # auto_now_add=True → Django preenche na criação e nunca mais altera
    date = models.DateTimeField(auto_now_add=True, verbose_name='Data')

    # Observações opcionais sobre o pagamento
    notes = models.TextField(blank=True, null=True, verbose_name='Observações')

    def __str__(self):
        return f'{self.from_user.username} pagou R${self.amount} para {self.to_user.username}'

    class Meta:
        # Pagamentos mais recentes aparecem primeiro
        ordering = ['-date']
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
