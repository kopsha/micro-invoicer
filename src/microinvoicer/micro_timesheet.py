"""Module to create fake tasks"""
import random
from datetime import timedelta, date


FAKE_TASKS_POOL = [
    "sprint planning",
    "sprint review",
    "development tasks estimation",
    "defects investigation",
    "worst case analysis",
    "code reviews",
    "refactoring old-code",
    "system architecture updates",
    "release notes",
    "system componend design",
    "public API design",
    "public API implementation",
    "public API integration",
    "{flavor} performance profiling",
    "{flavor} generic mock setup",
    "{flavor} state manager",
    "{flavor} components architecture",
    "{flavor} android communication layer",
    "{flavor} android native implementation",
    "{flavor} iOs communication layer",
    "{flavor} iOs native implementation",
    "{flavor} core implementation",
    "{flavor} class diagram",
    "{flavor} public interfaces",
    "{flavor} core business logic",
    "{flavor} testing module",
    "{flavor} user interface",
    "{flavor} presentation models",
    "{flavor} data modeling",
    "{flavor} event handling",
    "{flavor} exceptions handling",
    "{flavor} component design",
    "{flavor} component integration",
    "{flavor} defects verification",
    "{flavor} defects analysis",
    "{flavor} defects correction",
    "{flavor} code coverage testing",
    "{flavor} low level api",
]


def fake_timesheet(hours, flavor, project_id, start_date):
    timesheet = dict(start_date=start_date, flavor=flavor, project_id=project_id)
    how_many = random.randrange(8, stop=18)
    timesheet["tasks"] = create_random_tasks(timesheet, how_many, hours=hours)

    return timesheet


def previous_month():
    today = date.today()
    last_month = today.replace(day=1) - timedelta(days=1)
    last_month = last_month.replace(day=1)
    return last_month


def create_random_tasks(activity, how_many, hours):
    names = pick_task_names(flavor=activity["flavor"], count=how_many)
    durations = split_duration(duration=hours, count=how_many)
    dates = compute_start_dates(activity["start_date"], durations)
    projects = [activity["project_id"]] * how_many

    tasks = [
        dict(name=name, date=date, duration=duration, project=project)
        for name, date, duration, project in zip(names, dates, durations, projects)
    ]

    return tasks


def pick_task_names(flavor, count):
    tasks = [
        name.format(flavor=flavor).capitalize() for name in random.sample(FAKE_TASKS_POOL, k=count)
    ]
    return tasks


def split_duration(duration, count):
    left = duration
    splits = []
    step = 1

    for step in range(count - 1):
        max_split = round(left * (0.618 * (step + 2) / count))
        min_split = min(4, max_split - 1)
        current_split = random.randrange(min_split, stop=max_split)
        splits.append(current_split)
        left -= current_split

    splits.append(left)

    return splits


def compute_start_dates(start_date, durations):
    dates = []
    trace_date = start_date
    for duration in durations:
        trace_date += timedelta(days=round(duration / 8))
        if trace_date.weekday() > 4:
            trace_date += timedelta(days=7 - trace_date.weekday())
        dates.append(trace_date)

    return dates


if __name__ == "__main__":
    print("This is a pure module, it cannot be executed.")
