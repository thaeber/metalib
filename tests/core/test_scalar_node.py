import pytest
from metalib import MetadataScalarNode


def test_parent_is_None():
    node = MetadataScalarNode(None, None)

    assert node._parent is None
    assert node._level == 0


def test_parent():
    parent = MetadataScalarNode(None, None)
    node = MetadataScalarNode(parent, None)

    assert node._parent is parent
    assert node._level == 1


def test_getter():
    value = 'abc'

    def setter(x):
        value = x

    node = MetadataScalarNode(None, value)
    assert node._value == 'abc'
