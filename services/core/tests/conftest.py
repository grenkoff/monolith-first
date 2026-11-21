"""Pytest configuration, fixtures and plugins of core."""

pytest_plugins = [
    # Should be the first custom one:
    'plugins.django_settings',
    'plugins.tracecov_map',
    'plugins.hypothesis_profiles',
    'plugins.images_server',
    # TODO: add your own plugins here!
]
