"""PawPal+ logic layer.

Pets carry a list of note strings. Each note is expected to contain two
4-digit military-time tokens (start, end) and an optional priority word
(high/normal/low). Anything else is treated as the title. Missing tokens
fall back to defaults: priority=normal, start=0700, end=0800.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


DEFAULT_PRIORITY = "normal"
DEFAULT_START = "0700"
DEFAULT_END = "0800"

PRIORITY_WORDS = {"high", "normal", "low"}
PRIORITY_RANK = {"high": 0, "normal": 1, "low": 2}

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_WEEKDAY_LOOKUP = {d.lower(): d for d in WEEKDAYS}

_MIL_TIME_RE = re.compile(r"\b(?:[01]\d|2[0-3])[0-5]\d\b")
_DAYS_TOKEN_RE = re.compile(r"^days=([A-Za-z]{3}(?:,[A-Za-z]{3})*)$", re.IGNORECASE)


@dataclass
class Task:
    title: str
    priority: str
    start: str
    end: str
    duration_minutes: int
    pet_name: str
    raw: str
    days: list[str] = field(default_factory=lambda: list(WEEKDAYS))


def _minutes(hhmm: str) -> int:
    """Convert an 'HHMM' military-time string to minutes since midnight."""
    return int(hhmm[:2]) * 60 + int(hhmm[2:])


def parse_note(text: str, pet_name: str = "") -> Task:
    """Parse a note string into a Task, applying defaults for missing tokens."""
    raw = text
    times = _MIL_TIME_RE.findall(text)
    start = times[0] if len(times) >= 1 else DEFAULT_START
    end = times[1] if len(times) >= 2 else DEFAULT_END

    tokens = text.split()
    priority = DEFAULT_PRIORITY
    days: list[str] = list(WEEKDAYS)
    days_seen = False
    kept: list[str] = []
    times_consumed = 0
    for tok in tokens:
        low = tok.lower()
        if low in PRIORITY_WORDS:
            priority = low
            continue
        if low == "priority":
            continue
        if _MIL_TIME_RE.fullmatch(tok) and times_consumed < 2:
            times_consumed += 1
            continue
        m = _DAYS_TOKEN_RE.match(tok)
        if m and not days_seen:
            parsed_days: list[str] = []
            for part in m.group(1).split(","):
                canonical = _WEEKDAY_LOOKUP.get(part.lower())
                if canonical and canonical not in parsed_days:
                    parsed_days.append(canonical)
            if parsed_days:
                days = parsed_days
                days_seen = True
                continue
        kept.append(tok)

    title = " ".join(kept).strip()
    duration_minutes = _minutes(end) - _minutes(start)

    return Task(
        title=title,
        priority=priority,
        start=start,
        end=end,
        duration_minutes=duration_minutes,
        pet_name=pet_name,
        raw=raw,
        days=days,
    )


class Pet:
    def __init__(
        self,
        name: str,
        species: str,
        breed: str | None = None,
        age_years: int | None = None,
        notes: list[str] | None = None,
    ) -> None:
        self.name = name
        self.species = species
        self.breed = breed
        self.age_years = age_years
        self.notes: list[str] = list(notes) if notes else []

    def add_note(self, text: str) -> None:
        """Append a note to this pet; reject empty or whitespace-only text."""
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("note cannot be empty")
        self.notes.append(cleaned)

    def edit_note(self, index: int, new_text: str) -> None:
        """Replace the note at ``index`` with new text."""
        cleaned = new_text.strip()
        if not cleaned:
            raise ValueError("note cannot be empty")
        self.notes[index] = cleaned

    def remove_note(self, index: int) -> None:
        """Delete the note at ``index``."""
        del self.notes[index]

    def update_info(self, **fields: Any) -> None:
        """Update allowed Pet fields (name, species, breed, age_years) from keyword arguments."""
        allowed = {"name", "species", "breed", "age_years"}
        for key, value in fields.items():
            if key in allowed:
                setattr(self, key, value)


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
        """Add a Pet to this owner's list."""
        self.pets.append(pet)

    def update_info(self, **fields: Any) -> None:
        """Update allowed Owner fields (name, daily_minutes_available, preferences) from keyword arguments."""
        allowed = {"name", "daily_minutes_available", "preferences"}
        for key, value in fields.items():
            if key in allowed:
                setattr(self, key, value)


