from django.test import TestCase
from django.contrib.auth.models import User
from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Ticket,
    Reservation,
)
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from datetime import timedelta


class ShowThemeModelTest(TestCase):
    def test_show_theme_str(self):
        theme = ShowTheme.objects.create(name="Galactic Exploration")
        self.assertEqual(str(theme), theme.name)


class AstronomyShowModelTest(TestCase):
    def test_astronomy_show_str(self):
        show = AstronomyShow.objects.create(
            title="Journey Through the Stars",
            description="A fascinating tour of the universe.",
        )
        self.assertEqual(str(show), show.title)


class PlanetariumDomeModelTest(TestCase):
    def test_planetarium_dome_capacity(self):
        dome = PlanetariumDome.objects.create(
            name="Dome 1", rows=10, seats_in_row=20
        )
        self.assertEqual(dome.capacity, 200)


class ShowSessionModelTest(TestCase):
    def setUp(self):
        self.show = AstronomyShow.objects.create(
            title="Cosmic Voyage", description="Embark on a cosmic adventure."
        )
        self.dome = PlanetariumDome.objects.create(
            name="Dome 2", rows=5, seats_in_row=15
        )

    def test_show_session_str(self):
        session = ShowSession.objects.create(
            astronomy_show=self.show,
            planetarium_dome=self.dome,
            show_time=timezone.now() + timedelta(days=1),
        )
        self.assertEqual(str(session), session.astronomy_show.title)

    def test_show_session_clean_future_date(self):
        session = ShowSession(
            astronomy_show=self.show,
            planetarium_dome=self.dome,
            show_time=timezone.now() + timedelta(days=1),
        )
        session.clean()

    def test_show_session_clean_past_date(self):
        session = ShowSession(
            astronomy_show=self.show,
            planetarium_dome=self.dome,
            show_time=timezone.now() - timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            session.clean()


class TicketModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.show = AstronomyShow.objects.create(
            title="Stellar Phenomena",
            description="Discover the wonders of stars.",
        )
        self.dome = PlanetariumDome.objects.create(
            name="Dome 3", rows=8, seats_in_row=10
        )
        self.session = ShowSession.objects.create(
            astronomy_show=self.show,
            planetarium_dome=self.dome,
            show_time=timezone.now() + timedelta(days=2),
        )
        self.reservation = Reservation.objects.create(user=self.user)

    def test_ticket_validate_seat_and_row_valid(self):
        Ticket.validate_seat_and_row(seat=5, num_seat=10, row=3, num_rows=8)

    def test_ticket_validate_seat_and_row_invalid_seat(self):
        with self.assertRaises(ValidationError):
            Ticket.validate_seat_and_row(
                seat=11, num_seat=10, row=3, num_rows=8
            )

    def test_ticket_validate_seat_and_row_invalid_row(self):
        with self.assertRaises(ValidationError):
            Ticket.validate_seat_and_row(
                seat=5, num_seat=10, row=9, num_rows=8
            )

    def test_ticket_clean_valid(self):
        ticket = Ticket(row=1, seat=1, show_session=self.session)
        ticket.clean()

    def test_ticket_clean_invalid_seat(self):
        ticket = Ticket(row=1, seat=11, show_session=self.session)
        with self.assertRaises(ValidationError):
            ticket.clean()

    def test_ticket_clean_invalid_row(self):
        ticket = Ticket(row=9, seat=1, show_session=self.session)
        with self.assertRaises(ValidationError):
            ticket.clean()
