from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import (
    EvaluacionCalidadViewSet,
    EvaluacionCalidadDetalladaViewSet,
    FundoProductorViewSet,
    LoteDetalladoViewSet,
    LoteViewSet,
)
from . import views

app_name = 'agrotrace'

router = DefaultRouter()
router.register(r'fundos', FundoProductorViewSet, basename='fundo')
router.register(
    r'evaluaciones',
    EvaluacionCalidadViewSet,
    basename='evaluacion',
)
router.register(
    r'evaluaciones-detalladas',
    EvaluacionCalidadDetalladaViewSet,
    basename='evaluacion-detallada',
)
router.register(r'lotes', LoteViewSet, basename='lote')
router.register(
    r'lotes-detallados',
    LoteDetalladoViewSet,
    basename='lote-detallado-api',
)

urlpatterns = [
    # Fundos
    path('fundos/', views.fundo_list, name='fundo_list'),
    path('fundos/nuevo/', views.fundo_create, name='fundo_create'),
    path('fundos/editar/<int:pk>/', views.fundo_update, name='fundo_update'),
    path('fundos/eliminar/<int:pk>/', views.fundo_delete, name='fundo_delete'),

    # Lotes
    path('lotes/', views.lote_list, name='lote_list'),
    path('lotes/nuevo/', views.lote_create, name='lote_create'),
    path('lotes/editar/<int:pk>/', views.lote_update, name='lote_update'),
    path('lotes/eliminar/<int:pk>/', views.lote_delete, name='lote_delete'),

    # Operación Transaccional (Ejercicio 3 - Lab 07)
    path(
        'recepcion-transaccional/',
        views.recepcion_transaccional,
        name='recepcion_transaccional',
    ),

    # Reporte General (Ejercicio 6 - Lab 07)
    path('reporte/', views.reporte_general, name='reporte_general'),

    # API REST
    path('api/', include(router.urls)),
]