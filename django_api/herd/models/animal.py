from django.db import models
from .farm import Pasture, Farm

class Herd(models.Model):

    name = models.CharField(max_length=200)

    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="herds",
    )

class Species(models.TextChoices):
    SHEEP = "sheep", "Sheep"
    CATTLE = "cattle", "Cattle"
    PIG = "pig", "Pig"


class Animal(models.Model):

    species = models.CharField(max_length=20, choices=Species.choices)

    farm_id = models.CharField(max_length=100)

    herd = models.ForeignKey(
        Herd,
        on_delete=models.PROTECT,
        related_name="animals",
    )


    
