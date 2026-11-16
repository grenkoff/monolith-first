"""Names that import statements bind to the network or to other modules."""

import ast
import re
from collections.abc import Iterator
from typing import Final, Protocol, final, override

import attrs

PUBLIC_PACKAGE: Final = re.compile(r'server\.apps\.(?P<module>\w+)\.public\b')
_NETWORK_PACKAGES = frozenset(('grpc', 'requests', 'httpx', 'urllib', 'nats'))
_GENERATED_GRPC = '_pb2_grpc'


class Names(Protocol):
    """Names that some Python code binds."""

    def names(self) -> Iterator[str]:
        """Yields the bound names."""


class Bindings(Protocol):
    """Names that some Python code brings in, with the names it binds them to."""

    def pairs(self) -> Iterator[tuple[str, str]]:
        """Yields the full name of each import with its bound name."""


@final
@attrs.define(slots=True, frozen=True)
class ImportBindings(Bindings):
    """Full names an import statement brings in and the names it binds."""

    _node: ast.AST

    @override
    def pairs(self) -> Iterator[tuple[str, str]]:
        """Yields the full name of each import with its bound name."""
        match self._node:
            case ast.Import(names=aliases):
                yield from (
                    (alias.name, alias.asname or alias.name.partition('.')[0])
                    for alias in aliases
                )
            case ast.ImportFrom(module=str() as module, names=aliases):
                yield from (
                    (f'{module}.{alias.name}', alias.asname or alias.name)
                    for alias in aliases
                )
            case _:
                return


@final
@attrs.define(slots=True, frozen=True)
class NetworkImport(Names):
    """Names an import statement binds to network clients."""

    _node: ast.AST

    @override
    def names(self) -> Iterator[str]:
        """Yields the names bound to network packages or gRPC stubs."""
        yield from (
            name
            for source, name in ImportBindings(self._node).pairs()
            if source.partition('.')[0] in _NETWORK_PACKAGES
            or _GENERATED_GRPC in source
        )


@final
@attrs.define(slots=True, frozen=True)
class FacadeImport(Names):
    """Names an import statement binds to the public package of another module."""

    _node: ast.AST
    _owner: str

    @override
    def names(self) -> Iterator[str]:
        """Yields the names bound to public packages of modules but the owner."""
        for source, name in ImportBindings(self._node).pairs():
            found = PUBLIC_PACKAGE.match(source)
            if found and found['module'] != self._owner:
                yield name
