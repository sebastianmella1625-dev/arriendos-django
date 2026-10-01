from django.urls import path
from . import views

urlpatterns = [
    path('accounts/registro/', views.registro, name='registro'),
    path('accounts/perfil/', views.perfil, name='perfil'),
    path('accounts/perfil/editar/', views.editar_perfil, name='editar_perfil'),

    path('inmuebles/', views.inmuebles_disponibles, name='inmuebles_disponibles'),
    path('inmuebles/mios/', views.mis_inmuebles, name='mis_inmuebles'),
    path('inmuebles/nuevo/', views.crear_inmueble, name='crear_inmueble'),
    path('inmuebles/<int:pk>/editar/', views.editar_inmueble, name='editar_inmueble'),
    path('inmuebles/<int:pk>/eliminar/', views.eliminar_inmueble, name='eliminar_inmueble'),
]
