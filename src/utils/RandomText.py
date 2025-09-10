import random
from typing import Mapping, Sequence, Callable, Any, List, Tuple, Union
import json
Item = Any
MaybeKeyed = Union[Item, Tuple[Any, Item]]

with open ("/content/drive/MyDrive/Text_Cluster/processed_data/processed_data_dash.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def pick_random_items(
    data: Union[Sequence[Item], Mapping[Any, Item]],
    n: int = 20,
    seed: int | None = None,
    allow_repeat: bool = False,
    filter_fn: Callable[[Item], bool] | None = None,
    keep_keys: bool = False
) -> List[MaybeKeyed]:
    rng = random.Random(seed)
    if isinstance(data, Mapping):
        items: List[MaybeKeyed] = list(data.items()) if keep_keys else list(data.values())
    elif isinstance(data, Sequence) and not isinstance(data, (str, bytes, bytearray)):
        items = list(data)
    else:
        raise TypeError("data phải là list hoặc dict")
    if filter_fn is not None:
        if isinstance(data, Mapping) and keep_keys:
            items = [(k, v) for (k, v) in items if filter_fn(v)]
        else:
            items = [x for x in items if filter_fn(x)]

    if not items:
        return []
    if allow_repeat:
        return [rng.choice(items) for _ in range(n)]
    else:
        k = min(n, len(items))
        return rng.sample(items, k)