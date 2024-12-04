from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Departamento, GastoComun, Solicitud
from datetime import datetime, date
from django.shortcuts import render
from django.http import HttpResponse
import json

def home(request):
    return render(request, 'home.html')

def registrar_departamento_page(request):
    mensaje = None

    if request.method == 'POST':
        numero = request.POST.get('numero')
        if Departamento.objects.filter(numero=numero).exists():
            mensaje = "El departamento ya existe."
        else:
            Departamento.objects.create(numero=numero)
            mensaje = f"Departamento {numero} registrado con éxito."
    departamentos = Departamento.objects.all()
    
    return render(request, 'registrar_departamento.html', {'mensaje': mensaje, 'departamentos': departamentos})


@csrf_exempt
def registrar_departamento(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        numero = data.get('numero')
        if Departamento.objects.filter(numero=numero).exists():
            return JsonResponse({'error': 'El departamento ya existe'}, status=400)
        Departamento.objects.create(numero=numero)
        return JsonResponse({'message': 'Departamento registrado', 'numero': numero})

@csrf_exempt
def generar_gastos_comunes(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mes = data.get('mes')
        año = data.get('año')
        monto_base = data.get('monto_base', 50000)

        departamentos = Departamento.objects.all()
        if not departamentos.exists():
            return JsonResponse({'error': 'No hay departamentos registrados'}, status=404)

        gastos_generados = []
        for depto in departamentos:
            if GastoComun.objects.filter(departamento=depto, mes=mes, año=año).exists():
                continue
            gasto = GastoComun.objects.create(departamento=depto, mes=mes, año=año, monto=monto_base)
            gastos_generados.append({'departamento': depto.numero, 'mes': mes, 'año': año, 'monto': monto_base})

        return JsonResponse({'message': 'Gastos generados', 'gastos': gastos_generados})

def generar_gastos_comunes_page(request):
    mensaje = None
    if request.method == 'POST':
        mes = int(request.POST.get('mes'))
        año = int(request.POST.get('año'))
        monto_base = float(request.POST.get('monto_base', 50000))

        departamentos = Departamento.objects.all()
        if not departamentos.exists():
            mensaje = "No hay departamentos registrados. Registra al menos uno antes de generar gastos."
        else:
            gastos_generados = []
            for departamento in departamentos:
                if GastoComun.objects.filter(departamento=departamento, mes=mes, año=año).exists():
                    continue

                GastoComun.objects.create(
                    departamento=departamento,
                    mes=mes,
                    año=año,
                    monto=monto_base
                )
                gastos_generados.append(f"{departamento.numero} - {mes}/{año} - ${monto_base}")

            if gastos_generados:
                mensaje = f"Gastos comunes generados para {len(gastos_generados)} departamentos."
            else:
                mensaje = "Todos los gastos para el mes y año seleccionados ya estaban generados."

    return render(request, 'generar_gastos.html', {'mensaje': mensaje})

@csrf_exempt
def marcar_como_pagado(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        departamento_num = data.get('departamento')
        mes = data.get('mes')
        año = data.get('año')
        fecha_pago = data.get('fecha_pago')

        departamento = get_object_or_404(Departamento, numero=departamento_num)
        gasto = get_object_or_404(GastoComun, departamento=departamento, mes=mes, año=año)

        if gasto.pagado:
            return JsonResponse({'estado': 'Pago duplicado'}, status=400)

        gasto.pagado = True
        gasto.fecha_pago = datetime.strptime(fecha_pago, '%Y-%m-%d').date()
        gasto.save()

        return JsonResponse({
            'departamento': departamento.numero,
            'mes': mes,
            'año': año,
            'fecha_pago': gasto.fecha_pago.strftime('%Y-%m-%d'),
            'estado': gasto.estado_pago()
        })

def pagar_gasto_comun_page(request):
    mensaje = None
    gastos_pendientes = []

    if request.method == 'POST' and 'departamento' in request.POST:
        departamento_num = request.POST.get('departamento')
        try:
            departamento = get_object_or_404(Departamento, numero=departamento_num)
            gastos_pendientes = GastoComun.objects.filter(departamento=departamento, pagado=False)
            if not gastos_pendientes:
                mensaje = f"No hay gastos pendientes para el departamento {departamento_num}."
        except Exception as e:
            mensaje = "No se encontró el departamento ingresado."

    elif request.method == 'POST' and 'gasto_id' in request.POST:
        gasto_id = request.POST.get('gasto_id')
        try:
            gasto = get_object_or_404(GastoComun, id=gasto_id)
            gasto.pagado = True
            gasto.fecha_pago = date.today()
            gasto.save()
            mensaje = f"Gasto del departamento {gasto.departamento.numero} pagado con éxito."
        except Exception as e:
            mensaje = "Error al procesar el pago."

    return render(request, 'pagar_gasto.html', {
        'gastos_pendientes': gastos_pendientes,
        'mensaje': mensaje
    })

def listar_gastos_pendientes_page(request):
    pendientes = []
    mensaje = None
    if request.method == 'GET' and 'mes' in request.GET and 'año' in request.GET:
        try:
            mes = int(request.GET.get('mes'))
            año = int(request.GET.get('año'))

            gastos_pendientes = GastoComun.objects.filter(
                pagado=False,
                año__lt=año
            ) | GastoComun.objects.filter(
                pagado=False,
                año=año,
                mes__lte=mes
            )

            if gastos_pendientes.exists():
                pendientes = [
                    {
                        'departamento': gasto.departamento.numero,
                        'mes': gasto.mes,
                        'año': gasto.año,
                        'monto': gasto.monto
                    }
                    for gasto in gastos_pendientes
                ]
            else:
                mensaje = "No hay gastos pendientes hasta la fecha seleccionada."

        except ValueError:
            mensaje = "Por favor, ingresa valores válidos para mes y año."

    return render(request, 'listar_pendientes.html', {'pendientes': pendientes, 'mensaje': mensaje})

def listar_gastos_pendientes(request):
    mes = int(request.GET.get('mes'))
    año = int(request.GET.get('año'))
    gastos_pendientes = GastoComun.objects.filter(
        pagado=False,
        año__lt=año
    ) | GastoComun.objects.filter(
        año=año,
        mes__lte=mes
    )
    
    

    resultado = [{
        'departamento': gasto.departamento.numero,
        'mes': gasto.mes,
        'año': gasto.año,
        'monto': gasto.monto
    } for gasto in gastos_pendientes]

    return JsonResponse(resultado, safe=False)

def recibir_solicitudes_page(request):
    mensaje = None
    if request.method == 'POST':
        departamento_numero = request.POST.get('departamento')
        descripcion = request.POST.get('descripcion')

        departamento = get_object_or_404(Departamento, numero=departamento_numero)
        Solicitud.objects.create(departamento=departamento, descripcion=descripcion)

        mensaje = "Solicitud registrada con éxito."

    departamentos = Departamento.objects.all()
    return render(request, 'recibir_solicitudes.html', {'mensaje': mensaje, 'departamentos': departamentos})

def listar_solicitudes_page(request):
    solicitudes = Solicitud.objects.select_related('departamento').all().order_by('-fecha_solicitud')
    return render(request, 'listar_solicitudes.html', {'solicitudes': solicitudes})
