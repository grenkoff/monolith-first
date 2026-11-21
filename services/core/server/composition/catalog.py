"""Objects of the catalog, built for the composition root."""

import punq
from django.conf import settings

from server.apps.catalog.infra import photos, products, ranking, remote
from server.apps.catalog.logic.usecases import (
    add_product,
    attach_photo,
    find_photo,
    find_product,
    list_products,
    search_products,
)
from server.apps.catalog.public.products import Catalog


def inject(container: punq.Container) -> Catalog:
    """Registers the objects of the catalog and returns its facade."""
    stored = products.StoredProducts()
    container.register(
        add_product.AddProduct,
        instance=add_product.AddProduct(stored),
    )
    container.register(
        find_product.FindProduct,
        instance=find_product.FindProduct(stored),
    )
    container.register(
        list_products.ListProducts,
        instance=list_products.ListProducts(stored),
    )
    container.register(
        search_products.SearchProducts,
        instance=search_products.SearchProducts(
            stored,
            ranking.RustSimilarity(),
        ),
    )
    album = photos.StoredPhotos()
    container.register(
        attach_photo.AttachPhoto,
        instance=attach_photo.AttachPhoto(
            stored,
            remote.RemoteThumbnails(settings),
            album,
        ),
    )
    container.register(
        find_photo.FindPhoto,
        instance=find_photo.FindPhoto(album),
    )
    return stored
