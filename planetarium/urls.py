from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, \
    TokenRefreshView

from planetarium.views import (
    ShowThemeViewSet,
    AstronomyShowViewSet,
    PlanetariumDomeViewSet,
    ShowSessionViewSet,
    TicketViewSet,
    ReservationViewSet,
)

router = routers.DefaultRouter()

router.register("show_themes", ShowThemeViewSet)
router.register("astronomy_shows", AstronomyShowViewSet)
router.register("planetarium_domes", PlanetariumDomeViewSet)
router.register("show_sessions", ShowSessionViewSet)
router.register("tickets", TicketViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
]

app_name = "planetarium"
