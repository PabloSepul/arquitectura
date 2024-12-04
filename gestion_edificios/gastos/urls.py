from django.urls import path
from . import views

urlpatterns = [
    path('departamentos/', views.registrar_departamento),
    path('gastos_comunes/generar/', views.generar_gastos_comunes),
    path('gastos_comunes/pagar/', views.marcar_como_pagado),
    path('gastos_comunes/pendientes/', views.listar_gastos_pendientes),
    path('recibir-solicitudes/', views.recibir_solicitudes_page, name='recibir_solicitudes'),
    path('listar-solicitudes/', views.listar_solicitudes_page, name='listar_solicitudes'),
]
