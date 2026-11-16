"""Serializers shared by the HTTP APIs."""

from collections.abc import Mapping
from typing import Any, final, override

import attrs
from dmr.plugins.msgspec import MsgspecSerializer


@final
@attrs.define(slots=True, frozen=True)
class WholeNumbers:
    """JSON data whose floats without a fractional part are integers."""

    _parsed: object

    def normalized(self) -> object:
        """Returns the data with every whole float turned into an integer."""
        return self._normalized(self._parsed)

    def _normalized(self, node: object) -> object:
        """Turns whole floats into integers, looking into objects and arrays."""
        match node:
            case float() if node.is_integer():
                return int(node)
            case dict():
                return {key: self._normalized(member) for key, member in node.items()}
            case list():
                return [self._normalized(element) for element in node]
            case _:
                return node


@final
class StrictMsgspecSerializer(MsgspecSerializer):
    """Msgspec serializer that reads whole floats as integers, strictly."""

    @override
    @classmethod
    def from_python(
        cls,
        unstructured: Any,
        model: Any,
        *,
        strict: bool | None,
        extra_namespace: Mapping[str, Any] | None = None,
    ) -> Any:
        """Converts data to the model, strictly unless told otherwise."""
        return super().from_python(
            WholeNumbers(unstructured).normalized(),
            model,
            strict=strict is not False,
            extra_namespace=extra_namespace,
        )
