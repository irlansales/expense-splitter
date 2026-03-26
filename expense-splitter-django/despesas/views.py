from django.shortcuts import render
from django.contrib.auth.decorators import login_required



def home(request):
    return render(request, 'despesas/home.html')


def index(request):
    return render(request, 'despesas/index.html')


def livros(request):
    livros =['iracema', 'memórias postumas', 'Taquicardios']
    return render (request,'despesas/livros.html', {'livros':livros})

def detalhe_livro(request, numero):
    numero
    if numero == 1:
        detalhe =  'iracema é bem chato'
    elif numero == 2:
        detalhe = 'brás cubas é triste'
    elif numero == 3:
        detalhe =  'esse nem existe'
    else:
        detalhe = 'erro numero nao encontrado'
    return render (request,'despesas/detalhe.html',{'detalhe_livro':detalhe})

@login_required
def perfil(request):

    usuario = request.user
    email = request.user.email
    return render(request,'despesas/perfil.html',{'usuario':usuario, 'email':email} )



def autores(request):
    autor = [
        {'nome': 'Machado de Assis', 'nacionalidade': 'Brasileiro'},
        {'nome': 'José de Alencar', 'nacionalidade': 'Brasileiro'},]
    return render(request, 'despesas/autores.html/', {'autores' :autor,})
