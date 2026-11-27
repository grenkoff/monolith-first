"""Root URL configuration of core."""

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admindocs import urls as admindocs_urls
from django.urls import include
from django.views.generic import TemplateView
from dmr.openapi import build_schema
from dmr.openapi.views import (
    OpenAPIJsonView,
    RedocView,
    ScalarView,
    StoplightView,
    SwaggerView,
)
from dmr.openapi.views.yaml import OpenAPIYamlView
from dmr.plugins.msgspec import MsgspecSerializer
from dmr.routing import Router, build_404_handler, build_500_handler, path
from health_check.views import HealthCheckView

from server.apps.appearance.views import urls as appearance_page_urls
from server.apps.catalog.api import urls as catalog_api_urls
from server.apps.catalog.views import urls as catalog_page_urls
from server.apps.orders.api import urls as orders_api_urls
from server.apps.orders.views import urls as orders_page_urls
from server.common import health

admin.autodiscover()

router_v1 = Router('v1/')
router_v1.include(health.router, namespace='health')
router_v1.include(catalog_api_urls.router, namespace='catalog')
router_v1.include(orders_api_urls.router, namespace='orders')

router = Router('api/')
router.include(router_v1, namespace='v1')

schema_v1 = build_schema(router)

handler404 = build_404_handler(router.prefix, serializer=MsgspecSerializer)
handler500 = build_500_handler(router.prefix, serializer=MsgspecSerializer)

urlpatterns = [
    # Apis:
    router.to_urlpatterns(namespace='api'),
    # OpenAPI:
    path(
        'docs/v1/openapi.json/',
        staff_member_required(OpenAPIJsonView.as_view(schema_v1)),
        name='v1_openapi_json',
    ),
    path(
        'docs/v1/openapi.yaml/',
        staff_member_required(OpenAPIYamlView.as_view(schema_v1)),
        name='v1_openapi_yaml',
    ),
    path(
        'docs/v1/stoplight/',
        staff_member_required(StoplightView.as_view(schema_v1)),
        name='v1_stoplight',
    ),
    path(
        'docs/v1/swagger/',
        staff_member_required(SwaggerView.as_view(schema_v1)),
        name='v1_swagger',
    ),
    path(
        'docs/v1/scalar/',
        staff_member_required(ScalarView.as_view(schema_v1)),
        name='v1_scalar',
    ),
    path(
        'docs/v1/redoc/',
        staff_member_required(RedocView.as_view(schema_v1)),
        name='v1_redoc',
    ),
    # Pages:
    path('', include((appearance_page_urls.urlpatterns, 'appearance'))),
    path('', include((catalog_page_urls.urlpatterns, 'catalog'))),
    path('', include((orders_page_urls.urlpatterns, 'orders'))),
    path(
        'design/',
        TemplateView.as_view(
            template_name='design/index.html',
            extra_context={'themes': settings.SITE_THEMES},
        ),
        name='design',
    ),
    # Health checks:
    path(
        'health/',
        HealthCheckView.as_view(
            checks=[
                'health_check.Cache',
                'health_check.Database',
                'health_check.Storage',
            ],
        ),
        name='health_check',
    ),
    # django-admin:
    path('admin/doc/', include(admindocs_urls)),
    path('admin/', admin.site.urls),
    # Text and xml static files:
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='common/txt/robots.txt',
            content_type='text/plain',
        ),
        name='robots_txt',
    ),
    path(
        'humans.txt',
        TemplateView.as_view(
            template_name='common/txt/humans.txt',
            content_type='text/plain',
        ),
        name='humans_txt',
    ),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns = [
        # URLs specific only to django-debug-toolbar:
        path('__debug__/', include(debug_toolbar.urls)),
        *urlpatterns,
        # Serving media files in development only:
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
