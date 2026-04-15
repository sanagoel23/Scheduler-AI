from __future__ import annotations

import os
import random
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from csp import generate_assignment_steps, solve_timetable
from graph import (
    build_conflict_graph_from_enrollments,
    build_conflict_graph_from_pairs,
    graph_to_serializable,
)
import uvicorn

app = FastAPI(title="AI Exam Timetable Generator using CSP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class SolveRequest(BaseModel):
    input_mode: Literal["enrollments", "pairs"]
    total_slots: int = Field(ge=1, le=20)
    enrollments: dict[str, list[str]] = Field(default_factory=dict)
    subjects: list[str] = Field(default_factory=list)
    conflict_pairs: list[list[str]] = Field(default_factory=list)


@app.get("/")
def index() -> FileResponse:
    return FileResponse("static/index.html")


def validate_solution(graph: dict[str, set[str]], solution: dict[str, int]) -> bool:
    for subject, neighbors in graph.items():
        for neighbor in neighbors:
            if solution.get(subject) == solution.get(neighbor):
                return False
    return True


@app.get("/api/sample")
def get_sample() -> dict:
    subjects = ["Math", "Physics", "Chemistry", "Biology", "History", "English"]
    student_pool = [f"S{i:02d}" for i in range(1, 21)]

    enrollments: dict[str, list[str]] = {}
    for subject in subjects:
        enrollments[subject] = sorted(random.sample(student_pool, random.randint(6, 11)))

    return {
        "total_slots": 4,
        "input_mode": "enrollments",
        "enrollments": enrollments,
    }


@app.post("/api/solve")
def solve(request: SolveRequest) -> dict:
    if request.input_mode == "enrollments":
        if not request.enrollments:
            raise HTTPException(status_code=400, detail="Please provide enrollments data.")
        graph, conflict_reasons = build_conflict_graph_from_enrollments(request.enrollments)
    else:
        if not request.subjects:
            raise HTTPException(status_code=400, detail="Please provide subjects.")
        graph, conflict_reasons = build_conflict_graph_from_pairs(
            request.subjects, request.conflict_pairs
        )

    if not graph:
        raise HTTPException(status_code=400, detail="No subjects found.")

    algorithm_results = []
    configurations = [
        {"name": "Backtracking", "use_mrv": False, "use_forward_checking": False},
        {"name": "Backtracking + MRV", "use_mrv": True, "use_forward_checking": False},
        {"name": "Backtracking + MRV + Forward Checking", "use_mrv": True, "use_forward_checking": True},
    ]

    best_solution: dict[str, int] | None = None
    best_algo_name = ""

    for config in configurations:
        solution, metrics = solve_timetable(
            graph=graph,
            total_slots=request.total_slots,
            use_mrv=config["use_mrv"],
            use_forward_checking=config["use_forward_checking"],
        )
        algorithm_results.append(
            {
                "algorithm": config["name"],
                "found_solution": solution is not None,
                **metrics,
            }
        )
        if solution is not None and best_solution is None:
            best_solution = solution
            best_algo_name = config["name"]

    if best_solution is None:
        return {
            "success": False,
            "message": "No conflict-free timetable found with the given number of slots.",
            "graph": graph_to_serializable(graph),
            "conflict_reasons": conflict_reasons,
            "algorithm_results": algorithm_results,
        }

    timetable = [
        {"subject": subject, "time_slot": best_solution[subject]}
        for subject in sorted(best_solution.keys())
    ]

    valid = validate_solution(graph, best_solution)

    return {
        "success": True,
        "message": "Conflict-free timetable generated successfully." if valid else "Generated timetable has conflicts.",
        "selected_algorithm": best_algo_name,
        "timetable": timetable,
        "graph": graph_to_serializable(graph),
        "conflict_reasons": conflict_reasons,
        "assignment_steps": generate_assignment_steps(graph, best_solution),
        "algorithm_results": algorithm_results,
        "valid": valid,
        "csp_mapping": {
            "variables": sorted(list(graph.keys())),
            "domain": [f"Slot {slot}" for slot in range(1, request.total_slots + 1)],
            "constraints": "Connected subjects in the conflict graph cannot share the same slot.",
        },
    }


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("RELOAD", "true").lower() in {"1", "true", "yes"}
    uvicorn.run("app:app", host=host, port=port, reload=reload_enabled)

