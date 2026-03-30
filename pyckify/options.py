from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union


@dataclass
class Option:
    """A selectable item in a Pyckify picker.

    Parameters
    ----------
    label       : Display text shown in the list.
    value       : Arbitrary payload returned on selection (defaults to ``label``).
    description : Short helper text rendered beside the label.
    enabled     : When *False* the option is shown but cannot be selected.
    shortcut    : Single character that jumps to / selects this option.
    icon        : Emoji or ASCII prefix prepended to the label.
    group       : Group name used when ``group_by`` is set on the picker.
    tags        : Free-form tags used for display and tag-filter mode.
    preview     : Long-form text shown in the optional preview pane.
    style       : Optional Rich style override (overrides theme for this row).
    metadata    : Arbitrary dict for application-specific data.
    """

    label: str
    value: Union[object, str, Any] = None
    description: Optional[str] = None
    enabled: bool = True
    shortcut: Optional[str] = None
    icon: Optional[str] = None
    group: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    preview: Optional[str] = None          # NEW – shown in side/bottom preview pane
    style: Optional[str] = None            # NEW – per-row Rich style string
    metadata: Dict[str, Any] = field(default_factory=dict)  # NEW – app data bag

    def __post_init__(self) -> None:
        # If no explicit value given, default to the label string
        if self.value is None:
            self.value = self.label

    def match(self, query: str) -> bool:
        """Return True if *query* is found anywhere in searchable text."""
        query = query.lower()
        searchable = " ".join(
            filter(None, [self.label, self.description, " ".join(self.tags)])
        ).lower()
        return query in searchable

    def fuzzy_score(self, query: str) -> int:
        """
        Very lightweight fuzzy score: higher = better match.
        Returns 0 when there is no match at all.
        """
        if not query:
            return 1
        q = query.lower()
        text = self.label.lower()
        # Exact substring → best score
        if q in text:
            return 100 - text.index(q)
        # All characters present in order
        pos = 0
        score = 0
        for ch in q:
            idx = text.find(ch, pos)
            if idx == -1:
                return 0
            score += 1
            pos = idx + 1
        return max(1, score)


@dataclass
class Separator(Option):
    """A non-selectable visual separator / section header."""

    def __init__(self, label: str = "─" * 30, description: Optional[str] = None):
        super().__init__(label, description=description, enabled=False)

def make_options(items: List[Any], label_fn: Callable[[Any], str] = str,
                 **kwargs) -> List[Option]:
    """Wrap any list of objects in Option instances.

    Example
    -------
    >>> make_options([1, 2, 3], label_fn=lambda x: f"Item {x}")
    """
    return [Option(label=label_fn(item), value=item, **kwargs) for item in items]


def from_dict(data: List[Dict[str, Any]]) -> List[Option]:
    """Build Option list from a list of dicts (keys match Option fields).

    Example
    -------
    >>> from_dict([{"label": "Alpha", "tags": ["a"]}, {"label": "Beta"}])
    """
    return [Option(**{k: v for k, v in d.items() if k in Option.__dataclass_fields__})
            for d in data]
