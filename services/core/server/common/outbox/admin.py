"""Admin panel of the outbox."""

from django.contrib import admin

from server.common.outbox.models import Event

admin.site.register(Event)
