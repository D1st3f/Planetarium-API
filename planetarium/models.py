from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


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
        "ShowTheme", related_name="astronomy_show"
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return f"{self.name}"


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(AstronomyShow, on_delete=models.CASCADE)
    planetarium_dome = models.ForeignKey(
        PlanetariumDome, on_delete=models.SET_NULL, null=True
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["-show_time"]

    def __str__(self) -> str:
        return f"{self.astronomy_show.title}"

    def clean(self):
        if self.show_time <= timezone.now():
            raise ValidationError("Show session must be in future.")


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return (
            f"{self.user.first_name} {self.user.last_name} - "
            f"{self.created_at.ctime()}"
        )


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(ShowSession, on_delete=models.CASCADE)
    reservation = models.ForeignKey(
        Reservation, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        unique_together = ("row", "seat", "show_session")
        ordering = ["-reservation__created_at"]

    def __str__(self) -> str:
        return (
            f"{self.id} - {self.reservation.user.last_name} "
            f"{self.reservation.user.first_name} "
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
