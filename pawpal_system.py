from __future__ import annotations

from typing import Any


class Pet:
    def __init__(
        self,
        name: str,
        species: str,
        breed: str | None = None,
        age_years: int | None = None,
        notes: str | None = None,
    ) -> None:
        self.name = name
        self.species = species
        self.breed = breed
        self.age_years = age_years
        self.notes = notes

    def update_info(self, **fields: Any) -> None:
        raise NotImplementedError


class Owner:
    def __init__(
        self,
        name: str,
        daily_minutes_available: int,
        preferences: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.pets: list[Pet] = []
        self.daily_minutes_available = daily_minutes_available
        self.preferences: dict[str, Any] = preferences or {}

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def update_info(self, **fields: Any) -> None:
        raise NotImplementedError


class Task:
    def __init__(
        self,
        id: str,
        pet: Pet,
        title: str,
        duration_minutes: int,
        priority: str,
        category: str | None = None,
        notes: str | None = None,
    ) -> None:
        self.id = id
        self.pet = pet
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.notes = notes

    def update(self, **fields: Any) -> None:
        raise NotImplementedError


class Plan:
    def __init__(
        self,
        scheduled: list[tuple[Task, str]],
        skipped: list[tuple[Task, str]],
        total_minutes_used: int,
        day_budget: int,
    ) -> None:
        self.scheduled = scheduled
        self.skipped = skipped
        self.total_minutes_used = total_minutes_used
        self.day_budget = day_budget

    def render(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def explain(self) -> str:
        raise NotImplementedError


class Scheduler:
    def __init__(self, owner: Owner, tasks: list[Task]) -> None:
        self.owner = owner
        self.tasks = tasks

    def sort_tasks(self) -> list[Task]:
        raise NotImplementedError

    def build_plan(self) -> Plan:
        raise NotImplementedError

    def explain_choice(self, task: Task) -> str:
        raise NotImplementedError
