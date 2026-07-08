# permissions.py
from rest_framework.permissions import BasePermission
from .models import FarmMembership


class IsFarmMember(BasePermission):
    def has_permission(self, request, view):
        farm_id = view.kwargs.get("farm_pk") or view.kwargs.get("pk")

        if not farm_id:
            return request.user and request.user.is_authenticated

        return FarmMembership.objects.filter(
            farm_id=farm_id,
            user=request.user,
        ).exists()