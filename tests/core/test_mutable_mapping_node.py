import pytest
from metalib import MetadataMutableMappingNode, MetadataMutableSequenceNode


def test_parent_is_None():
    node = MetadataMutableMappingNode(None, {})

    assert node._parent is None
    assert node._level == 0


def test_parent():
    parent = MetadataMutableMappingNode(None, {})
    node = MetadataMutableMappingNode(parent, {})

    assert node._parent is parent
    assert node._level == 1


def test_access_scalar_with_key():
    mapping = dict(a='test', b=2)
    node = MetadataMutableMappingNode(None, mapping)

    # get access
    assert node['a'] == 'test'
    assert node['b'] == 2

    # set access should modify the underlying mapping
    node['a'] = 'passed'
    node['b'] = 4
    assert mapping['a'] == 'passed'
    assert mapping['b'] == 4


def test_access_mapping_with_key():
    mapping = dict(a=dict(a_a='test', a_b=3), b=1)
    node = MetadataMutableMappingNode(None, mapping)

    # get access
    assert isinstance(node['a'], MetadataMutableMappingNode)
    assert node['a']['a_a'] == 'test'

    # set access
    node['a']['a_a'] = 'passed'
    assert mapping['a']['a_a'] == 'passed'


def test_replace_mapping_with_scalar():
    mapping = dict(a=dict(a_a='test', a_b=3), b=1)
    node = MetadataMutableMappingNode(None, mapping)

    # replace
    node['a'] = 1234
    assert node['a'] == 1234
    assert mapping['a'] == 1234


def test_replace_scalar_with_mapping():
    mapping = dict(a=dict(a_a='test', a_b=3), b=1)
    node = MetadataMutableMappingNode(None, mapping)

    # replace
    node['b'] = dict(b_a=1234)
    assert node['b']['b_a'] == 1234
    assert mapping['b']['b_a'] == 1234
    assert isinstance(node['b'], MetadataMutableMappingNode)


def test_replace_scalar_with_nested_mapping():
    mapping = dict(a=dict(aa='test', ab=3), b=1)
    node = MetadataMutableMappingNode(None, mapping)

    # replace
    node['b'] = dict(ba=1234, bb=dict(bba='nested value'), bc=[1, 2, 3])
    assert mapping['b']['bb']['bba'] == 'nested value'
    assert node['b']['bb']['bba'] == 'nested value'
    assert isinstance(node['b'], MetadataMutableMappingNode)
    assert isinstance(node['b']['bb'], MetadataMutableMappingNode)
    assert isinstance(node['b']['bc'], MetadataMutableSequenceNode)


def test_number_of_nodes():
    mapping = dict(a=dict(a_a='test', a_b=3), b=1)
    node = MetadataMutableMappingNode(None, mapping)

    # replace
    assert len(node) == 2


def test_delete_node():
    mapping = dict(a=dict(), b=1, c='test', d=True)
    node = MetadataMutableMappingNode(None, mapping)

    # delete node
    del node['b']
    assert len(node) == 3
    assert isinstance(node['a'], MetadataMutableMappingNode)
    assert node['c'] == 'test'
    assert node['d'] is True
    assert set(node.keys()) == set(['a', 'c', 'd'])

    # check item has been deleted in original mapping
    assert len(mapping) == 3
    assert set(mapping.keys()) == set(['a', 'c', 'd'])


def test_add_node():
    mapping = dict(a=dict(), b=1, c='test')
    node = MetadataMutableMappingNode(None, mapping)

    # add node
    node['d'] = 'new item'
    assert len(node) == 4
    assert set(node.keys()) == set(['a', 'b', 'c', 'd'])
    assert node['d'] == 'new item'

    # check item has been added to original mapping
    assert len(mapping) == 4
    assert set(mapping.keys()) == set(['a', 'b', 'c', 'd'])
    assert mapping['d'] == 'new item'


def test_access_scalar_with_dot_notation():
    mapping = dict(a='test', b=2, c=dict(d=1234))
    node = MetadataMutableMappingNode(None, mapping)

    # get access
    assert node.a == 'test'
    assert node.b == 2
    assert node.c.d == 1234

    # inheritance
    assert node.c.a == 'test'


def test_check_if_key_is_in_node():
    mapping = dict(a='test', b=2, c=dict(d=1234))
    node = MetadataMutableMappingNode(None, mapping)

    assert 'b' in mapping


def test_key_iteration():
    mapping = dict(a='a', b='b', c=[7, 8, 9], d=dict(a='nested value'), e=12.0)
    node = MetadataMutableMappingNode(None, mapping)

    # replace
    lst = [node[key] for key in node]
    assert isinstance(lst[0], str)
    assert isinstance(lst[1], str)
    assert isinstance(lst[2], MetadataMutableSequenceNode)
    assert isinstance(lst[3], MetadataMutableMappingNode)
    assert isinstance(lst[4], float)

    assert lst[0] == 'a'
    assert lst[1] == 'b'
    assert lst[4] == 12.0


def test_value_iteration():
    mapping = dict(a='a', b='b', c=[7, 8, 9], d=dict(a='nested value'), e=12.0)
    node = MetadataMutableMappingNode(None, mapping)

    # replace
    lst = [value for value in node.values()]
    assert isinstance(lst[0], str)
    assert isinstance(lst[1], str)
    assert isinstance(lst[2], MetadataMutableSequenceNode)
    assert isinstance(lst[3], MetadataMutableMappingNode)
    assert isinstance(lst[4], float)

    assert lst[0] == 'a'
    assert lst[1] == 'b'
    assert lst[4] == 12.0