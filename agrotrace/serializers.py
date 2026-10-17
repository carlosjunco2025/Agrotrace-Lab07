from rest_framework import serializers

from .models import (
    CertificacionAgricola,
    CertificacionLote,
    EvaluacionCalidadLote,
    FundoProductor,
    LoteRecepcionado,
)


class LoteSimpleSerializer(serializers.ModelSerializer):
    fundo = serializers.PrimaryKeyRelatedField(
        queryset=FundoProductor.objects.all(),
    )
    estado_evaluacion = serializers.ChoiceField(
        choices=LoteRecepcionado.ESTADOS,
        default='PENDIENTE',
    )

    class Meta:
        model = LoteRecepcionado
        fields = (
            'id',
            'codigo_lote',
            'toneladas_brutas',
            'porcentaje_descarte',
            'estado_evaluacion',
            'fundo',
        )
        read_only_fields = ('id',)

    def validate_toneladas_brutas(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Las toneladas brutas deben ser mayores a 0.'
            )
        return value


class FundoProductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundoProductor
        fields = (
            'id',
            'nombre_fundo',
            'propietario_dni_ruc',
            'hectareas',
            'valido_exportacion',
            'cupo_diario_lotes',
        )

    def validate_hectareas(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Las hectáreas deben ser mayores a 0.'
            )
        return value


class EvaluacionCalidadSerializer(serializers.ModelSerializer):
    lote = serializers.PrimaryKeyRelatedField(
        queryset=LoteRecepcionado.objects.all(),
    )

    class Meta:
        model = EvaluacionCalidadLote
        fields = (
            'id',
            'lote',
            'nivel_brix',
            'firmeza_fruto',
            'observaciones',
            'fecha_evaluacion',
        )


class LoteDeEvaluacionSerializer(serializers.ModelSerializer):
    fundo = FundoProductorSerializer(read_only=True)

    class Meta:
        model = LoteRecepcionado
        fields = ('id', 'codigo_lote', 'fundo')


class EvaluacionCalidadDetalladaSerializer(serializers.ModelSerializer):
    lote = LoteDeEvaluacionSerializer(read_only=True)

    class Meta:
        model = EvaluacionCalidadLote
        fields = (
            'id',
            'lote',
            'nivel_brix',
            'firmeza_fruto',
            'observaciones',
            'fecha_evaluacion',
        )


class CertificacionAgricolaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificacionAgricola
        fields = ('id', 'nombre_certificacion', 'entidad_emisora')


FundoSerializer = FundoProductorSerializer
EvaluacionSerializer = EvaluacionCalidadSerializer
CertificacionSerializer = CertificacionAgricolaSerializer


class CertificacionLoteSerializer(serializers.ModelSerializer):
    certificacion = CertificacionSerializer(read_only=True)

    class Meta:
        model = CertificacionLote
        fields = (
            'certificacion',
            'fecha_auditoria',
            'codigo_inspeccion',
            'costo_auditoria',
        )


class LoteDetalladoSerializer(serializers.ModelSerializer):
    fundo = FundoProductorSerializer(read_only=True)
    evaluacioncalidadlote = EvaluacionCalidadSerializer(
        source='evaluacion_calidad',
        read_only=True,
    )
    certificaciones_lote = CertificacionLoteSerializer(
        source='certificacionlote_set',
        many=True,
        read_only=True,
    )

    class Meta:
        model = LoteRecepcionado
        fields = (
            'id',
            'codigo_lote',
            'toneladas_brutas',
            'porcentaje_descarte',
            'estado_evaluacion',
            'fecha_ingreso',
            'fundo',
            'evaluacioncalidadlote',
            'certificaciones_lote',
        )
