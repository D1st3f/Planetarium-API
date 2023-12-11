from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from planetarium.models import (
    AstronomyShow,
    ShowTheme,
    ShowSession,
    PlanetariumDome,
    Ticket,
    Reservation,
)


class ShowThemeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=ShowTheme.objects.all(),
                message="This theme with this name already exists.",
            )
        ]
    )

    class Meta:
        model = ShowTheme
        fields = "__all__"


class AstronomyShowSerializer(serializers.ModelSerializer):
    show_theme = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "show_theme")


class AstronomyShowDetailSerializer(AstronomyShowSerializer):
    show_theme = ShowThemeSerializer(many=True, read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                Ticket.objects.all(),
                ["row", "seat", "show_session"],
                message="This seat is already taken.",
            )
        ]

    def validate(self, attrs) -> dict:
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seat_and_row(
            seat=attrs["seat"],
            num_seat=attrs["show_session"].planetarium_dome.seats_in_row,
            row=attrs["row"],
            num_rows=attrs["show_session"].planetarium_dome.rows,
        )
        return data


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = "__all__"


class ShowSessionListSerializer(ShowSessionSerializer):
    planetarium_dome = serializers.StringRelatedField(
        many=False, read_only=True
    )
    astronomy_show = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="title"
    )
    tickets_left = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_time",
            "tickets_left",
        )


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=PlanetariumDome.objects.all(),
                message="Planetarium dome with this name already exists.",
            )
        ]
    )

    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class ShowSessionDetailSerializer(ShowSessionListSerializer):
    planetarium_dome = PlanetariumDomeSerializer(many=False, read_only=True)
    astronomy_show = AstronomyShowSerializer(many=False, read_only=True)
    taken_seats = serializers.SerializerMethodField()

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_time",
            "taken_seats",
        )

    def get_taken_seats(self, obj):
        return obj.tickets.values_list("seat", flat=True)


class TicketListSerializer(TicketSerializer):
    astronomy_show = serializers.CharField(
        source="show_session.astronomy_show.title", read_only=True
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "astronomy_show",
            "row",
            "seat",
        )


class ReservationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["id", "user", "created_at"]


class TicketDetailSerializer(TicketSerializer):
    show_session = ShowSessionListSerializer(read_only=True)
    reservation = ReservationUserSerializer(many=False, read_only=True)


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = "__all__"

    def create(self, validated_data) -> Reservation:
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationDetailSerializer(ReservationSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)
