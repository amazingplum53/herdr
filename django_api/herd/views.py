from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Count, OuterRef, Subquery, DecimalField, Avg
from django.db.models.functions import TruncDate

from .models import Farm, FarmMembership, Herd, Pasture, Animal, Measurement
from .serializers import (
    FarmSerializer,
    HerdSerializer,
    PastureSerializer,
    AnimalSerializer,
    MeasurementSerializer,
)
from .permissions import IsFarmMember


class FarmViewSet(viewsets.ModelViewSet):
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Farm.objects.filter(
            users=self.request.user
        )

    def perform_create(self, serializer):
        farm = serializer.save()
        FarmMembership.objects.create(
            farm=farm,
            user=self.request.user,
            role="admin",
        )


class HerdViewSet(viewsets.ModelViewSet):
    serializer_class = HerdSerializer
    permission_classes = [IsAuthenticated, IsFarmMember]

    def get_queryset(self):
        return (
            Herd.objects
            .filter(
                farm_id=self.kwargs["farm_pk"],
                farm__users=self.request.user,
            )
            .annotate(animal_count=Count("animals"))
            .prefetch_related("animals")
        )

    def perform_create(self, serializer):
        serializer.save(farm_id=self.kwargs["farm_pk"])


class PastureViewSet(viewsets.ModelViewSet):
    serializer_class = PastureSerializer
    permission_classes = [IsAuthenticated, IsFarmMember]

    def get_queryset(self):
        return (
            Pasture.objects
            .filter(
                farm_id=self.kwargs["farm_pk"],
                farm__users=self.request.user,
            )
            .prefetch_related("herds")
        )

    def perform_create(self, serializer):
        serializer.save(farm_id=self.kwargs["farm_pk"])


class AnimalViewSet(viewsets.ModelViewSet):
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated, IsFarmMember]

    def get_queryset(self):
        latest_weight = (
            Measurement.objects
            .filter(animal=OuterRef("pk"))
            .order_by("-measured_at")
            .values("weight")[:1]
        )

        queryset = (
            Animal.objects
            .filter(
                herd__farm_id=self.kwargs["farm_pk"],
                herd__farm__users=self.request.user,
            )
            .annotate(
                latest_weight=Subquery(
                    latest_weight,
                    output_field=DecimalField(max_digits=7, decimal_places=2),
                )
            )
            .select_related("herd")
        )

        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(animal_id__icontains=search)

        return queryset


class WeightMeasurementViewSet(viewsets.ModelViewSet):
    serializer_class = MeasurementSerializer
    permission_classes = [IsAuthenticated, IsFarmMember]

    def get_queryset(self):
        return Measurement.objects.filter(
            animal_id=self.kwargs["animal_pk"],
            animal__herd__farm_id=self.kwargs["farm_pk"],
            animal__herd__farm__users=self.request.user,
        ).order_by("measured_at")

    def perform_create(self, serializer):
        serializer.save(animal_id=self.kwargs["animal_pk"])


class HerdPerformanceListView(APIView):
    permission_classes = [IsAuthenticated, IsFarmMember]

    def get(self, request, farm_pk, herd_pk):
        measurements = (
            Measurement.objects.filter(
                animal__herd__farm_id=farm_pk,
                animal__herd_id=herd_pk,
                animal__herd__farm__users=request.user,
            )
            .annotate(date=TruncDate("measured_at"))
            .values("date")
            .annotate(
                average_weight=Avg("weight"),
            )
            .order_by("date")
        )

        return Response(measurements)