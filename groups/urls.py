from django.urls import path
from . import views


urlpatterns = [

    path('grupo/', views.ver_grupos, name='ver_grupos')




]