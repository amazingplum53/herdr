from django.db import models
from django.conf import settings


class Farm(models.Model):

    name = models.CharField(max_length=200)
    address_line_1 = models.CharField(max_length=200)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="farms",
        through="FarmMembership",
    )


class Membership(models.TextChoices):
    ADMIN = "admin", "Admin"
    MEMBER = "member", "Member"


class FarmMembership(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")

    role = models.CharField(max_length=50, default="member", choices=Membership.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["farm", "user"],
                name="unique_farm_membership",
            )
        ]


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
