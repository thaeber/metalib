from pathlib import Path
from typing import Any, Dict, List, Callable, Iterator, Mapping, Sequence, Union, Iterable
import collections.abc

import yaml


class MetadataNode():
    def __init__(self, parent: Union[None, "MetadataNode"]):

        self.parent = parent
        if parent is not None:
            self.level = parent.level + 1
        else:
            self.level = 0

    def _transform_value(self, value: Any):
        if isinstance(value, MetadataNode):
            # the value is already a metadata node
            return value
        if isinstance(value, str):
            # plain string, just return to avoid recursion
            # because str is also a Sequence type
            return value
        if isinstance(value, collections.abc.Mapping):
            # the value is a key:value mapping
            return MetadataDictNode(self, value)
        elif isinstance(value, collections.abc.Sequence):
            # the value is an indexable sequence
            return MetadataListNode(self, value)
        else:
            # scalar type or unknown type
            return value

    def get_child_nodes(self) -> Iterator["MetadataNode"]:
        yield from []

    def has(self, param_name: str) -> bool:
        try:
            _ = self.__getattr__(param_name)
            return True
        except AttributeError:
            return False

    def get(self, param_name: Union[str, List[str]]) -> Any:
        if isinstance(param_name, str):
            return self.__getattr__(param_name)
        elif isinstance(param_name, list):
            return [self.__getattr__(s) for s in param_name]
        else:
            raise ValueError("param_name must be a string or list of strings.")

    def query(
        self,
        predicate: Callable[["MetadataNode"], bool],
    ) -> Iterator[Any]:

        for child in self.get_child_nodes():
            # check children of child node
            yield from child.query(predicate)

            # check child node itself
            try:
                if predicate(child):
                    yield child
            except AttributeError:
                pass


class MetadataDictNode(MetadataNode, dict):
    def __init__(self, parent: MetadataNode, values: Mapping):

        MetadataNode.__init__(self, parent)

        # loop over values and replace dict and list objects
        transformed = {
            key: self._transform_value(value)
            for key, value in values.items()
        }

        dict.__init__(self, transformed)

    def __getattr__(self, name: str) -> Any:

        if name in self:
            # the name is in the current dictionary
            return self[name]
        elif name in self.__dict__:
            return self.__dict__[name]
        elif self.parent is not None:
            # call the parent to retrieve the parameter
            return self.parent.__getattr__(name)
        else:
            # could not find a parameter of the given name
            raise AttributeError(name)

    def get_child_nodes(self) -> Iterator["MetadataNode"]:
        for value in self.values():
            if isinstance(value, MetadataNode):
                yield value


class MetadataListNode(MetadataNode, list):
    def __init__(self, parent: MetadataNode, values: Sequence):
        MetadataNode.__init__(self, parent)

        # loop over values and replace dict and list objects
        transformed = [self._transform_value(value) for value in values]
        list.__init__(self, transformed)

    def __getattr__(self, name: str) -> Any:
        if name in self.__dict__:
            return self.__dict__[name]
        if self.parent is not None:
            # call the parent to retrieve the parameter
            return self.parent.__getattr__(name)
        else:
            # could not find a parameter of the given name
            raise AttributeError(name)

    def get_child_nodes(self) -> Iterator["MetadataNode"]:
        for value in self:
            if isinstance(value, MetadataNode):
                yield value


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


def concat(
        metadata_or_list: Union[MetadataNode,
                                List[MetadataNode]]) -> MetadataNode:
    if isinstance(metadata_or_list, MetadataNode):
        return metadata_or_list
    else:
        return MetadataListNode(None, metadata_or_list)