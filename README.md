# AI Exam Timetable Generator using CSP

A clean, professional full-stack application that generates a conflict-free exam timetable using **Constraint Satisfaction Problem (CSP)** techniques.

This project is designed for academic submission and portfolio demonstration, with strong focus on clarity, correctness, and explainability.

## Project Overview

The system schedules subjects into available exam time slots while ensuring that subjects with common students are never assigned the same slot.

It supports two input styles:

1. **Preferred**: `Subject -> list of students`
2. **Alternative**: Direct subject conflict pairs

## CSP Mapping

- **Variables**: Subjects (e.g., Math, Physics)
- **Domains**: Allowed exam slots (e.g., Slot 1, Slot 2, ...)
- **Constraints**: Conflicting subjects (shared students or manually defined conflicts) cannot share a slot

## Features

- Build conflict graph from enrollments or conflict pairs
- CSP solver with:
  - Backtracking (mandatory baseline)
  - MRV heuristic
  - Forward Checking
- Conflict-free timetable generation
- Explainability:
  - Why subjects conflict
  - How slots are assigned
- Performance comparison table:
  - Execution time
  - Recursive calls
  - Constraint checks
- Option to select number of time slots
- Auto-generated sample dataset
- Minimal, professional dashboard-style UI

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, FastAPI
- **Charts**: Not required (table-first approach used)

## Code Structure

- `app.py` -> FastAPI backend and API routes
- `csp.py` -> CSP algorithms (`is_valid`, `backtracking`, MRV, forward checking)
- `graph.py` -> Conflict graph creation and processing
- `metrics.py` -> Performance metrics tracking
- `static/index.html` -> UI structure
- `static/styles.css` -> Minimal professional styling
- `static/app.js` -> Frontend logic and API integration

## Setup Instructions

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
uvicorn app:app --reload
```

Alternative (recommended, one-command reliable startup):

```bash
bash run.sh
```

4. Open in browser:

```text
http://127.0.0.1:8000
```

## Example Input/Output

### Example Input (Option A)

```text
Math: S1, S2, S3
Physics: S2, S4
Chemistry: S1, S5
Biology: S6, S7
```

Time slots: `3`

### Example Output

```text
Math -> Slot 1
Physics -> Slot 2
Chemistry -> Slot 2
Biology -> Slot 1
```

Validation: `Conflict-free timetable generated successfully.`

## Algorithm Explanation (Simple)

1. Build a conflict graph:
   - Each subject is a node.
   - An edge is added when two subjects share students (or are manually marked as conflicting).
2. Start CSP solving using backtracking.
3. Use **MRV** to pick the subject with the fewest remaining valid slots first.
4. Use **Forward Checking** to remove invalid slots from neighboring subjects after each assignment.
5. Continue until all subjects are assigned, or report that no solution exists for current slot count.


