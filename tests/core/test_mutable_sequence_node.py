import pytest
from metalib import MetadataMutableSequenceNode, MetadataMutableMappingNode


def test_parent_is_None():
    node = MetadataMutableSequenceNode(None, [])

    assert node._parent is None
    assert node._level == 0


def test_parent():
    parent = MetadataMutableSequenceNode(None, [])
    node = MetadataMutableSequenceNode(parent, [])

    assert node._parent is parent
    assert node._level == 1


def test_access_scalar_with_index():
    sequence = ['test', 2]
    node = MetadataMutableSequenceNode(None, sequence)

    # get access
    assert node[0] == 'test'
    assert node[1] == 2

    # set access should modify the underlying mapping
    node[0] = 'passed'
    node[1] = 4
    assert sequence[0] == 'passed'
    assert sequence[1] == 4


def test_access_collection_node_with_index():
    sequence = [dict(a_a='test', a_b=3), 1, ['a', 2, 3, 4]]
    node = MetadataMutableSequenceNode(None, sequence)

    # get access
    assert isinstance(node[0], MetadataMutableMappingNode)
    assert isinstance(node[2], MetadataMutableSequenceNode)
    assert node[0]['a_a'] == 'test'

    # set access
    node[0]['a_a'] = 'passed'
    assert sequence[0]['a_a'] == 'passed'

    node[2][1] = 10
    assert sequence[2][1] == 10


def test_replace_sequence_with_scalar():
    sequence = [[1, 2, 3, 4], 1]
    node = MetadataMutableSequenceNode(None, sequence)

    # replace
    node[0] = 1234
    assert node[0] == 1234
    assert sequence[0] == 1234


def test_replace_scalar_with_sequence():
    sequence = [1, 2, 3, 4]
    node = MetadataMutableSequenceNode(None, sequence)

    # replace
    node[2] = ['a', 'b', 'c']
    assert isinstance(node[2], MetadataMutableSequenceNode)
    assert node[2][0] == 'a'
    assert sequence[2][0] == 'a'


def test_replace_scalar_with_nested_sequence():
    sequence = [1, 2, 3, 4]
    node = MetadataMutableSequenceNode(None, sequence)

    # replace
    node[2] = ['a', 'b', [7, 8, 9], dict(a='nested value')]
    assert isinstance(node[2], MetadataMutableSequenceNode)
    assert isinstance(node[2][2], MetadataMutableSequenceNode)
    assert isinstance(node[2][3], MetadataMutableMappingNode)
    assert node[2][0] == 'a'
    assert sequence[2][0] == 'a'


def test_number_of_nodes():
    sequence = [1, dict(), 3, [4, 5, 6]]
    node = MetadataMutableSequenceNode(None, sequence)

    # replace
    assert len(node) == 4


def test_delete_node():
    sequence = [1, dict(), 3, [4, 5, 6]]
    node = MetadataMutableSequenceNode(None, sequence)

    # delete node
    del node[1]
    assert len(node) == 3
    assert node[0] == 1
    assert node[1] == 3
    assert isinstance(node[2], MetadataMutableSequenceNode)

    # check item has been deleted in original mapping
    assert len(sequence) == 3
    assert list(sequence) == [1, 3, [4, 5, 6]]


def test_insert_node():
    sequence = [1, 2, 3, [4, 5, 6]]
    node = MetadataMutableSequenceNode(None, sequence)

    # add node
    node.insert(1, 'new item')
    assert len(node) == 5
    assert node[0] == 1
    assert node[1] == 'new item'
    assert node[2] == 2

    # check item has been added to original mapping
    assert len(sequence) == 5
    assert sequence[0] == 1
    assert sequence[1] == 'new item'
    assert sequence[2] == 2


def test_access_scalar_with_dot_notation():
    mapping = dict(a='test', b=[1, 2, 3, 4])
    node = MetadataMutableMappingNode(None, mapping)

    # inheritance
    assert node.b.a == 'test'
