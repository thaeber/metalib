from typing import Mapping, Sequence
from metalib.core import MetadataMutableMappingNode, MetadataScalarNode
from pathlib import Path

import metalib
from metalib import MetadataMutableMappingNode
from metalib._yaml import _get_git_commit_hash
import pytest
import warnings


def test_dumped_history(tmp_path: Path):
    # create and dump metadata
    meta = metalib.from_obj(dict(name='Test'))
    meta.to_yaml(tmp_path / 'dump.yaml')

    # load metadata and check history
    dumped = metalib.from_yaml(tmp_path / 'dump.yaml')
    assert dumped['$history'][-1]['$script'] == 'test_dump_metadata.py'
    assert dumped['$history'][-1]['$git-commit'] == _get_git_commit_hash()


def test_dump_metadata(tmp_path: Path):

    # create metadata
    obj: dict = dict(name='a',
                     value=2.4,
                     params=[
                         dict(p1='1', p2=2, p3=[1, 2, 3, 4]),
                         dict(p1='3', p2=4, p3=dict(sub_p1=1, sub_p2='x'))
                     ])
    meta = metalib.from_obj(obj)

    # dump metadata
    filename = tmp_path / 'dump.yaml'
    meta.to_yaml(filename)

    # the original dataset should not contain a history node
    assert '$history' not in obj

    # load metadata
    dumped = metalib.from_yaml(filename)
    del dumped['$history']  # $history is only in dumped version

    def compare_object_trees(left, right, level='root'):
        if isinstance(left, Mapping):
            keys = set(left) | set(right)
            for key in keys:
                assert key in left, f'key "{key}" not in left side @ {level}'
                assert key in right, f'key "{key}" not in right side @ {level}'
                compare_object_trees(left[key], right[key],
                                     level + f'["{key}"]')
        elif isinstance(left, Sequence) and not isinstance(left, str):
            assert len(left) == len(right), f'different lengths @ {level}'
            for k, (x, y) in enumerate(zip(left, right)):
                compare_object_trees(x, y, level + f'[{k}]')
        else:
            assert repr(left) == repr(
                right), f'{str(left)} != {str(right)} @ {level}'

    compare_object_trees(dumped, obj)
