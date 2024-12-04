from django.contrib import admin
from django.urls import include, path
from gastos.views import home, registrar_departamento_page, generar_gastos_comunes_page, pagar_gasto_comun_page, listar_gastos_pendientes_page

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('gastos.urls')),
    path('registrar_departamento/', registrar_departamento_page, name='registrar_departamento'),
    path('generar_gastos/', generar_gastos_comunes_page, name='generar_gastos'),
    path('pagar_gasto/', pagar_gasto_comun_page, name='pagar_gasto'),
    path('listar_pendientes/', listar_gastos_pendientes_page, name='listar_pendientes'),
]
