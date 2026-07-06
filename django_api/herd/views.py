# views.py

from rest_framework import viewsets
from django.db.models import Count, OuterRef, Subquery, DecimalField

from .models import Farm, Herd, Pasture, Animal, Measurement
from .serializers import (
    FarmSerializer,
    HerdSerializer,
    PastureSerializer,
    AnimalSerializer,
    MeasurementSerializer,
)


class FarmViewSet(viewsets.ModelViewSet):
    serializer_class = FarmSerializer
    queryset = Farm.objects.all()


class HerdViewSet(viewsets.ModelViewSet):
    serializer_class = HerdSerializer

    def get_queryset(self):

        return (
            Herd.objects
            .filter(farm_id=self.kwargs["farm_pk"])
            .annotate(animal_count=Count("animals"))
        )

    def perform_create(self, serializer):
        serializer.save(farm_id=self.kwargs["farm_pk"])


class PastureViewSet(viewsets.ModelViewSet):
    serializer_class = PastureSerializer

    def get_queryset(self):
        return Pasture.objects.filter(
            farm_id=self.kwargs["farm_pk"]
        ).prefetch_related("herds")

    def perform_create(self, serializer):
        serializer.save(farm_id=self.kwargs["farm_pk"])


class AnimalViewSet(viewsets.ModelViewSet):
    serializer_class = AnimalSerializer

    def get_queryset(self):

        latest_weight = (
            WeightMeasurement.objects
            .filter(animal=OuterRef("pk"))
            .order_by("-measured_at")
            .values("weight")[:1]
        )

        return (
            Animal.objects
            .filter(farm_id=self.kwargs["farm_pk"])
            .annotate(
                latest_weight=Subquery(
                    latest_weight,
                    output_field=DecimalField(
                        max_digits=7,
                        decimal_places=2,
                    ),
                )
            )
        )

    def perform_create(self, serializer):
        serializer.save(farm_id=self.kwargs["farm_pk"])


class WeightMeasurementViewSet(viewsets.ModelViewSet):
    serializer_class = MeasurementSerializer

    def get_queryset(self):
        return Measurement.objects.filter(
            animal_id=self.kwargs["animal_pk"],
            animal__farm_id=self.kwargs["farm_pk"],
        )

    def perform_create(self, serializer):
        serializer.save(animal_id=self.kwargs["animal_pk"])