from metalib.core import MetadataNode

import metalib


def create_metadata() -> MetadataNode:
    obj = dict(name='a',
               value=2.4,
               params=[
                   dict(p1='1',
                        p2=2,
                        p3=[11, 22, 33],
                        p4=dict(x=10, y=20, z=100)),
                   dict(p1='3',
                        p2=4,
                        p3=[11, 22, 33],
                        p4=dict(x=20, y=20, z=200)),
                   dict(p1='3',
                        p2=4,
                        p3=[11, 22, 33],
                        p4=dict(x=20, y=20, z=300)),
                   dict(p1='3', p2=4, p3=[11, 22, 33], p4=dict(x=30, z=400)),
               ])
    return metalib.from_obj(obj)


def test_access_by_key():
    meta = create_metadata()

    # check access
    assert meta["name"] == 'a'
    assert meta["params"][1]['p2'] == 4


def test_access_by_property():
    meta = create_metadata()

    # check access
    assert meta.name == 'a'
    assert meta.params[1].p2 == 4


def test_inheritance_of_properties():
    meta = create_metadata()

    # check access
    assert meta.params[1].name == 'a'
    assert meta.params[0].p4.name == 'a'


def test_get_param():
    meta = create_metadata()

    assert meta.get_param('name') == 'a'
    assert meta.params[1].get_param('p1') == '3'
    assert meta.params[1].p4.get_param('name') == 'a'


def test_get_multiple_params():
    meta = create_metadata()

    values = meta.params[1].p4.get_param(['x', 'p2', 'value'])
    assert values == [20, 4, 2.4]

    values = meta.params[0].p4.get_param(['x', 'p2', 'value'])
    assert values == [10, 2, 2.4]


def test_has_param():
    meta = create_metadata()

    assert meta.has_param('name')
    assert meta.params[1].has_param('p1')
    assert meta.params[1].p4.has_param('name')
    assert not meta.has_param('x')


def test_query():
    meta = create_metadata()

    result = meta.query(lambda node: ('y' in node) and (node.x == 20))
    result = list(result)

    assert len(result) == 2
    assert result[0].z == 200
    assert result[0].name == 'a'
    assert result[1].z == 300
    assert result[1].name == 'a'