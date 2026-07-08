from django.db.models import Count, Avg
from rest_framework import serializers
from .models import Farm, Herd, Pasture, Animal, Measurement


class FarmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Farm
        fields = ["id", "name"]


class HerdAnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ["id", "animal_id", "species"]


class HerdSerializer(serializers.ModelSerializer):
    animal_count = serializers.IntegerField(read_only=True)
    animals = HerdAnimalSerializer(many=True, read_only=True)

    class Meta:
        model = Herd
        fields = ["id", "farm", "name", "animal_count", "animals"]


class PastureSerializer(serializers.ModelSerializer):
    herd_names = serializers.SerializerMethodField()
    herds = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Herd.objects.all(),
        required=False,
    )

    class Meta:
        model = Pasture
        fields = ["id", "farm", "name", "herds", "herd_names"]

    def get_herd_names(self, pasture):
        return [herd.name for herd in pasture.herds.all()]


class AnimalSerializer(serializers.ModelSerializer):
    latest_weight = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)

    class Meta:
        model = Animal
        fields = ["id", "herd", "animal_id", "species", "latest_weight"]


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ["id", "animal", "weight", "measured_at"]
        read_only_fields = ["animal"]