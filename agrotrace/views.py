from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum, Avg, Count
from .models import FundoProductor, LoteRecepcionado, CertificacionLote
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
    lotes = LoteRecepcionado.objects.select_related(
        'fundo', 'evaluacion_calidad'
    ).prefetch_related('certificaciones').pendientes()
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
# Ejercicio 3/10: Vista Transaccional con F()
# ==========================================
def recepcion_transaccional(request):
    if request.method == 'POST':
        fundo_id = request.POST.get('fundo_id')
        codigo_lote = request.POST.get('codigo_lote')
        toneladas = request.POST.get('toneladas')
        porcentaje_descarte = request.POST.get('porcentaje_descarte', 0)

        try:
            with transaction.atomic():
                fundo = FundoProductor.objects.select_for_update().get(id=fundo_id)

                if fundo.cupo_diario_lotes <= 0:
                    raise ValueError(f"El fundo '{fundo.nombre_fundo}' ya no cuenta con cupo diario disponible.")

                fundo.cupo_diario_lotes = F('cupo_diario_lotes') - 1
                fundo.save()

                LoteRecepcionado.objects.create(
                    fundo=fundo,
                    codigo_lote=codigo_lote,
                    toneladas_brutas=toneladas,
                    porcentaje_descarte=porcentaje_descarte,
                    estado_evaluacion='PENDIENTE'
                )

                messages.success(request, f"¡Éxito! Lote {codigo_lote} registrado y cupo descontado.")
                return redirect('agrotrace:lote_list')

        except Exception as e:
            messages.error(request, f"Operación cancelada (Rollback): {str(e)}")

    fundos = FundoProductor.objects.all()
    return render(request, 'agrotrace/recepcion_transaccional.html', {'fundos': fundos})

# ==========================================
# Ejercicio 6/11: Vista de Reporte — ÚNICA DEFINICIÓN, completa
# ==========================================
def reporte_general(request):
    # Ejercicio 4: Agregación global sobre el modelo intermedio
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

    # Ejercicio 5.2: Anotación por objeto (lotes por fundo)
    fundos_resumen = FundoProductor.objects.annotate(
        total_lotes=Count('lotes')
    )

    # Ejercicio 7/12: QuerySet personalizado encadenado
    lotes_criticos = LoteRecepcionado.objects.pendientes().con_alto_descarte(umbral=1.5)

    context = {
        'metricas_globales': metricas_globales,
        'reporte_estados': reporte_estados,
        'fundos_resumen': fundos_resumen,
        'lotes_criticos': lotes_criticos,
    }
    return render(request, 'agrotrace/reporte.html', context)