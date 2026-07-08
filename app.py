from datetime import time

import streamlit as st

from pawpal_system import WEEKDAYS, Owner, Pet, Plan, Scheduler, parse_note

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. Enter your info, add pets and tasks, then generate this week's schedule.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

with st.expander("What the app does", expanded=False):
    st.markdown(
        """
- Represents owner + pets and their care tasks.
- Parses each task into `(title, priority, start, end, duration)`.
- Builds a weekly plan that respects your daily minute budget, ordered by priority.
- Explains why each task was scheduled or skipped.
"""
    )

st.divider()

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Lino", daily_minutes_available=180)
if "plan" not in st.session_state:
    st.session_state.plan = None
if "completed" not in st.session_state:
    st.session_state.completed = {}
owner: Owner = st.session_state.owner

# --- Owner ---
st.subheader("Owner")
o_col1, o_col2 = st.columns(2)
with o_col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with o_col2:
    owner.daily_minutes_available = int(
        st.number_input(
            "Daily minutes available",
            min_value=15,
            max_value=1440,
            value=owner.daily_minutes_available,
            step=15,
        )
    )

st.divider()

# --- Pets ---
st.subheader("Pets")

if owner.pets:
    for i, pet in enumerate(owner.pets):
        row = st.columns([4, 1])
        with row[0]:
            details = pet.species
            if pet.breed:
                details += f", {pet.breed}"
            if pet.age_years:
                details += f", age {pet.age_years}"
            st.write(f"**{pet.name}** — {details}")
        with row[1]:
            if st.button("Remove", key=f"remove_pet_{i}"):
                owner.pets.pop(i)
                st.rerun()

with st.expander("Add a pet"):
    with st.form("add_pet_form", clear_on_submit=True):
        new_name = st.text_input("Name")
        new_species = st.selectbox("Species", ["dog", "cat", "other"])
        new_breed = st.text_input("Breed (optional)")
        new_age = st.number_input(
            "Age in years (optional)", min_value=0, max_value=40, value=0
        )
        if st.form_submit_button("Add pet"):
            if not new_name.strip():
                st.error("Pet name is required.")
            else:
                owner.add_pet(
                    Pet(
                        name=new_name.strip(),
                        species=new_species,
                        breed=new_breed.strip() or None,
                        age_years=int(new_age) if new_age else None,
                    )
                )
                st.rerun()

st.divider()

# --- Tasks ---
st.subheader("Tasks")

if not owner.pets:
    st.info("Add a pet to begin.")
else:
    pet_names = [p.name for p in owner.pets]
    selected_name = st.selectbox("Pet", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_name)

    with st.form("add_task_form", clear_on_submit=False):
        title = st.text_input("Task title", value="fill food water bowl")
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            priority = st.selectbox("Priority", ["high", "normal", "low"], index=1)
        with t_col2:
            start_t = st.time_input("Start", value=time(7, 0))
        with t_col3:
            end_t = st.time_input("End", value=time(8, 0))
        selected_days = st.multiselect(
            "Days",
            WEEKDAYS,
            default=list(WEEKDAYS),
            help="Which weekdays this task recurs on.",
        )
        if st.form_submit_button("Add task"):
            if not title.strip():
                st.error("Task title is required.")
            elif not selected_days:
                st.error("Pick at least one day.")
            else:
                ordered_days = [d for d in WEEKDAYS if d in selected_days]
                days_token = "days=" + ",".join(ordered_days)
                note_str = (
                    f"{title.strip()} {priority} "
                    f"{start_t.strftime('%H%M')} {end_t.strftime('%H%M')} "
                    f"{days_token}"
                )
                selected_pet.add_note(note_str)
                st.rerun()

    if selected_pet.notes:
        st.caption(f"Tasks for {selected_pet.name}:")
        for i, note in enumerate(selected_pet.notes):
            parsed = parse_note(note, pet_name=selected_pet.name)
            days_label = (
                "daily" if len(parsed.days) == 7 else ", ".join(parsed.days)
            )
            n_row = st.columns([5, 1])
            with n_row[0]:
                st.code(note, language="text")
                st.caption(f"Days: {days_label}")
            with n_row[1]:
                if st.button("Remove", key=f"remove_note_{selected_pet.name}_{i}"):
                    selected_pet.remove_note(i)
                    st.rerun()
    else:
        st.caption("No tasks yet for this pet.")

st.divider()

# --- Generate schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule", type="primary"):
    st.session_state.plan = Scheduler(owner).build_weekly_plan()
    st.session_state.completed = {}
    st.rerun()


def render_day_rows(day: str, day_plan: Plan, pets_filter, status_filter, sort_dir):
    col_spec = [1, 2, 2, 4, 1, 1]
    filtered = [
        (i, r) for i, r in enumerate(day_plan.scheduled)
        if r["pet_name"] in pets_filter
    ]
    filtered.sort(
        key=lambda pair: pair[1]["start"], reverse=(sort_dir == "Descending")
    )

    header = st.columns(col_spec)
    header[0].markdown("**Done**")
    header[1].markdown("**Time**")
    header[2].markdown("**Pet**")
    header[3].markdown("**Task**")
    header[4].markdown("**Priority**")
    header[5].markdown("**Duration**")

    shown = 0
    for i, r in filtered:
        key = (day, i)
        done = st.session_state.completed.get(key, False)
        if status_filter == "Pending" and done:
            continue
        if status_filter == "Completed" and not done:
            continue

        cols = st.columns(col_spec)
        st.session_state.completed[key] = cols[0].checkbox(
            "done",
            value=done,
            key=f"done_{day}_{i}",
            label_visibility="collapsed",
        )
        is_done = st.session_state.completed[key]
        open_tag = '<span style="color:#999;opacity:0.55;">' if is_done else ""
        close_tag = "</span>" if is_done else ""
        time_str = (
            f"{r['start'][:2]}:{r['start'][2:]}–{r['end'][:2]}:{r['end'][2:]}"
        )
        cols[1].markdown(f"{open_tag}{time_str}{close_tag}", unsafe_allow_html=True)
        cols[2].markdown(f"{open_tag}{r['pet_name']}{close_tag}", unsafe_allow_html=True)
        cols[3].markdown(f"{open_tag}{r['title']}{close_tag}", unsafe_allow_html=True)
        cols[4].markdown(f"{open_tag}{r['priority']}{close_tag}", unsafe_allow_html=True)
        cols[5].markdown(
            f"{open_tag}{r['duration_minutes']}m{close_tag}", unsafe_allow_html=True
        )
        shown += 1

    if shown == 0:
        st.caption(f"No tasks for {day}.")


weekly = st.session_state.plan
if weekly is not None and weekly.total_scheduled() > 0:
    st.subheader("This Week's Schedule")

    pet_names_in_plan = sorted(
        {r["pet_name"] for p in weekly.days.values() for r in p.scheduled}
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        selected_pets = st.multiselect(
            "Filter by pet", pet_names_in_plan, default=pet_names_in_plan
        )
    with c2:
        status = st.radio(
            "Status", ["All", "Pending", "Completed"], horizontal=True
        )
    with c3:
        sort_dir = st.radio(
            "Sort by time", ["Ascending", "Descending"], horizontal=True
        )

    tabs = st.tabs(WEEKDAYS)
    for day, tab in zip(WEEKDAYS, tabs):
        with tab:
            render_day_rows(
                day, weekly.days[day], selected_pets, status, sort_dir
            )

    with st.expander("Explanation"):
        st.text(weekly.explain())
elif weekly is not None:
    st.info("No tasks scheduled — add notes to a pet first.")
