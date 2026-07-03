from django.db import models


class Farm(models.Model):

    name = models.CharField(max_length=200)
    address_line_1 = models.CharField(max_length=200)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=100)


class Pasture(models.Model):

    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="pastures",
    )

    herds = models.ManyToManyField(
        "Herd",
        related_name="pastures",
        blank=True
    )
