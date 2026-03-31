# accounts/views.py
# Views do app accounts: login, cadastro, logout, perfil, editar perfil,
# mudar senha, notificações e a função auxiliar criar_notificacao.
#
# Uma VIEW em Django é uma função Python que:
# 1. Recebe um objeto HttpRequest (request) com dados do navegador
# 2. Processa a lógica (valida dados, acessa o banco, etc.)
# 3. Retorna um objeto HttpResponse (geralmente um template renderizado)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification, UserProfile


# =============================================================================
# FUNÇÃO AUXILIAR: criar_notificacao
# =============================================================================
# Esta é uma função auxiliar — não é uma view, não tem URL.
# Ela é importada por outras views (groups, expenses) para criar notificações.
# Ao centralizar aqui, evitamos repetir código em vários lugares.
def criar_notificacao(user, message, link=''):
    """
    Cria uma notificação para um usuário.

    Parâmetros:
        user    — o objeto User que receberá a notificação
        message — texto da notificação (ex: "João adicionou uma despesa")
        link    — URL opcional para onde a notificação aponta (ex: '/despesas/5/')

    Exemplo de uso em outra view:
        from accounts.views import criar_notificacao
        criar_notificacao(membro, 'Nova despesa adicionada!', f'/despesas/{despesa.pk}/')
    """
    # Notification.objects.create() insere um novo registro no banco de dados
    # Passamos user, message e link — o campo 'read' fica False por padrão (definido no model)
    Notification.objects.create(user=user, message=message, link=link)


# =============================================================================
# HOME
# =============================================================================
# Página inicial — redireciona para login se não estiver logado
def home(request):
    # request.user.is_authenticated verifica se há uma sessão ativa
    if not request.user.is_authenticated:
        return redirect('login')
    # Se estiver logado, redireciona para a lista de grupos
    return redirect('lista_grupos')


# =============================================================================
# CADASTRO
# =============================================================================
def cadastro(request):
    # GET = usuário abriu a página — mostra o formulário vazio
    if request.method == 'GET':
        return render(request, 'accounts/cadastro.html')

    # POST = usuário enviou o formulário
    if request.method == 'POST':
        username = request.POST.get('username')   # pega o campo 'username' do formulário
        email    = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')  # confirmação de senha

        # Validações básicas
        if password != password2:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'accounts/cadastro.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já existe.')
            return render(request, 'accounts/cadastro.html')

        # create_user cria o usuário já com senha criptografada
        user = User.objects.create_user(username=username, email=email, password=password)

        # O signal post_save em accounts/models.py cria o UserProfile automaticamente aqui

        # Loga o usuário automaticamente após cadastro
        login(request, user)
        return redirect('lista_grupos')


