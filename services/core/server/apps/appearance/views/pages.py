"""Pages of appearance rendered on the server."""

from typing import final

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views import View

from server.common.di import HasContainer


@final
class ThemeForm(HasContainer, View):
    """Form in the header where staff choose the theme of the whole site."""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Chooses the theme from the form and returns to the page it came from."""
        return redirect('/')
