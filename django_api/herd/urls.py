# urls.py
from rest_framework_nested import routers
from .views import FarmViewSet, HerdViewSet, PastureViewSet, AnimalViewSet, WeightMeasurementViewSet

router = routers.DefaultRouter()
router.register("farms", FarmViewSet, basename="farm")

farm_router = routers.NestedDefaultRouter(router, "farms", lookup="farm")
farm_router.register("herds", HerdViewSet, basename="farm-herds")
farm_router.register("pastures", PastureViewSet, basename="farm-pastures")
farm_router.register("animals", AnimalViewSet, basename="farm-animals")

animal_router = routers.NestedDefaultRouter(farm_router, "animals", lookup="animal")
animal_router.register("weights", WeightMeasurementViewSet, basename="animal-weights")

urlpatterns = router.urls + farm_router.urls + animal_router.urls