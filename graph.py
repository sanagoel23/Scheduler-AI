from itertools import combinations


def build_conflict_graph_from_enrollments(enrollments: dict[str, list[str]]) -> tuple[dict[str, set[str]], list[dict]]:
    """
    Build a graph where each subject is a node and edges represent
    at least one shared student.
    """
    subjects = list(enrollments.keys())
    graph = {subject: set() for subject in subjects}
    conflict_reasons: list[dict] = []

    for subject_a, subject_b in combinations(subjects, 2):
        students_a = set(enrollments.get(subject_a, []))
        students_b = set(enrollments.get(subject_b, []))
        shared = sorted(students_a.intersection(students_b))
        if shared:
            graph[subject_a].add(subject_b)
            graph[subject_b].add(subject_a)
            conflict_reasons.append(
                {
                    "subject_a": subject_a,
                    "subject_b": subject_b,
                    "shared_students": shared,
                }
            )

    return graph, conflict_reasons


def build_conflict_graph_from_pairs(subjects: list[str], pairs: list[list[str]]) -> tuple[dict[str, set[str]], list[dict]]:
    """Build a graph directly from subject conflict pairs."""
    graph = {subject: set() for subject in subjects}
    conflict_reasons: list[dict] = []

    for pair in pairs:
        if len(pair) != 2:
            continue
        subject_a, subject_b = pair[0].strip(), pair[1].strip()
        if subject_a not in graph or subject_b not in graph or subject_a == subject_b:
            continue
        graph[subject_a].add(subject_b)
        graph[subject_b].add(subject_a)
        conflict_reasons.append(
            {
                "subject_a": subject_a,
                "subject_b": subject_b,
                "shared_students": [],
            }
        )

    return graph, conflict_reasons


def graph_to_serializable(graph: dict[str, set[str]]) -> dict[str, list[str]]:
    return {subject: sorted(list(neighbors)) for subject, neighbors in graph.items()}
