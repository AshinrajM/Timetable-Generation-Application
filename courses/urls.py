from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PeriodViewSet,CourseViewSet,StaffViewSet

router = DefaultRouter()
router.register(r"periods", PeriodViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'staff', StaffViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
