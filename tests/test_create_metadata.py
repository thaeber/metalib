from pathlib import Path
from datetime import date

import metalib


def test_from_dict_obj():
    obj = dict(
        name='a',
        value=2.4,
        params=dict(p1='1', p2=2),
    )
    meta = metalib.from_obj(obj)
    assert meta.name == 'a'
    assert meta.value == 2.4
    assert meta.params.p1 == '1'
    assert meta.params.p2 == 2


def test_from_yaml():
    filename = Path(__file__).parent / 'data/test.yaml'
    meta = metalib.from_yaml(filename)

    # check selected fields
    assert meta.date == date(2020, 8, 21)
    assert meta.system == 'PIV1'
    assert meta.stage_position.x == 4850
    assert len(meta.datasets) == 4
    assert meta.datasets[0].Re == 5000

    # check inheritance of parameters
    assert meta.datasets[0].piv_region == '16x16'


def test_from_yaml_includes_filepath():
    filename = Path(__file__).parent / 'data/test.yaml'
    meta = metalib.from_yaml(filename)

    assert isinstance(meta._filename, str)
    assert meta._filename == filename.name

    assert isinstance(meta._path, Path)
    assert meta._path == filename.parent
