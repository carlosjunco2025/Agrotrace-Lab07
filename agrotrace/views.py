from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from .models import FundoProductor, LoteRecepcionado
from .forms import FundoProductorForm, LoteRecepcionadoForm

# ==========================================
# Vistas de FundoProductor
# ==========================================
def fundo_list(request):
    fundos = FundoProductor.objects.all()
    return render(request, 'agrotrace/fundo_list.html', {'fundos': fundos})

def fundo_create(request):
    if request.method == 'POST':
        form = FundoProductorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('agrotrace:fundo_list')
    else:
        form = FundoProductorForm()
    return render(request, 'agrotrace/fundo_form.html', {'form': form, 'title': 'Nuevo Fundo'})

def fundo_update(request, pk):
    fundo = get_object_or_404(FundoProductor, pk=pk)
    if request.method == 'POST':
        form = FundoProductorForm(request.POST, instance=fundo)
        if form.is_valid():
            form.save()
            return redirect('agrotrace:fundo_list')
    else:
        form = FundoProductorForm(instance=fundo)
    return render(request, 'agrotrace/fundo_form.html', {'form': form, 'title': 'Editar Fundo'})

def fundo_delete(request, pk):
    fundo = get_object_or_404(FundoProductor, pk=pk)
    if request.method == 'POST':
        fundo.delete()
        return redirect('agrotrace:fundo_list')
    return render(request, 'agrotrace/fundo_confirm_delete.html', {'object': fundo, 'type': 'Fundo'})

# ==========================================
# Vistas de LoteRecepcionado
# ==========================================
def lote_list(request):
    # Optimización de consultas ORM
    # select_related para relaciones 1:1 y 1:N (JOIN en SQL)
    # prefetch_related para relaciones N:M
    lotes = LoteRecepcionado.objects.select_related(
        'fundo', 
        'evaluacion_calidad'
    ).prefetch_related(
        'certificaciones'
    )
    return render(request, 'agrotrace/lote_list.html', {'lotes': lotes})

def lote_create(request):
    if request.method == 'POST':
        form = LoteRecepcionadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('agrotrace:lote_list')
    else:
        form = LoteRecepcionadoForm()
    return render(request, 'agrotrace/lote_form.html', {'form': form, 'title': 'Nuevo Lote'})

def lote_update(request, pk):
    lote = get_object_or_404(LoteRecepcionado, pk=pk)
    if request.method == 'POST':
        form = LoteRecepcionadoForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()
            return redirect('agrotrace:lote_list')
    else:
        form = LoteRecepcionadoForm(instance=lote)
    return render(request, 'agrotrace/lote_form.html', {'form': form, 'title': 'Editar Lote'})

def lote_delete(request, pk):
    lote = get_object_or_404(LoteRecepcionado, pk=pk)
    if request.method == 'POST':
        lote.delete()
        return redirect('agrotrace:lote_list')
    return render(request, 'agrotrace/lote_confirm_delete.html', {'object': lote, 'type': 'Lote'})

# ==========================================
# Ejercicio 3: Vista Transaccional con F()
# ==========================================
def recepcion_transaccional(request):
    if request.method == 'POST':
        fundo_id = request.POST.get('fundo_id')
        codigo_lote = request.POST.get('codigo_lote')
        toneladas = request.POST.get('toneladas')
        porcentaje_descarte = request.POST.get('porcentaje_descarte', 0)

        try:
            # Transacción atómica
            with transaction.atomic():
                fundo = FundoProductor.objects.select_for_update().get(id=fundo_id)

                # Regla de negocio: Validar existencia de cupos
                if fundo.cupo_diario_lotes <= 0:
                    raise ValueError(f"El fundo '{fundo.nombre_fundo}' ya no cuenta con cupo diario disponible.")

                # 1. Descuento directamente en la BD usando F()
                fundo.cupo_diario_lotes = F('cupo_diario_lotes') - 1
                fundo.save()

                # 2. Creación del registro de lote
                LoteRecepcionado.objects.create(
                    fundo=fundo,
                    codigo_lote=codigo_lote,
                    toneladas_brutas=toneladas,
                    porcentaje_descarte=porcentaje_descarte,
                    estado_evaluacion='PENDIENTE'
                )

                messages.success(request, f"¡Éxito! Lote {codigo_lote} registrado y cupo descontado.")
                # Patrón Post/Redirect/Get
                return redirect('agrotrace:lote_list')

        except Exception as e:
            # Mensaje de error (Rollback ejecutado)
            messages.error(request, f"Operación cancelada (Rollback): {str(e)}")

    fundos = FundoProductor.objects.all()
    return render(request, 'agrotrace/recepcion_transaccional.html', {'fundos': fundos})

from django.db.models import Sum, Avg, Count

def reporte_general(request):
    # Ejercicio 4: Agregación Global en CertificacionLote
    metricas_globales = CertificacionLote.objects.aggregate(
        total_costo=Sum('costo_auditoria'),
        promedio_costo=Avg('costo_auditoria'),
        total_auditorias=Count('id')
    )

    # Ejercicio 5.1: Agrupado por estado con values().annotate()
    reporte_estados = LoteRecepcionado.objects.values('estado_evaluacion').annotate(
        total_lotes=Count('id'),
        total_toneladas=Sum('toneladas_brutas'),
        promedio_descarte=Avg('porcentaje_descarte')
    ).order_by('-total_toneladas')

    # Ejercicio 5.2: Anotación por objeto (Lotes por Fundo)
    fundos_resumen = FundoProductor.objects.annotate(
        total_lotes=Count('lotes')
    )

    context = {
        'metricas_globales': metricas_globales,
        'reporte_estados': reporte_estados,
        'fundos_resumen': fundos_resumen,
    }
    return render(request, 'agrotrace/reporte.html', context)

# Vista 1: Listado de Lotes utilizando el método del QuerySet
def lote_list(request):
    # Reemplazo de consulta: Uso de select_related/prefetch_related + método personalizado
    lotes = LoteRecepcionado.objects.select_related(
        'fundo', 
        'evaluacion_calidad'
    ).prefetch_related(
        'certificaciones'
    ).pendientes() # <-- Método del QuerySet personalizado

    return render(request, 'agrotrace/lote_list.html', {'lotes': lotes})


# Vista 2: Vista de Reporte reutilizando métodos encadenados
def reporte_general(request):
    # ... (métricas globales) ...

    # Uso encadenado de los métodos del QuerySet personalizado
    lotes_criticos = LoteRecepcionado.objects.pendientes().con_alto_descarte(umbral=1.5)

    context = {
        # ... tus otros contextos ...
        'lotes_criticos': lotes_criticos,
    }
    return render(request, 'agrotrace/reporte.html', context)