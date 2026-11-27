"""Admin panel of appearance."""

from typing import final, override

from django.contrib import admin
from django.http import HttpRequest

from server.apps.appearance.models import ThemeChoice


@final
class ThemeChoiceAdmin(admin.ModelAdmin[ThemeChoice]):
    """Journal of the themes staff chose in the header, read only."""

    list_display = ('name', 'id')

    @override
    def has_add_permission(self, request: HttpRequest) -> bool:
        """Forbids adding, so a theme is chosen only in the header."""
        return False

    @override
    def has_change_permission(
        self,
        request: HttpRequest,
        _choice: ThemeChoice | None = None,
    ) -> bool:
        """Forbids changing, so the journal stays as it was written."""
        return False


admin.site.register(ThemeChoice, ThemeChoiceAdmin)
