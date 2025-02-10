from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

@dataclass
class Option:
    label: str
    value: Union[object, str, Any] = None
    description: Optional[str] = None
    enabled: bool = True
    shortcut: Optional[str] = None
    icon: Optional[str] = None
    group: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class Separator(Option):
    def __init__(self, label: str, description: Optional[str] = None):
        super().__init__(label, description=description, enabled=False)
        