from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
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

    @abstractmethod
    def get_todos_by_date(self, target_date: date) -> List[Todo]:
        pass

    @abstractmethod
    def get_all_todos_by_user(self, user_id: int) -> List[Todo]:
        pass

    @abstractmethod
    def get_todos_by_date_and_user(self, target_date: date, user_id: int) -> List[Todo]:
        pass
