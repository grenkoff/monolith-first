"""Tests of the report of calls to other modules inside database transactions."""

from pathlib import Path
from typing import Final

from scripts.transactions import TransactionReport

_ADAPTER: Final = (
    'from django.db import transaction',
    'from server.apps.catalog.public import facade',
    'from server.apps.billing.public import events',
    'with transaction.atomic():',
    '    facade.reserve()',
    '    events.Charged()',
)


def test_reports_facade_call_inside_transaction() -> None:
    adapter = Path('apps/billing/infra/adapters.py')

    problems = list(TransactionReport(adapter, '\n'.join(_ADAPTER)).problems())

    assert problems == [f'{adapter}:5: another module called inside a transaction']
