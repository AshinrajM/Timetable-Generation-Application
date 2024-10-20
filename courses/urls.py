from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PeriodViewSet

router = DefaultRouter()
router.register(r"periods", PeriodViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
