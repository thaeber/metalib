from typing import Any, Dict, List, Callable, Iterator, Union, Iterable


class MetadataNode():
    def __init__(self, parent: "MetadataNode"):

        self.parent = parent
        if parent is not None:
            self.level = parent.level + 1
        else:
            self.level = 0
        # print(f'Level: {self.level}')

    def _transform_value(self, value: Any):
        if isinstance(value, (MetadataDictNode, MetadataListNode)):
            # the value is already a metadata node
            return value
        if isinstance(value, dict):
            # print(f'dict: {value}')
            return MetadataDictNode(self, value)
        elif isinstance(value, list):
            # print(f'list: {value}')
            return MetadataListNode(self, value)
        else:
            # print(value)
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
    def __init__(self, parent: MetadataNode, values: Dict):

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
    def __init__(self, parent: MetadataNode, values: Union[List, Iterable]):
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
