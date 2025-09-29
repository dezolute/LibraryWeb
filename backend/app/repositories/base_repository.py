from abc import ABC, abstractmethod
from typing import List


class AbstractRepository(ABC):

    @abstractmethod
    async def create(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def create_multiple(self, data: List[dict]):
        raise NotImplementedError

    @abstractmethod
    async def update(self, data: dict, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def find(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def create_employee(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def create_admin(self, data: dict):
        raise NotImplementedError
