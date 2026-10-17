from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import EvaluacionCalidadLote, FundoProductor, LoteRecepcionado
from .serializers import (
    EvaluacionCalidadSerializer,
    EvaluacionCalidadDetalladaSerializer,
    FundoProductorSerializer,
    LoteDetalladoSerializer,
    LoteSimpleSerializer,
)


class EstadoFilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado_evaluacion=estado)
        return queryset


class FundoProductorViewSet(viewsets.ModelViewSet):
    queryset = FundoProductor.objects.all()
    serializer_class = FundoProductorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre_fundo', 'propietario_dni_ruc']
    ordering_fields = ['hectareas', 'id']


class EvaluacionCalidadViewSet(viewsets.ModelViewSet):
    queryset = EvaluacionCalidadLote.objects.select_related('lote')
    serializer_class = EvaluacionCalidadSerializer


class EvaluacionCalidadDetalladaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EvaluacionCalidadDetalladaSerializer

    def get_queryset(self):
        queryset = EvaluacionCalidadLote.objects.select_related(
            'lote',
            'lote__fundo',
        )
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(lote__estado_evaluacion=estado)
        return queryset

    @action(detail=False, methods=['get'])
    def aprobados(self, request):
        evaluaciones_aprobadas = self.get_queryset().filter(
            lote__in=LoteRecepcionado.objects.aprobados(),
        )
        serializer = self.get_serializer(evaluaciones_aprobadas, many=True)
        return Response(serializer.data)


class LoteViewSet(EstadoFilterMixin, viewsets.ModelViewSet):
    queryset = LoteRecepcionado.objects.all()
    serializer_class = LoteSimpleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo_lote']
    ordering_fields = ['toneladas_brutas', 'id']

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        lotes_pendientes = self.get_queryset().pendientes()
        serializer = self.get_serializer(lotes_pendientes, many=True)
        return Response(serializer.data)


class LoteDetalladoViewSet(EstadoFilterMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = LoteDetalladoSerializer
    queryset = LoteRecepcionado.objects.select_related(
        'fundo',
        'evaluacion_calidad',
    ).prefetch_related(
        'certificacionlote_set__certificacion',
    )

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        lotes_pendientes = self.get_queryset().pendientes()
        serializer = self.get_serializer(lotes_pendientes, many=True)
        return Response(serializer.data)
