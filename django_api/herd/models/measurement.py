from django.db import models
from .animal import Animal


class Measurement(models.Model):

    weight = models.DecimalField(max_digits=6, decimal_places=2) # In kg

    measured_at = models.DateTimeField()

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="measurements",
    )