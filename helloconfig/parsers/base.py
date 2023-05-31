from abc import ABC, abstractmethod
from typing import Any


class AbstractParser(ABC):  # pragma: no cover
    @abstractmethod
    def parse_string(self, data: str) -> 'dict[str, Any]':
        raise NotImplementedError

    @abstractmethod
    def update_config(self, config: str, fields: 'dict[str, Any]') -> str:
        raise NotImplementedError
