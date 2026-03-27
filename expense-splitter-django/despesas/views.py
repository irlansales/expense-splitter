from django.shortcuts import render
from django.contrib.auth.decorators import login_required



def home(request):
    return render(request, 'despesas/home.html')


def index(request):
    return render(request, 'despesas/index.html')
