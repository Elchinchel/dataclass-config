## Hello, config!

### So, what's the plan?

1. You are describing config as dataclass
2. I'm making sample file with needed fields
3. You're filling in specified file
4. ???????
5. App is good to go

__What's was not mentioned:__

    nested fields supported cherez zhopu (are not supported)
    cause it's too complicated for me, i'll try do it again later

    you can try nested fields, but updating existing config will not work

    also there is some problem (idfk what) with dataclass fields
    defined as class variables (not annotations)

### About

Available on PyPI, so can be installed with `pip install helloconfig`

Supports Python, YAML, JSON and .env configuration files

Main feature (and why i made this library) is creating config file if it's not exists.
If config class was updated and existing config misses any field,
file will be updated with fields needed.

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

`PythonConfig`, `YamlConfig`, `DotEnvConfig`
preserve existing comments when updating fields.\
(nested fields are not supported, as i said above)

`JsonConfig` does not support comments, and even order of fields
may change

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
