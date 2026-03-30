from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def ver_grupos (request):



  
    return   render(request, 'grupos.html', {'grupo':'grupo'})