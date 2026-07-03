from django.db.models import Count, Avg
from rest_framework import serializers
from .models import Farm, Herd, Pasture, Animal, WeightMeasurement


class FarmSerializer(serializers.ModelSerializer):
    animal_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Farm
        fields = ["id", "name"]


class HerdSerializer(serializers.ModelSerializer):
    animal_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Herd
        fields = ["id", "farm", "name", "animal_count"]


class PastureSerializer(serializers.ModelSerializer):
    herd_names = serializers.SerializerMethodField()

    class Meta:
        model = Pasture
        fields = ["id", "farm", "name", "herd_names"]

    def get_herd_names(self, pasture):
        return [
            herd.name
            for herd in pasture.herds.all()
        ]


class AnimalSerializer(serializers.ModelSerializer):
    latest_weight = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)

    class Meta:
        model = Animal
        fields = ["id", "farm", "herd", "pasture", "animal_id", "species", "latest_weight"]


class WeightMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightMeasurement
        fields = ["id", "animal", "weight_kg", "measured_at"]
        read_only_fields = ["animal"]