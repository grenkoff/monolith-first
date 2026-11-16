"""Composition root: binds every protocol to its implementation."""

import punq


def _inject_main(container: punq.Container) -> None:
    """Registers the objects of the main app in the container."""
    from server.apps.main.infra import mappers, repository
    from server.apps.main.logic.usecases import blogpost_create, blogpost_get

    stored = repository.BlogPostRepo()
    mapper = mappers.BlogPostMapper()
    container.register(
        blogpost_create.CreateBlogPost,
        instance=blogpost_create.CreateBlogPost(stored, mapper),
    )
    container.register(
        blogpost_get.GetBlogPost,
        instance=blogpost_get.GetBlogPost(stored, mapper),
    )


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


def populate_dependencies(container: punq.Container) -> punq.Container:
    """Registers the objects of every module in the container."""
    _inject_main(container)
    _inject_greetings(container)
    _inject_catalog(container)
    return container
