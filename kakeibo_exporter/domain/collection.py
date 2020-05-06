from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Collection(Generic[T]):
    values: [T]

    def __iter__(self):
        return iter(self.values)

    def __add__(self, other):
        return self.__class__(self.values + other.values)

    def __len__(self):
        return len(self.values)
