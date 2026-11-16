"""Calls in Python code and the names they start from."""

import ast
from collections.abc import Iterator
from typing import Protocol, final, override

import attrs

_ON_COMMIT = 'on_commit'


class Target(Protocol):
    """Python call that may reach one of some names."""

    def reaches(self, names: frozenset[str]) -> bool:
        """Returns true when the call starts from one of the names."""


class Calls(Protocol):
    """Calls that some Python code makes."""

    def calls(self) -> Iterator[ast.Call]:
        """Yields the calls in the order they appear."""


@final
@attrs.define(slots=True, frozen=True)
class EagerCalls(Calls):
    """Calls that code makes at once, leaving out code given to `on_commit`."""

    _node: ast.AST

    @override
    def calls(self) -> Iterator[ast.Call]:
        """Yields the calls of the node and its children, outside `on_commit`."""
        if isinstance(self._node, ast.Call):
            if ast.unparse(self._node.func).rpartition('.')[2] == _ON_COMMIT:
                return
            yield self._node
        for child in ast.iter_child_nodes(self._node):
            yield from EagerCalls(child).calls()


@final
@attrs.define(slots=True, frozen=True)
class CallRoot(Target):
    """Call seen by the name it starts from, as `grpc` in `grpc.connect()`."""

    _call: ast.Call

    @override
    def reaches(self, names: frozenset[str]) -> bool:
        """Returns true when the called expression starts from one of the names."""
        target = self._call.func
        while isinstance(target, ast.Attribute):
            target = target.value
        return isinstance(target, ast.Name) and target.id in names
