"""Objects of the greetings app, built for the composition root."""

import punq
from django.conf import settings

from server.apps.greetings.infra import remote
from server.apps.greetings.logic.usecases import greet


def inject(container: punq.Container) -> None:
    """Registers the objects of the greetings app in the container."""
    container.register(
        greet.Greet,
        instance=greet.Greet(remote.RemoteGreetings(settings)),
    )
