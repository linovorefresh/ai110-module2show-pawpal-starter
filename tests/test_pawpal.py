"""Tests for PawPal+ parser and scheduler."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import (
    DEFAULT_END,
    DEFAULT_PRIORITY,
    DEFAULT_START,
    Owner,
    Pet,
    Scheduler,
    Task,
    parse_note,
)


# ---------- parse_note ----------

def test_parse_note_all_fields_present():
    t = parse_note("fill food water high 0700 0730", pet_name="Mochi")
    assert t.title == "fill food water"
    assert t.priority == "high"
    assert t.start == "0700"
    assert t.end == "0730"
    assert t.duration_minutes == 30
    assert t.pet_name == "Mochi"


def test_parse_note_defaults_when_all_missing():
    t = parse_note("nap")
    assert t.title == "nap"
    assert t.priority == DEFAULT_PRIORITY
    assert t.start == DEFAULT_START
    assert t.end == DEFAULT_END
    assert t.duration_minutes == 60


def test_parse_note_priority_is_case_insensitive():
    assert parse_note("walk HIGH 0700 0800").priority == "high"
    assert parse_note("walk Low 0700 0800").priority == "low"


def test_parse_note_strips_priority_decorator_word():
    t = parse_note("fill food priority high 0700 0730")
    assert t.title == "fill food"
    assert t.priority == "high"


def test_parse_note_only_first_two_times_are_consumed():
    t = parse_note("walk 0700 0800 1200")
    assert t.start == "0700"
    assert t.end == "0800"
    assert "1200" in t.title


def test_parse_note_invalid_range_still_parses():
    t = parse_note("bad 0800 0700")
    assert t.duration_minutes == -60


# ---------- Scheduler.sort_tasks ----------

def test_sort_tasks_orders_by_priority_then_start():
    owner = Owner("O", daily_minutes_available=500)
    pet = Pet("P", "dog")
    owner.add_pet(pet)
    pet.add_note("late low 1800 1830")
    pet.add_note("early low 0600 0630")
    pet.add_note("urgent high 1200 1230")

    sched = Scheduler(owner)
    ordered = sched.sort_tasks(sched.tasks())
    assert [t.title for t in ordered] == ["urgent", "early", "late"]


def test_sort_tasks_returns_chronological_order_within_same_priority():
    """Sorting Correctness: same-priority tasks come back in chronological order."""
    owner = Owner("O", daily_minutes_available=500)
    pet = Pet("P", "dog")
    owner.add_pet(pet)
    pet.add_note("noon normal 1200 1230")
    pet.add_note("dawn normal 0600 0630")
    pet.add_note("dusk normal 1800 1830")
    pet.add_note("morning normal 0900 0930")

    sched = Scheduler(owner)
    ordered = sched.sort_tasks(sched.tasks())
    assert [t.title for t in ordered] == ["dawn", "morning", "noon", "dusk"]
    assert [t.start for t in ordered] == ["0600", "0900", "1200", "1800"]


# ---------- Scheduler.build_plan ----------

def test_build_plan_respects_daily_budget():
    owner = Owner("O", daily_minutes_available=30)
    pet = Pet("P", "dog")
    owner.add_pet(pet)
    pet.add_note("short high 0700 0715")   # 15 min, fits
    pet.add_note("long normal 0800 0900")  # 60 min, exceeds

    plan = Scheduler(owner).build_plan()
    assert [s["title"] for s in plan.scheduled] == ["short"]
    assert plan.skipped[0]["title"] == "long"
    assert plan.skipped[0]["reason"] == "budget exceeded"
    assert plan.total_minutes_used == 15
    assert plan.day_budget == 30


def test_build_plan_skips_invalid_time_range():
    owner = Owner("O", daily_minutes_available=500)
    pet = Pet("P", "dog")
    owner.add_pet(pet)
    pet.add_note("bad 0800 0700")

    plan = Scheduler(owner).build_plan()
    assert plan.scheduled == []
    assert plan.skipped[0]["reason"] == "invalid time range"


def test_build_plan_empty_when_no_pets():
    owner = Owner("O", daily_minutes_available=60)
    plan = Scheduler(owner).build_plan()
    assert plan.scheduled == []
    assert plan.skipped == []
    assert plan.total_minutes_used == 0
    assert plan.day_budget == 60


def test_build_plan_covers_multiple_pets():
    owner = Owner("O", daily_minutes_available=120)
    a = Pet("A", "cat")
    b = Pet("B", "dog")
    owner.add_pet(a)
    owner.add_pet(b)
    a.add_note("feed high 0700 0715")
    b.add_note("walk high 0730 0815")

    plan = Scheduler(owner).build_plan()
    pet_names = {s["pet_name"] for s in plan.scheduled}
    assert pet_names == {"A", "B"}


# ---------- Pet note management ----------

def test_pet_add_note_increases_note_count():
    pet = Pet("Mochi", "cat")
    assert len(pet.notes) == 0
    pet.add_note("feed high 0700 0715")
    assert len(pet.notes) == 1
    pet.add_note("nap normal 1200 1300")
    assert len(pet.notes) == 2


def test_pet_add_note_rejects_empty():
    pet = Pet("P", "cat")
    with pytest.raises(ValueError):
        pet.add_note("   ")


def test_pet_edit_and_remove_note():
    pet = Pet("P", "cat")
    pet.add_note("walk high 0700 0800")
    pet.edit_note(0, "walk low 0700 0800")
    assert pet.notes[0] == "walk low 0700 0800"
    pet.remove_note(0)
    assert pet.notes == []


# ---------- Task return type ----------

def test_scheduler_tasks_returns_task_instances():
    owner = Owner("O", daily_minutes_available=60)
    pet = Pet("P", "cat")
    owner.add_pet(pet)
    pet.add_note("feed high 0700 0715")

    tasks = Scheduler(owner).tasks()
    assert len(tasks) == 1
    assert isinstance(tasks[0], Task)
