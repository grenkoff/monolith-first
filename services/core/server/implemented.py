"""Composition root: binds every protocol to its implementation."""

import punq


def _inject_greetings(container: punq.Container) -> None:
    """Registers the objects of the greetings app in the container."""
    from django.conf import settings

    from server.apps.greetings.infra import remote
    from server.apps.greetings.logic.usecases import greet

    container.register(
        greet.Greet,
        instance=greet.Greet(remote.RemoteGreetings(settings)),
    )


def _inject_catalog(container: punq.Container) -> None:
    """Registers the objects of the catalog in the container."""
    from server.apps.catalog.infra import products
    from server.apps.catalog.logic.usecases import add_product, find_product

    stored = products.StoredProducts()
    container.register(
        add_product.AddProduct,
        instance=add_product.AddProduct(stored),
    )
    container.register(
        find_product.FindProduct,
        instance=find_product.FindProduct(stored),
    )


def _inject_orders(container: punq.Container) -> None:
    """Registers the objects of orders, with the catalog behind its facade."""
    from server.apps.catalog.infra import products
    from server.apps.orders.infra import catalog, orders
    from server.apps.orders.logic.usecases import find_order, place_order

    stored = orders.StoredOrders()
    container.register(
        place_order.PlaceOrder,
        instance=place_order.PlaceOrder(
            catalog.CatalogPrices(products.StoredProducts()),
            stored,
        ),
    )
    container.register(
        find_order.FindOrder,
        instance=find_order.FindOrder(stored),
    )


def populate_dependencies(container: punq.Container) -> punq.Container:
    """Registers the objects of every module in the container."""
    _inject_greetings(container)
    _inject_catalog(container)
    _inject_orders(container)
    return container
