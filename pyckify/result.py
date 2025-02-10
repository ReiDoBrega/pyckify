from typing import Any, List, NamedTuple, Union

class PickResult(NamedTuple):
    values: Union[List[Any], Any]
    indices: Union[List[int], int]
