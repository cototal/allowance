from dataclasses import dataclass
from decimal import Decimal

from app.models import Entry, Task, User


@dataclass
class EntryIndexViewModel:
    entries: list[Entry]
    page: int
    pages: int
    total: int
    search_params: dict[str, str]
    users: list[User]
    selected_user: User | None
    balance: Decimal
    monthly_spending: Decimal
    task: Task | None
    sort: str
    direction: str
    sort_urls: dict[str, str]
    page_urls: dict[int, str]
    page_numbers: list[int]
    search_errors: list[str]


@dataclass
class TaskFormViewModel:
    task: Task | None
    title: str
    goal: str
    reward: str
    selected_days: list[str]
    days: list[str]
    errors: list[str]
