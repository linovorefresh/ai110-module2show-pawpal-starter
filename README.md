# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# Today's Schedule for Camila
# ========================================
#  0700-0715  Twentyone  fill food water  [high, 15 min]
#  0730-0815  Odie      morning walk  [high, 45 min]
#  1000-1030  Odie      training  [normal, 30 min]
#  1800-1845  Odie      evening walk  [normal, 45 min]
#  1900-1915  Twentyone  brush fur  [low, 15 min]
# ----------------------------------------
```

## 🧪 Testing PawPal+

Run the full test suite from the repo root:

```bash
python -m pytest
# Or with coverage:
pytest --cov
```

The suite in `tests/test_pawpal.py` covers:

- **Note parsing** — `parse_note` extracts title, priority, and start/end times; applies defaults when tokens are missing; is case-insensitive for priority; strips the `priority` decorator word; consumes only the first two time tokens; and still parses inverted ranges.
- **Sorting correctness** — `Scheduler.sort_tasks` orders tasks by priority first, then chronologically by start time within the same priority.
- **Plan building** — `Scheduler.build_plan` respects the owner's daily minute budget, skips tasks with invalid time ranges, returns an empty plan when no pets are registered, and aggregates tasks across multiple pets.
- **Pet note management** — `Pet.add_note`, `edit_note`, and `remove_note` add, update, and delete notes and reject empty input.
- **Task return type** — `Scheduler.tasks()` returns `Task` instances.

Sample test output:

```
# Paste your pytest output here
=================================================================================== test session starts ====================================================================================
platform darwin -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/catalino/Desktop/vid-rec/codepath/module2/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 16 items                                                                                                                                                                         

tests/test_pawpal.py ................                                                                                                                                                [100%]

==================================================================================== 16 passed in 0.07s ====================================================================================
```
Confidence Level 4 stars

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
