from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.todo import Todo

class TodoRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Todo]:
        pass

    @abstractmethod
    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        pass

    @abstractmethod
    def create(self, todo: Todo) -> Todo:
        pass

    @abstractmethod
    def update(self, todo: Todo) -> Todo:
        pass

    @abstractmethod
    def delete(self, todo_id: int) -> None:
        pass
