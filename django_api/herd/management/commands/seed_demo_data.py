from decimal import Decimal
from random import randint, uniform, choice

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from herd.models import Farm, FarmMembership, Herd, Pasture, Animal, Measurement
from herd.models.farm import Membership


class Command(BaseCommand):
    help = "Seeds demo farm data for development and analysis"

    def handle(self, *args, **options):
        User = get_user_model()

        user, _ = User.objects.get_or_create(
            email="matthewpaulh@hotmail.co.uk",
            defaults={
                "password": "abcd1234",
            },
        )

        farm, _ = Farm.objects.get_or_create(
            name="Orchards Farm",
            defaults={
                "address_line_1": "1 Farm Lane",
                "postcode": "CF10 1AA",
                "country": "Wales",
            },
        )

        FarmMembership.objects.get_or_create(
            farm=farm,
            user=user,
            defaults={"role": Membership.ADMIN},
        )

        herd_data = [
            ("Spring Lambs", "sheep"),
            ("Beef Cattle", "cattle"),
            ("Pigs", "pig"),
        ]

        herds = []

        for herd_name, species in herd_data:
            herd, _ = Herd.objects.get_or_create(
                farm=farm,
                name=herd_name,
            )
            herds.append((herd, species))

        pasture_names = ["North Field", "South Meadow", "Hill Pasture"]

        pastures = []

        for name in pasture_names:
            pasture, _ = Pasture.objects.get_or_create(
                farm=farm,
                name=name,
            )
            pastures.append(pasture)

        for pasture in pastures:
            pasture.herds.set([herd for herd, _species in herds])

        today = timezone.now()

        for herd, species in herds:
            for index in range(1, 16):
                animal, _ = Animal.objects.get_or_create(
                    herd=herd,
                    animal_id=f"{herd.name[:3].upper()}-{index:03}",
                    defaults={
                        "species": species,
                    },
                )

                if species == "sheep":
                    starting_weight = Decimal(str(round(uniform(25, 40), 2)))
                    monthly_gain = Decimal(str(round(uniform(2.0, 4.5), 2)))
                elif species == "cattle":
                    starting_weight = Decimal(str(round(uniform(180, 280), 2)))
                    monthly_gain = Decimal(str(round(uniform(15, 35), 2)))
                else:
                    starting_weight = Decimal(str(round(uniform(45, 80), 2)))
                    monthly_gain = Decimal(str(round(uniform(5, 12), 2)))

                for month in range(6):
                    measured_at = today - timezone.timedelta(days=(5 - month) * 30)

                    weight = starting_weight + (monthly_gain * month)

                    weight += Decimal(str(round(uniform(-1.5, 1.5), 2)))

                    Measurement.objects.get_or_create(
                        animal=animal,
                        measured_at=measured_at,
                        defaults={
                            "weight": weight,
                        },
                    )

        self.stdout.write(
            self.style.SUCCESS("Demo farm data created successfully.")
        )