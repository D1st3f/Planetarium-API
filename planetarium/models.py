from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class ShowTheme(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    show_theme = models.ManyToManyField(
        "ShowTheme",
        related_name="astronomy_shows",
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        AstronomyShow, on_delete=models.CASCADE, related_name="show_sessions"
    )
    planetarium_dome = models.ForeignKey(
        PlanetariumDome,
        on_delete=models.SET_NULL,
        null=True,
        related_name="show_sessions",
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["-show_time"]

    def __str__(self) -> str:
        return self.astronomy_show.title

    def clean(self):
        if self.show_time <= timezone.now():
            raise ValidationError("Show session must be in future.")


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (f"Reservation №{self.id}, "
                f"created at: {self.created_at}")


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(
        ShowSession, on_delete=models.CASCADE, related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tickets",
    )

    class Meta:
        unique_together = ("row", "seat", "show_session")
        ordering = ["-reservation__created_at"]

    def __str__(self):
        return (
            f"{str(self.show_session)} (row: {self.row}, seat: {self.seat})"
        )

    @staticmethod
    def validate_seat_and_row(
        seat: int, num_seat: int, row: int, num_rows: int
    ) -> None:
        if row > num_rows or row <= 0:
            raise ValidationError("Incorrect row number.")
        if seat > num_seat or seat <= 0:
            raise ValidationError("Incorrect seat number.")

    def clean(self) -> None:
        Ticket.validate_seat_and_row(
            seat=self.seat,
            num_seat=self.show_session.planetarium_dome.seats_in_row,
            row=self.row,
            num_rows=self.show_session.planetarium_dome.rows,
        )