class Plan:
    def __init__(
        self,
        scheduled: list[dict[str, Any]],
        skipped: list[dict[str, Any]],
        total_minutes_used: int,
        day_budget: int,
    ) -> None:
        self.scheduled = scheduled
        self.skipped = skipped
        self.total_minutes_used = total_minutes_used
        self.day_budget = day_budget

    def render(self) -> list[dict[str, Any]]:
        """Return the scheduled entries as UI-ready row dicts."""
        return self.scheduled

    def explain(self) -> str:
        """Return a human-readable summary of scheduled and skipped items."""
        lines = [
            f"Used {self.total_minutes_used} of {self.day_budget} min.",
        ]
        for item in self.scheduled:
            lines.append(
                f"  {item['start']}-{item['end']} {item['pet_name']}: "
                f"{item['title']} — {item['reason']}"
            )
        if self.skipped:
            lines.append("Skipped:")
            for item in self.skipped:
                lines.append(f"  {item['title']} — {item['reason']}")
        return "\n".join(lines)


class WeeklyPlan:
    def __init__(self, days: dict[str, Plan]) -> None:
        self.days = days

    def total_scheduled(self) -> int:
        return sum(len(p.scheduled) for p in self.days.values())

    def explain(self) -> str:
        parts: list[str] = []
        for day, plan in self.days.items():
            parts.append(f"=== {day} ===")
            parts.append(plan.explain())
        return "\n".join(parts)


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def tasks(self) -> list[Task]:
        """Parse every note across the owner's pets into Task objects."""
        result: list[Task] = []
        for pet in self.owner.pets:
            for note_text in pet.notes:
                result.append(parse_note(note_text, pet_name=pet.name))
        return result

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by priority (high→low), then by start time."""
        return sorted(
            tasks,
            key=lambda t: (PRIORITY_RANK.get(t.priority, 1), t.start),
        )

    def _build_plan_from_tasks(self, tasks: list[Task]) -> Plan:
        """Greedily fill the day budget with the given tasks, sorted by priority then start."""
        tasks = self.sort_tasks(tasks)
        budget = self.owner.daily_minutes_available
        used = 0
        scheduled: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []

        for task in tasks:
            entry = {
                "pet_name": task.pet_name,
                "title": task.title,
                "priority": task.priority,
                "start": task.start,
                "end": task.end,
                "duration_minutes": task.duration_minutes,
                "raw_note": task.raw,
                "reason": "",
            }
            if task.duration_minutes <= 0:
                entry["reason"] = "invalid time range"
                skipped.append(entry)
                continue
            if used + task.duration_minutes <= budget:
                entry["reason"] = (
                    f"priority={task.priority}, fits {task.duration_minutes} min"
                )
                scheduled.append(entry)
                used += task.duration_minutes
            else:
                entry["reason"] = "budget exceeded"
                skipped.append(entry)

        return Plan(
            scheduled=scheduled,
            skipped=skipped,
            total_minutes_used=used,
            day_budget=budget,
        )

    def build_plan(self) -> Plan:
        """Build a single-day plan from all parsed tasks (ignores per-task days metadata)."""
        return self._build_plan_from_tasks(self.tasks())

    def build_weekly_plan(self) -> WeeklyPlan:
        """Build a per-weekday plan, filtering tasks by their days metadata."""
        all_tasks = self.tasks()
        plans: dict[str, Plan] = {}
        for day in WEEKDAYS:
            day_tasks = [t for t in all_tasks if day in t.days]
            plans[day] = self._build_plan_from_tasks(day_tasks)
        return WeeklyPlan(days=plans)
