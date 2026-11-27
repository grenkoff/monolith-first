"""Pages of appearance rendered on the server."""

from typing import final

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from server.apps.appearance.logic.themes import UnknownThemeError
from server.apps.appearance.logic.usecases.choose_theme import ChooseTheme
from server.common.di import HasContainer


@final
class ThemeForm(HasContainer, View):
    """Form in the header where staff choose the theme of the whole site."""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Chooses the theme from the form and returns to the page it came from."""
        if not request.user.is_staff:
            raise PermissionDenied
        try:
            self.resolve(ChooseTheme)(request.POST.get('theme', ''))
        except UnknownThemeError:
            return HttpResponseBadRequest('The site has no such theme.')
        page = request.POST.get('next', '')
        safe = url_has_allowed_host_and_scheme(
            page,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
        return redirect(page if safe else '/')
