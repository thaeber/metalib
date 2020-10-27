from pathlib import Path
from toolz import pipe, curry

from .core import *
import yaml


@curry
def _add_metadata_filename(filename: Path, node: MetadataNode):
    node._filename = filename.name
    node._path = filename.parent
    return node


def _metadata_dict_node_representer(dumper: yaml.Dumper,
                                    data: MetadataMutableMappingNode):
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', data)


def _metadata_list_node_representer(dumper: yaml.Dumper,
                                    data: MetadataMutableSequenceNode):
    return dumper.represent_sequence(u'tag:yaml.org,2002:seq', data)


yaml.add_representer(MetadataMutableMappingNode,
                     _metadata_dict_node_representer)
yaml.add_representer(MetadataMutableSequenceNode,
                     _metadata_list_node_representer)


def from_yaml(filename: Union[str, Path]) -> MetadataNode:
    if not isinstance(filename, Path):
        filename = Path(filename)

    return pipe(
        filename.read_text(),
        yaml.safe_load,
        from_obj,
        _add_metadata_filename(filename),
    )


def to_yaml(filename: Union[str, Path], metadata: MetadataNode):
    with open(filename, 'w') as file:
        yaml.dump(
            metadata,
            file,
            encoding='utf-8',
            indent=2,
            allow_unicode=True,
            default_flow_style=False,
        )


def _to_yaml(self: MetadataNode, filename: Union[str, Path]):
    to_yaml(filename, self)


# add to_yaml convenience method to class
MetadataNode.to_yaml = _to_yaml