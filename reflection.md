# PawPal+ Project Reflection

## 1. System Design

### Core actions

- Add pet & info
- Add/edit tasks and info
- Generate schedule plan

**a. Initial design**

The initial UML centers on five classes covering the three core actions (add pet, add/edit tasks, generate plan):

- **Pet** — holds info about a single animal (`name`, `species`, `breed`, `age_years`, `notes`). `update_info()` lets the owner edit any field.
- **Owner** — the user. Owns a list of `Pet`s plus the day-level constraint `daily_minutes_available` and a loose `preferences` dict. `add_pet()` and `update_info()` cover the "add pet & info" action.
- **Task** — one care task tied to a pet (`title`, `duration_minutes`, `priority`, optional `category`, `notes`). `update()` covers the "edit tasks" action.
- **Scheduler** — pure logic. Holds an `Owner` and `tasks` list. `sort_tasks()` orders by priority then duration; `build_plan()` greedily fills the day budget; `explain_choice()` produces per-task reasoning.
- **Plan** — the output. Carries `scheduled` and `skipped` task lists (each with a reason), `total_minutes_used`, and `day_budget`. `render()` returns rows for the Streamlit table; `explain()` returns a narrative.

Relationships: `Owner 1—* Pet`, `Pet 1—* Task`, `Scheduler` uses `Owner`/`Task` and produces a `Plan`. Splitting `Scheduler` from `Plan` keeps scheduling logic separate from the UI-facing output object so each can be tested on its own.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
