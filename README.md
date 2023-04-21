## dataclass_config

Describe config files as dataclasses

Supports Python, YAML, JSON and .env configuration files

Main feature (and why i made this library) is creating config file if it's not exists.
If config class was updated and existing config misses any field,
file will be updated with fields needed.

### Usage

On first run last line will raise `dataclass_config.FieldsMissing` exception
and create file with zero (or default, if specified in class) values.

```python
from dataclass_config import PythonConfig


class Config(PythonConfig):
    host: str
    port: int = 8080


config = Config.from_file('config.pyi')
```

