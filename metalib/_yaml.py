import inspect
import io
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ruamel.yaml import YAML
from toolz import curry, pipe

from .core import *


@curry
def _add_metadata_filename(filename: Path, node: MetadataNode):
    node._filename = filename.name
    node._path = filename.parent
    return node


@curry
def _add_yaml_instance(yaml: YAML, node: MetadataNode):
    node._yaml_serializer = yaml
    return node


def _create_yaml_serializer() -> YAML:
    yaml = YAML()
    yaml.encoding = 'utf-8'
    yaml.allow_unicode = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    return yaml


def from_yaml(filename: Union[str, Path]) -> MetadataNode:
    if not isinstance(filename, Path):
        filename = Path(filename)

    yaml = _create_yaml_serializer()

    return pipe(
        filename.read_text(),
        yaml.load,
        from_obj,
        _add_metadata_filename(filename),
        _add_yaml_instance(yaml),
    )


def _get_caller_filepath() -> Path:
    # get the caller's stack frame and extract its file path
    # (we take the first stack frame outside the "_yaml.py" module
    # and outside of the installed packages in the "site-packages" folder)
    frame_info = next(frame for frame in inspect.stack()
                      if not frame.filename.endswith('_yaml.py')
                      and 'site-packages' not in frame.filename)
    filepath = frame_info.filename
    del frame_info  # drop the reference to the stack frame to avoid reference cycles

    # make the path absolute (optional)
    return Path(filepath).resolve()


def _get_git_commit_hash() -> Union[str, None]:
    try:
        label = subprocess.check_output(
            ["git", "describe", "--always", "--dirty"], text=True).strip()
        return str(label)
    except:
        return None


def _append_history(node: MetadataNode):
    if not isinstance(node, MetadataMutableMappingNode):
        return node

    if '$history' not in node:
        node['$history'] = []

    entry = {
        '$date': datetime.now(),
        '$script': _get_caller_filepath().name,
        '$git-commit': _get_git_commit_hash()
    }
    node['$history'].append(entry)

    return node


def _memory_roundtrip(yaml: YAML, node: MetadataNode):
    stream = io.StringIO()

    # dump yaml to memory
    yaml.dump(node._ref, stream)

    # reload yaml from memory
    stream.seek(0)
    return pipe(
        yaml.load(stream),
        from_obj,
    )


def to_yaml(filename: Union[str, Path], metadata: MetadataNode):

    filename = Path(filename)

    # obtain YAML serializer instance
    try:
        yaml = metadata._yaml_serializer
    except Exception as e:
        print(e)
        yaml = None
    if (yaml is None) or not isinstance(yaml, YAML):
        print('create new yaml serializer')
        yaml = _create_yaml_serializer()
    else:
        print('resusing yaml serializer')

    pipe(
        metadata,
        # clone metadata in memory
        curry(_memory_roundtrip, yaml),
        # add history only to clone to avoid modifying the original metadata
        _append_history,
        # dump metadata to file
        lambda meta: yaml.dump(meta._ref, filename),
    )


def _to_yaml(self: MetadataNode, filename: Union[str, Path]):
    to_yaml(filename, self)


# add to_yaml convenience method to class
MetadataNode.to_yaml = _to_yaml
