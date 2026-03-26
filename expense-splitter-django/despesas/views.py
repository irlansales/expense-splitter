from django.shortcuts import render


def home(request):
    return render(request, 'despesas/home.html')


def index(request):
    return render(request, 'despesas/index.html')

# Create your views here.
