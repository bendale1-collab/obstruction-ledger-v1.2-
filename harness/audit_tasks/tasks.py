"""inspect_ai scaffold: registers the four audit classes as tasks.

The mechanical audit logic lives in ol/audit/classes.py (card B1-01).
These tasks are the harness wiring that lets `inspect list tasks` and
`inspect eval` enumerate and run each class through inspect_ai's
dataset/solver/scorer pipeline; they do not themselves define the
audit predicates.
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import generate


def _single_sample_task(class_name: str) -> Task:
    sample = Sample(
        input=f"Audit class {class_name}: evaluate the attached trajectory.",
        target=class_name,
    )
    return Task(
        dataset=[sample],
        solver=[generate()],
        scorer=includes(),
    )


@task
def a_weak() -> Task:
    return _single_sample_task("A_weak")


@task
def a_selfev() -> Task:
    return _single_sample_task("A_selfev")


@task
def a_nonex() -> Task:
    return _single_sample_task("A_nonex")


@task
def a_pad() -> Task:
    return _single_sample_task("A_pad")
