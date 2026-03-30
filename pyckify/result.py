from __future__ import annotations
from typing import Any, Iterator, List, NamedTuple, Union


class PickResult(NamedTuple):
    """The return value from a Pyckify picker.

    Attributes
    ----------
    values  : The selected option value(s) – a single item or a list in
              multiselect mode.
    indices : The original list index / indices of the selected option(s).
    """

    values: Union[List[Any], Any]
    indices: Union[List[int], int]

    @property
    def is_multi(self) -> bool:
        return isinstance(self.values, list)

    @property
    def as_list(self) -> List[Any]:
        """Always return a list, even for single-select results."""
        return self.values if self.is_multi else [self.values]

    @property
    def index_list(self) -> List[int]:
        return self.indices if self.is_multi else [self.indices]

    def __iter__(self) -> Iterator:  # type: ignore[override]
        # Preserve original tuple iteration
        yield self.values
        yield self.indices

    def __bool__(self) -> bool:
        if self.is_multi:
            return bool(self.values)
        return self.values is not None
