#%%
from ruamel.yaml import YAML
from pathlib import Path

# %%
yaml = YAML()
yaml.encoding = 'utf-8'
meta = yaml.load(Path('./tests/data/test.yaml'))
print(type(meta))
meta
# %%

yaml.dump(meta, Path('dump.yaml'))

# %%
