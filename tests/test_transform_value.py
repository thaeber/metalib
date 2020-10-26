from metalib.core import MetadataDictNode, MetadataListNode
import pytest
from metalib import MetadataNode


def test_map_dict():
    value = dict(a='b', c=2)
    node = MetadataNode(None)
    assert isinstance(node._transform_value(value), MetadataDictNode)


def test_map_list():
    value = [1, 2, 3, 4]
    node = MetadataNode(None)
    assert isinstance(node._transform_value(value), MetadataListNode)
