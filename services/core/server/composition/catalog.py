"""Objects of the catalog, built for the composition root."""

import punq

from server.apps.catalog.infra import products, ranking
from server.apps.catalog.logic.usecases import (
    add_product,
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
    return stored
