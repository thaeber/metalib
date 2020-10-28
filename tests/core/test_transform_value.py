from metalib.core import MetadataMutableMappingNode, MetadataMutableSequenceNode, MetadataScalarNode
import pytest
from metalib import MetadataNode


def test_map_string():
    value = 'test'
    node = MetadataNode._transform_value(None, value)
    assert isinstance(node, MetadataScalarNode)


def test_map_dict():
    value = dict(a='b', c=2)
    node = MetadataNode._transform_value(None, value)
    assert isinstance(node, MetadataMutableMappingNode)


def test_map_list():
    value = ['a', 2, 3, 4]
    node = MetadataNode._transform_value(None, value)
    assert isinstance(node, MetadataMutableSequenceNode)
