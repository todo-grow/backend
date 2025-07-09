from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.todo import Todo

class ITodoRepository(ABC):
    @abstractmethod
    def get_all_todos(self) -> List[Todo]:
        pass

    @abstractmethod
    def create_todo(self, todo: Todo) -> Todo:
        pass
    
    @abstractmethod
    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        pass
