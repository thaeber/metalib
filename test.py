# #%%
# from ruamel.yaml import YAML
# from pathlib import Path

# # %%
# yaml = YAML()
# yaml.encoding = 'utf-8'
# meta = yaml.load(Path('./tests/data/test.yaml'))
# print(type(meta))
# meta
# # %%

# yaml.dump(meta, Path('dump.yaml'))

# %%
from metalib import MetadataMutableSequenceNode
# %%
sequence = [1, dict(), 3, [4, 5, 6]]
node = MetadataMutableSequenceNode(None, sequence)

list(node)

#%%
# delete node
del node[1]

#%%
len(node)
# %%
list(node)
# %%
for t in node:
    print(t)
# %%
