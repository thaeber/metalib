__version__ = '0.1.0'

#%%
from pathlib import Path
from typing import List, Union, Iterable

import yaml
from toolz import pipe, curry
from pandas import DataFrame
from ._nodes import MetadataNode, MetadataListNode, MetadataDictNode


#%%
def from_obj(obj: Union[dict, list, Iterable]) -> MetadataNode:
    """
    Encapsulates a dictionary, list or iterable in a metadata structure.

    Args:
        
    - `obj (dict, list, Iterable)`: The object that will be encapsulated.

    Raises:
    
    - `ValueError`: The parameter 'obj' is not of the correct type.

    Returns:
        
    `MetadataNode`: The metadata structure with information from the specified parameter `obj`.

    """
    if isinstance(obj, dict):
        return MetadataDictNode(None, obj)
    elif isinstance(obj, (list, Iterable)):
        return MetadataListNode(None, obj)
    else:
        raise ValueError('"obj" must be of type list or dict.')


@curry
def _add_metadata_filename(filename: Path, node: MetadataNode):
    node._filename = filename.name
    node._path = filename.parent
    return node


def from_yaml(filename: Union[str, Path]) -> MetadataNode:
    if not isinstance(filename, Path):
        filename = Path(filename)

    return pipe(
        filename.read_text(),
        yaml.safe_load,
        from_obj,
        _add_metadata_filename(filename),
    )


def concat(
        metadata_or_list: Union[MetadataNode,
                                List[MetadataNode]]) -> MetadataNode:
    if isinstance(metadata_or_list, MetadataNode):
        return metadata_or_list
    else:
        return MetadataListNode(None, metadata_or_list)


def to_dataframe(datasets: List[MetadataNode],
                 include_keys: Union[str, Iterable[str]] = None,
                 exclude_keys: Union[str, Iterable[str]] = None) -> DataFrame:
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

    data = [ds.get(keys) for ds in datasets]
    df = DataFrame(data, columns=keys)
    return df
