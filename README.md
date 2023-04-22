## Hello, config!

### So, what's the plan?

1. You are describing config as dataclass
2. I'm making sample file with needed fields
3. You're filling them in
4. ???????
5. App is good to go

__What's was not mentioned:__

    nested fields supported cherez zhopu (are not supported)
    cause it's too complicated for me, i'll try to do it again later

    you can try nested fields, but updating existing config will not work

    also there is some problem (idfk what) with dataclass fields
    defined as class variables (not annotations)

### About

Available on PyPI, so can be installed with `pip install helloconfig`

Supports Python, YAML, JSON and .env configuration files

Main feature (and why i made this library) is creating config file if it's not exists.
If config class was updated and existing config misses any field,
file will be updated with fields needed.

Data loaded with [dataclass-factory](https://github.com/reagento/dataclass-factory) library,
so also value validation should be supported, but this require additional meta programming,
which... i also will do later.\
(unfortunately, DF didn't support validators in
dataclasses by design, so it's not ready out of the box)

### Usage

On first run last line will raise `helloconfig.FieldsMissing` exception
and create file with zero (or default, if specified in class) values.

```python
from helloconfig import PythonConfig


class Config(PythonConfig):
    host: str
    port: int = 8080


config = Config.from_file('config.pyi')
```

### About formats

`PythonConfig`, `YamlConfig`, `DotEnvConfig`
preserve existing comments when updating fields.\
(new fields are appending to the end of file)

`JsonConfig` does not support comments, and even order of fields
may change.

### what is nested fields

```python
class Config(PythonConfig):
    a: str

    class some_field:
        nested_field: int
```

it will result in following python file

```python
a = ''

class some_field:
    nested_field = 0
```

and only PythonConfig tested such way,
other types don't know anything about nesting
