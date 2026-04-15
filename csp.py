from copy import deepcopy

from metrics import Metrics


def is_valid(
    subject: str,
    slot: int,
    assignment: dict[str, int],
    graph: dict[str, set[str]],
    metrics: Metrics,
) -> bool:
    """Check if assigning slot to subject breaks any conflict constraint."""
    for neighbor in graph.get(subject, set()):
        metrics.constraint_checks += 1
        if assignment.get(neighbor) == slot:
            return False
    return True


def select_unassigned_variable_mrv(
    assignment: dict[str, int],
    domains: dict[str, set[int]],
) -> str:
    """
    MRV: choose the unassigned subject with the smallest remaining domain.
    Ties are broken alphabetically for deterministic outputs.
    """
    unassigned = [subject for subject in domains if subject not in assignment]
    return min(unassigned, key=lambda s: (len(domains[s]), s))


def forward_check(
    subject: str,
    slot: int,
    assignment: dict[str, int],
    domains: dict[str, set[int]],
    graph: dict[str, set[str]],
    metrics: Metrics,
) -> tuple[bool, dict[str, set[int]]]:
    """
    Remove the chosen slot from neighboring unassigned variables.
    Returns whether the branch remains consistent and the updated domains.
    """
    new_domains = deepcopy(domains)

    for neighbor in graph.get(subject, set()):
        if neighbor in assignment:
            continue
        metrics.constraint_checks += 1
        if slot in new_domains[neighbor]:
            new_domains[neighbor].remove(slot)
            if not new_domains[neighbor]:
                return False, new_domains

    return True, new_domains


def backtracking(
    assignment: dict[str, int],
    domains: dict[str, set[int]],
    graph: dict[str, set[str]],
    metrics: Metrics,
    use_mrv: bool = True,
    use_forward_checking: bool = True,
) -> dict[str, int] | None:
    metrics.recursive_calls += 1

    if len(assignment) == len(graph):
        return assignment

    if use_mrv:
        subject = select_unassigned_variable_mrv(assignment, domains)
    else:
        subject = next(s for s in domains if s not in assignment)

    for slot in sorted(domains[subject]):
        if not is_valid(subject, slot, assignment, graph, metrics):
            continue

        new_assignment = dict(assignment)
        new_assignment[subject] = slot

        if use_forward_checking:
            consistent, next_domains = forward_check(
                subject=subject,
                slot=slot,
                assignment=new_assignment,
                domains=domains,
                graph=graph,
                metrics=metrics,
            )
            if not consistent:
                continue
        else:
            next_domains = domains

        result = backtracking(
            assignment=new_assignment,
            domains=next_domains,
            graph=graph,
            metrics=metrics,
            use_mrv=use_mrv,
            use_forward_checking=use_forward_checking,
        )
        if result is not None:
            return result

    return None


def solve_timetable(
    graph: dict[str, set[str]],
    total_slots: int,
    use_mrv: bool = True,
    use_forward_checking: bool = True,
) -> tuple[dict[str, int] | None, dict]:
    domains = {subject: set(range(1, total_slots + 1)) for subject in graph}
    metrics = Metrics()
    metrics.start()

    solution = backtracking(
        assignment={},
        domains=domains,
        graph=graph,
        metrics=metrics,
        use_mrv=use_mrv,
        use_forward_checking=use_forward_checking,
    )
    metrics.stop()
    return solution, metrics.as_dict()


def generate_assignment_steps(graph: dict[str, set[str]], assignment: dict[str, int]) -> list[str]:
    """
    Build a readable explanation of assigned slots.
    """
    steps: list[str] = []
    for subject in sorted(assignment.keys()):
        slot = assignment[subject]
        conflicting_neighbors = sorted(graph.get(subject, []))
        if conflicting_neighbors:
            neighbor_text = ", ".join(conflicting_neighbors)
            steps.append(
                f"{subject} -> Slot {slot} because it avoids conflicts with: {neighbor_text}."
            )
        else:
            steps.append(f"{subject} -> Slot {slot} (no direct conflicts with other subjects).")
    return steps
