<!--
Sync Impact Report
- Version change: unratified template -> 1.0.0
- Modified principles:
  - Template Principle 1 -> I. Stable Data Contract and Durable Writes
  - Template Principle 2 -> II. Shared Core and Thin Interfaces
  - Template Principle 3 -> III. Test-First Development (NON-NEGOTIABLE)
  - Template Principle 4 -> IV. Contract and End-to-End Verification
  - Template Principle 5 -> V. Local Simplicity and Controlled Scope
- Added sections:
  - Technical Constraints
  - Development Workflow
- Removed sections: none
- Follow-up TODOs: none
-->

# TaskHub Constitution

## Core Principles

### I. Stable Data Contract and Durable Writes

`tasks.json` MUST have the document shape `{ "version": 1, "tasks": [...] }`. Each task MUST be
the exact serialization of the `Task` dataclass without undeclared fields. Schema changes MUST
increment the document version and update the model, validator, CLI, UI, and tests together.

Every data mutation MUST use the shared storage write path. The write path MUST snapshot the
current file, write UTF-8 JSON to a temporary file, and atomically replace `tasks.json`. Undo MUST
use the internal history, retain at most three snapshots, and accept only one to three steps.
These rules protect user data and keep recovery behavior independent of Git or interface choice.

### II. Shared Core and Thin Interfaces

Business rules and file operations MUST reside in the model, storage, validation, or shared
controller layer. CLI, Tkinter UI, and MCP adapters MUST only validate interface-specific input,
invoke shared operations, and present results. They MUST NOT implement competing persistence or
domain logic.

Equivalent operations exposed through multiple interfaces MUST preserve the same task fields,
status transitions, error meaning, and storage effects. The Tkinter UI MUST remain a separate
local adapter and MUST NOT change existing CLI contracts merely for presentation convenience.
This separation keeps behavior consistent and allows headless testing of core functionality.

### III. Test-First Development (NON-NEGOTIABLE)

Every behavior change MUST follow Red-Green-Refactor: first add or update a test that fails for
the intended reason, then implement the smallest change that makes it pass, and only then perform
limited refactoring. A feature MUST include tests for its primary scenario and at least one
relevant error or boundary scenario.

Existing tests MUST remain green. Tests MUST use temporary storage and MUST NOT depend on network
access, a developer's `tasks.json`, Git history, or a graphical display unless the test explicitly
isolates the Tk adapter. A change without executable evidence of its requirements is incomplete.

### IV. Contract and End-to-End Verification

Public behavior MUST be specified in observable terms before implementation. CLI output MUST
preserve documented formats, including list rows, undo success output, and nonzero exit codes for
invalid input or missing entities. UI behavior MUST define actions, disabled states, successful
refreshes, and visible error states. Storage and validation behavior MUST define accepted data and
failure semantics.

Changes that cross an interface boundary MUST include a test that exercises the complete local
path from the interface or controller through storage and back to an observable result. Schema,
serialization, filtering, status, history, and shared error changes MUST also retain focused unit
coverage. This makes agreements between UI and logic independently verifiable.

### V. Local Simplicity and Controlled Scope

TaskHub MUST remain an offline Python 3.11+ application using the standard library, Typer, pytest,
and Tkinter supplied by Python. Production code MUST NOT perform network requests or contain MCP,
plugin, or agent orchestration logic. New runtime dependencies require explicit human approval
and a documented reason that the existing stack cannot satisfy.

Changes MUST be limited to `practices/practice_04/` unless the user explicitly approves a wider
scope. Implementations MUST prefer the smallest correct design, preserve compatible behavior, and
avoid speculative abstractions or backward-compatibility layers without a concrete consumer.
Simplicity is required because the project is intentionally small and locally inspectable.

## Technical Constraints

- `Task` MUST remain the canonical domain model. IDs MUST be UUID4 values produced by `Task.new`.
- Status MUST be `todo` or `done` unless a versioned schema change explicitly extends it.
- `created_at` and non-null `due_date` values MUST use `ISO_FORMAT` in UTC with a `Z` suffix.
- JSON MUST be UTF-8, use two-space indentation, and preserve non-ASCII text.
- CLI stdout MUST contain only documented command output; user errors MUST return a nonzero code.
- The list format MUST remain `<id> [status] title (due=... tags=...)` unless its contract is
  explicitly revised together with tests and documentation.
- Source code MUST use type annotations, snake_case naming, and lines no longer than 100 characters.
- CLI code belongs in `src/taskhub/app.py`, Tk UI code in `src/taskhub/gui.py`, persistence in
  `src/taskhub/storage.py`, and model serialization in `src/taskhub/models.py`.

## Development Workflow

1. Read `AGENTS.md`, `STYLE_GUIDE.md`, affected code, and existing tests before proposing changes.
2. Record requirements, preserved behavior, errors, boundaries, and explicit exclusions before code.
3. For work spanning UI and logic, agree on one contract covering data, calls, errors, and states.
4. Add a failing test, confirm the failure, implement the minimum behavior, and rerun focused tests.
5. Run `pytest -q` and `python3 tools/lint.py` from `practices/practice_04/` before acceptance.
6. Inspect the diff and report actual verification results, including any checks that could not run.
7. Do not commit, archive a specification, or broaden scope without explicit human approval.

A change is complete only when its requirements, implementation, documentation where applicable,
and tests agree. Failed quality gates MUST be fixed or explicitly accepted by the user before the
change is considered ready.

## Governance

This constitution is the highest project-level engineering policy for TaskHub. `AGENTS.md`,
`STYLE_GUIDE.md`, specifications, plans, and implementation decisions MUST comply with it. When
documents conflict, the constitution takes precedence; a specification cannot silently override a
constitutional rule.

Amendments MUST be proposed as an explicit constitution change, explain the motivation and impact,
and receive human approval before dependent implementation begins. An amendment MUST update the
Sync Impact Report, version, and amendment date. If it changes persisted data or public behavior,
it MUST also identify the required migration, compatibility decision, and affected verification.

Constitution versions follow semantic versioning: MAJOR for incompatible governance changes or
principle removals, MINOR for new principles or materially expanded obligations, and PATCH for
clarifications that do not change requirements. Every feature review MUST verify constitutional
compliance, and any justified exception MUST be documented and approved by the user before merge.

**Version**: 1.0.0 | **Ratified**: 2026-11-01 | **Last Amended**: 2026-11-01
