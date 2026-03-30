from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def ver_grupos (request):
    if request.method == 'GET':
        nome='irlan'
        return render(request, 'grupos.html', {'grupo': nome})
    elif request.method == 'POST':
        print('olá')