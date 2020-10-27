from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, List, Callable, Iterator, MutableMapping, MutableSequence, Union, Iterable, overload
import collections.abc
from toolz import curry


class MetadataNode(metaclass=ABCMeta):
    def __init__(self, parent: Union[None, "MetadataNode"]):

        self._parent = parent
        self._level = 0
        if parent is not None:
            self._level = parent._level + 1

    @staticmethod
    def _transform_value(parent: Union["MetadataNode", None],
                         value: Any) -> "MetadataNode":

        # wrap getter/setter in a metadata node instance
        if isinstance(value, MetadataNode):
            # the value is already a metadata node, just return it
            return value
        if isinstance(value, str):
            # specifically check for string to avoid
            # recursion because str is also a Sequence type
            return MetadataScalarNode(parent, value)
        if isinstance(value, collections.abc.MutableMapping):
            # the value is a key:value mapping
            return MetadataMutableMappingNode(parent, value)
        elif isinstance(value, collections.abc.MutableSequence):
            # the value is an indexable sequence
            return MetadataMutableSequenceNode(parent, value)
        else:
            # scalar type or unknown type
            return MetadataScalarNode(parent, value)

    def __getattr__(self, name: str) -> Any:
        if name in self.__dict__:
            # requests an attribute of the current node
            return self.__dict__[name]
        elif self._parent is not None:
            # call the parent to retrieve the parameter
            return self._parent.__getattr__(name)
        else:
            # could not find a parameter of the given name
            raise AttributeError(name)

    @abstractmethod
    def _iter_nodes_(self) -> Iterator["MetadataNode"]:
        pass

    def has_param(self, param_name: str) -> bool:
        raise NotImplementedError()
        try:
            _ = self.__getattr__(param_name)
            return True
        except AttributeError:
            return False

    def get_param(self, param_name: Union[str, List[str]]) -> Any:
        raise NotImplementedError()
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
        raise NotImplementedError()
        for child in self.get_child_nodes():
            # check children of child node
            yield from child.query(predicate)

            # check child node itself
            try:
                if predicate(child):
                    yield child
            except AttributeError:
                pass


class MetadataScalarNode(MetadataNode):
    def __init__(self, parent: Union[MetadataNode, None], value: Any):

        # call super class
        super().__init__(parent)

        # store getter/setter
        self._value = value

    def _iter_nodes_(self) -> Iterator["MetadataNode"]:
        yield from []

    def __repr__(self) -> str:
        return f'scalar: {self._value}'


class MetadataCollectionNode(MetadataNode):
    def __init__(self, parent: Union[MetadataNode, None]):
        super().__init__(parent)

    # @abstractmethod
    # def get_child_nodes(self) -> Iterator["MetadataNode"]:
    #     pass


class MetadataMutableMappingNode(MetadataCollectionNode,
                                 collections.abc.MutableMapping):
    def __init__(
        self,
        parent: Union[MetadataNode, None],
        mapping: MutableMapping,
    ):

        # call super class
        super().__init__(parent)

        # store a reference to the mapping instance
        self._ref = mapping

        # loop over values and build metadata node tree
        self._child_nodes = {
            key: MetadataNode._transform_value(self, value)
            for key, value in mapping.items()
        }

    def __getitem__(self, key: Any) -> Any:
        node = self._child_nodes[key]
        if isinstance(node, MetadataScalarNode):
            # directly return scalar value
            return node._value
        else:
            # return collection nodes
            return node

    def __setitem__(self, key: Any, value: Any) -> None:
        self._ref[key] = value
        self._child_nodes[key] = MetadataNode._transform_value(self, value)

    def __iter__(self) -> Iterator[Any]:
        return self._child_nodes.__iter__()

    def __len__(self) -> int:
        return len(self._child_nodes)

    def __delitem__(self, key: Any) -> None:
        del self._ref[key]
        del self._child_nodes[key]

    def __getattr__(self, name: str) -> Any:
        if name in self:
            # the attribute name is in the child dictionary
            return self[name]
        else:
            # call super class
            return super().__getattr__(name)

    def _iter_nodes_(self) -> Iterator["MetadataNode"]:
        # for value in self.values():
        #     if isinstance(value, MetadataNode):
        #         yield value
        raise NotImplementedError()


class MetadataMutableSequenceNode(MetadataNode,
                                  collections.abc.MutableSequence):
    def __init__(
        self,
        parent: Union[MetadataNode, None],
        sequence: MutableSequence,
    ):
        # call super class
        super().__init__(parent)

        # store a reference to the sequence instance
        self._ref = sequence

        # loop over values and build metadata node tree
        self._child_nodes = [
            MetadataNode._transform_value(self, value) for value in sequence
        ]

    def __getitem__(self, index: Union[int, slice]) -> Any:
        if isinstance(index, slice):
            raise NotImplementedError('Slicing ist not supported')
        elif isinstance(index, int):
            node = self._child_nodes[index]
            if isinstance(node, MetadataScalarNode):
                return node._value
            else:
                return node
        else:
            raise TypeError('"index" must be of type "int" or "slice".')

    def __setitem__(
        self,
        index: Union[int, slice],
        value: Union[Any, Iterable[Any]],
    ) -> None:
        if isinstance(index, slice):
            raise NotImplementedError('Slicing ist not supported')
        elif isinstance(index, int):
            self._ref[index] = value
            self._child_nodes[index] = MetadataNode._transform_value(
                self, value)
        else:
            raise TypeError('"index" must be of type "int" or "slice".')

    def __delitem__(self, index: Union[int, slice]) -> None:
        if isinstance(index, slice):
            raise NotImplementedError('Slicing ist not supported')
        elif isinstance(index, int):
            del self._ref[index]
            del self._child_nodes[index]
            print('Test')
        else:
            raise TypeError('"index" must be of type "int" or "slice".')

    def __iter__(self) -> Iterator[Any]:
        return self._child_nodes.__iter__()

    def __len__(self) -> int:
        return len(self._child_nodes)

    def insert(self, index: int, value: Any) -> None:
        self._ref.insert(index, value)
        self._child_nodes.insert(index,
                                 MetadataNode._transform_value(self, value))

    def _iter_nodes_(self) -> Iterator["MetadataNode"]:
        raise NotImplementedError()
        # for value in self:
        #     if isinstance(value, MetadataNode):
        #         yield value


def from_obj(obj: Union[MutableMapping, MutableSequence]) -> MetadataNode:
    """
    Encapsulates a dictionary, list or iterable in a metadata structure.

    Args:
        
    - `obj (dict, list, Iterable)`: The object that will be encapsulated.

    Raises:
    
    - `ValueError`: The parameter 'obj' is not of the correct type.

    Returns:
        
    `MetadataNode`: The metadata structure with information from the specified parameter `obj`.

    """
    if isinstance(obj, MutableMapping):
        return MetadataMutableMappingNode(None, obj)
    elif isinstance(obj, MutableSequence):
        return MetadataMutableSequenceNode(None, obj)
    else:
        raise ValueError('"obj" must be of type list or dict.')


def concat(
        metadata_or_list: Union[MetadataNode,
                                List[MetadataNode]]) -> MetadataNode:
    if isinstance(metadata_or_list, MetadataNode):
        return metadata_or_list
    else:
        return MetadataMutableSequenceNode(None, metadata_or_list)