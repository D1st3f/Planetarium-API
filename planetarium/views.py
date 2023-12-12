from django.db.models import Count, F
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination


from planetarium.models import (
    AstronomyShow,
    ShowTheme,
    ShowSession,
    PlanetariumDome,
    Ticket,
    Reservation,
)
from planetarium.permissions import (
    IsAdminOrIfAuthenticatedEditOnly,
    IsAdminOrIfAuthenticatedReadOnly,
)

from planetarium.serializers import (
    AstronomyShowSerializer,
    AstronomyShowDetailSerializer,
    ShowThemeSerializer,
    ShowSessionSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer,
    PlanetariumDomeSerializer,
    TicketSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
    ReservationSerializer,
    ReservationDetailSerializer,
)


class OrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedEditOnly,)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("show_theme")
    serializer_class = AstronomyShowSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAdminOrIfAuthenticatedEditOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        return self.serializer_class


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAdminOrIfAuthenticatedEditOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ReservationDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = Reservation.objects.filter(user=self.request.user)
        if self.action in ["list", "retrieve"]:
            queryset = queryset.prefetch_related(
                "tickets__show_session__astronomy_show",
                "tickets__show_session__planetarium_dome",
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAdminOrIfAuthenticatedEditOnly,)

    def get_queryset(self):
        queryset = Ticket.objects.filter(reservation__user=self.request.user)

        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related(
                "show_session__astronomy_show",
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketDetailSerializer
        if self.action == "list":
            return TicketListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        reservation = Reservation.objects.create(user=self.request.user)
        serializer.save(reservation=reservation)


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        planetarium_dome = self.request.query_params.get(
            "planetarium_dome", None
        )
        astronomy_show = self.request.query_params.get("astronomy_show", None)

        if astronomy_show:
            astronomy_show_ids = self._params_to_ints(astronomy_show)
            queryset = ShowSession.objects.filter(
                astronomy_show__id__in=astronomy_show_ids
            )

        if planetarium_dome:
            planetarium_dome_ids = self._params_to_ints(planetarium_dome)
            queryset = ShowSession.objects.filter(
                planetarium_dome__id__in=planetarium_dome_ids
            )

        if self.action == "list":
            capacity = F("planetarium_dome__rows") * F(
                "planetarium_dome__seats_in_row"
            )
            queryset = queryset.select_related(
                "astronomy_show", "planetarium_dome"
            ).annotate(tickets_left=capacity - Count("tickets"))

        if self.action == "retrieve":
            queryset = queryset.select_related(
                "astronomy_show", "planetarium_dome"
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="astronomy_show",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by Astronomy Show id ("
                "astronomy_show=1,2)",
            ),
            OpenApiParameter(
                name="planetarium_dome",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by Planetarium Dome id ("
                "planetarium_dome=1,2)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
