from pathlib import Path

import metalib
import pytest
import warnings


def test_dump_metadata(tmp_path: Path):

    # create metadata
    obj = dict(name='a',
               value=2.4,
               params=[
                   dict(p1='1', p2=2, p3=[1, 2, 3, 4]),
                   dict(p1='3', p2=4, p3=dict(subp1=1, subp2='x'))
               ])
    meta = metalib.from_obj(obj)

    # dump metadata
    filename = tmp_path / 'dump.yaml'
    meta.to_yaml(tmp_path / 'dump.yaml')
    meta.to_yaml('dump.yaml')

    # load metadata
