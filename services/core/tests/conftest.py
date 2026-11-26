"""Pytest configuration, fixtures and plugins of core."""

pytest_plugins = [
    'tests.plugins.django_settings',
    'tests.plugins.tracecov_map',
    'tests.plugins.hypothesis_profiles',
    'tests.plugins.images_server',
]
