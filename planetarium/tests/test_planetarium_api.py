from django.urls import reverse

from planetarium.models import (
    PlanetariumDome,
    AstronomyShow,
    ShowSession,
    ShowTheme,
)

SHOW_THEMES_URL = reverse("planetarium:showsession-list")


def sample_astronomy_show(**params):
    defaults = {
        "name": "Sample show",
        "description": "Sample description",
    }
    defaults.update(params)

    return AstronomyShow.objects.create(**defaults)


def sample_show_theme(**params):
    defaults = {
        "name": "Stars",
    }
    defaults.update(params)

    return ShowTheme.objects.create(**defaults)


def sample_show_session(**params):
    planetarium_dome = PlanetariumDome.objects.create(
        name="Cosmos", rows=20, seats_in_row=20
    )

    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "astronomy_show": None,
        "planetarium_dome": planetarium_dome,
    }
    defaults.update(params)

    return ShowSession.objects.create(**defaults)


def detail_url(astronomy_show_id):
    return reverse(
        "planetarium:astronomyshow-detail", args=[astronomy_show_id]
    )
