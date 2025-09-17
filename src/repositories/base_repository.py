from abc import ABC, abstractmethod


class BaseRepository(ABC):

    @abstractmethod
    async def create(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def update(self, **kwargs):
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