# =============================================================================
# LOGIN
# =============================================================================
def login_view(request):
    # Se já está logado, não precisa ver o login
    if request.user.is_authenticated:
        return redirect('lista_grupos')

    if request.method == 'GET':
        return render(request, 'accounts/login.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # authenticate verifica usuário e senha — retorna o User ou None
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # cria a sessão
            return redirect('lista_grupos')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
            return render(request, 'accounts/login.html')


# =============================================================================
# LOGOUT
# =============================================================================
def logout_view(request):
    logout(request)  # encerra a sessão
    return redirect('login')


# =============================================================================
# PERFIL PÚBLICO
# =============================================================================
# Exibe o perfil de qualquer usuário — qualquer pessoa pode ver
@login_required
def perfil(request, username):
    # get_object_or_404 busca o User pelo username
    # Se não existir, Django retorna automaticamente a página 404
    usuario = get_object_or_404(User, username=username)

    # Busca os grupos que o usuário visitado e o usuário logado têm em comum
    # .filter() com dois argumentos = WHERE members=usuario AND members=request.user
    # Mas ManyToMany precisa de uma abordagem diferente:
    meus_grupos = set(request.user.groups_member.values_list('pk', flat=True))
    grupos_do_usuario = usuario.groups_member.all()
    # Filtra apenas os grupos em comum (interseção)
    grupos_em_comum = [g for g in grupos_do_usuario if g.pk in meus_grupos]

    # Conta quantas despesas esse usuário pagou no total
    total_despesas = usuario.paid_expenses.count()

    # Tenta buscar o perfil — o signal garante que existe, mas usamos getattr por segurança
    # hasattr verifica se o atributo existe antes de acessar
    try:
        perfil_obj = usuario.profile
    except UserProfile.DoesNotExist:
        # Caso o perfil não exista por algum motivo, criamos um
        perfil_obj = UserProfile.objects.create(user=usuario)

    return render(request, 'accounts/perfil.html', {
        'usuario': usuario,               # o usuário cujo perfil estamos vendo
        'perfil_obj': perfil_obj,         # o UserProfile com bio e avatar
        'grupos_em_comum': grupos_em_comum,
        'total_despesas': total_despesas,
    })


# =============================================================================
# EDITAR PERFIL
# =============================================================================
# O usuário edita suas próprias informações (nome, email, bio)
@login_required
def editar_perfil(request):
    # Busca ou cria o perfil do usuário logado
    # get_or_create retorna uma tupla (objeto, criado) — usamos _ para ignorar o segundo
    perfil_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        # Passamos o usuário e o perfil para o template poder pré-preencher o formulário
        return render(request, 'accounts/editar_perfil.html', {
            'perfil_obj': perfil_obj,
        })

    if request.method == 'POST':
        # Pega os valores do formulário
        first_name = request.POST.get('first_name', '')
        last_name  = request.POST.get('last_name', '')
        email      = request.POST.get('email', '')
        bio        = request.POST.get('bio', '')

        # Atualiza o modelo User (dados básicos)
        request.user.first_name = first_name
        request.user.last_name  = last_name
        request.user.email      = email
        request.user.save()  # salva no banco

        # Atualiza o UserProfile (dados extras)
        perfil_obj.bio = bio

        # Verifica se o usuário enviou uma nova foto (avatar)
        # request.FILES contém arquivos enviados via formulário com enctype="multipart/form-data"
        if 'avatar' in request.FILES:
            perfil_obj.avatar = request.FILES['avatar']

        perfil_obj.save()  # salva no banco

        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('perfil', username=request.user.username)


# =============================================================================
# MUDAR SENHA
# =============================================================================
@login_required
def mudar_senha(request):
    if request.method == 'GET':
        return render(request, 'accounts/mudar_senha.html')

    if request.method == 'POST':
        senha_atual    = request.POST.get('senha_atual')
        nova_senha     = request.POST.get('nova_senha')
        confirma_senha = request.POST.get('confirma_senha')

        # check_password verifica se a senha atual está correta
        # É seguro pois compara com o hash armazenado, não a senha em texto puro
        if not request.user.check_password(senha_atual):
            messages.error(request, 'Senha atual incorreta.')
            return render(request, 'accounts/mudar_senha.html')

        if nova_senha != confirma_senha:
            messages.error(request, 'As novas senhas não coincidem.')
            return render(request, 'accounts/mudar_senha.html')

        if len(nova_senha) < 8:
            messages.error(request, 'A nova senha deve ter pelo menos 8 caracteres.')
            return render(request, 'accounts/mudar_senha.html')

        # set_password muda a senha e atualiza o hash no banco
        request.user.set_password(nova_senha)
        request.user.save()

        # update_session_auth_hash é ESSENCIAL aqui!
        # Quando a senha muda, o Django invalida a sessão atual por segurança.
        # Essa função atualiza a sessão com a nova senha para o usuário
        # não ser deslogado após trocar a senha.
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Senha alterada com sucesso!')
        return redirect('editar_perfil')


# =============================================================================
# NOTIFICAÇÕES
# =============================================================================
@login_required
def notificacoes(request):
    # Busca todas as notificações do usuário logado (mais recentes primeiro)
    # O order_by está definido no Meta do model, então .all() já ordena
    todas = request.user.notifications.all()

    # Marca todas como lidas
    # .update() faz um UPDATE no banco para TODOS os registros de uma vez
    # É mais eficiente do que um loop fazendo .save() em cada um
    request.user.notifications.filter(read=False).update(read=True)

    return render(request, 'accounts/notificacoes.html', {
        'notificacoes': todas,
    })
