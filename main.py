"""Demo runner for PawPal+.

Builds a small Owner + Pets + notes graph and prints today's schedule.
"""

from pawpal_system import Owner, Pet, Scheduler


def main() -> None:
    owner = Owner(name="Camila", daily_minutes_available=180)

    twentyone = Pet(name="Twentyone", species="cat", age_years=3)
    odie = Pet(name="Odie", species="dog", breed="Golden Retriever", age_years=5)
    owner.add_pet(twentyone)
    owner.add_pet(odie)

    twentyone.add_note("fill food water high 0700 0715")
    twentyone.add_note("brush fur low 1900 1915")

    odie.add_note("morning walk high 0730 0815")
    odie.add_note("training normal 1000 1030")
    odie.add_note("evening walk normal 1800 1845")

    plan = Scheduler(owner).build_plan()

    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    for item in plan.render():
        print(
            f"  {item['start']}-{item['end']}  "
            f"{item['pet_name']:8s}  {item['title']}  "
            f"[{item['priority']}, {item['duration_minutes']} min]"
        )
    print("-" * 40)
    print(f"Used {plan.total_minutes_used} of {plan.day_budget} min.")

    if plan.skipped:
        print("\nSkipped:")
        for item in plan.skipped:
            print(f"  {item['pet_name']:8s}  {item['title']} — {item['reason']}")


if __name__ == "__main__":
    main()
