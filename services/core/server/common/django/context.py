"""Values that every template of the site reads."""

from django.conf import settings
from django.http import HttpRequest


def site(_request: HttpRequest) -> dict[str, str]:
    """Returns the name of the site for the layout."""
    return {'site_name': settings.SITE_NAME}
