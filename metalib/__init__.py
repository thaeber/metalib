__version__ = '0.2.1-dev4'

from typing import List, Union, Iterable

from pandas import DataFrame
from .core import *
from ._yaml import from_yaml, to_yaml


def to_dataframe(datasets: List[MetadataNode],
                 include_keys: Union[str, Iterable[str]] = None,
                 exclude_keys: Union[str, Iterable[str]] = None) -> DataFrame:
    raise NotImplementedError()
    # get common parameter keys
    keys = set()
    for ds in datasets:
        if isinstance(ds, dict):
            keys.update(ds.keys())

    # include/exclude keys
    if include_keys is not None:
        if isinstance(include_keys, str):
            include_keys = [include_keys]
        keys.update(include_keys)
    if exclude_keys is not None:
        if isinstance(exclude_keys, str):
            exclude_keys = [exclude_keys]
        keys.difference_update(exclude_keys)
    keys = list(keys)

    data = [ds.get_param(keys) for ds in datasets]
    df = DataFrame(data, columns=keys)
    return df
