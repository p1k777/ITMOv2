# Project Management - Practice 2 - Scenario 1

Goal
- Bring the "Project Management" artifact to a complete state for Practice 2, Scenario 1, with clear rule traceability, measurable verifiability, aligned dependencies, and a textual Gantt.
- Minimality: strictly within Scenario 1.

Scope and Assumptions
- Repository: ITMOv2, Practice 2.
- Editable artifact: this document. Checks and measures are textual, no non-focused sections added.
- Accepted rules: SEC-1, API-1, REL-1, OUT-1, QA-1, OBS-1.

Traceability to Rules
- Each rule section includes: short description, measurable criteria, checks (unit/integration/e2e/contract) with preconditions, steps, expected outcomes; for SEC-1/REL-1/OBS-1 also metrics/signals.

## SEC-1 - Basic Security
Description
- Control secrets and vulnerabilities, secure configurations, forbid storing sensitive data in code.

Measurable Criteria
- Secrets in code: 0 detects (secret_scan_findings == 0).
- Critical dependency vulnerabilities: 0 (vuln_critical == 0).
- Minimum TLS/HTTPS version for outbound calls: >= 1.2.
- Timeouts on every network call: each call has timeout <= 5s.

Checks
- unit:
  Preconditions: secret scanner/linter configured in repo.
  Steps: run local secret-scan across all files.
  Expected: 0 findings, report shows "secret_scan_findings: 0".
- integration:
  Preconditions: CI job for dependency and secret scanning configured.
  Steps: run CI on branch; wait for scanning jobs.
  Expected: all checks pass, no critical CVEs.
- e2e:
  Preconditions: blocking CI policies enabled.
  Steps: commit a file with a secret marker (e.g. "AWS_SECRET_ACCESS_KEY=..."); open PR.
  Expected: PR is blocked, "Secret Scan" check fails with reason.
- contract:
  Preconditions: security-policy.yml accepted (TLS>=1.2, timeouts<=5s, no open ports outside allowlist).
  Steps: run policy-checker against configs and codebase.
  Expected: all requirements satisfied, signed report produced.

Metrics/Signals (OBS-1/REL-1/SEC-1)
- security.secret_scan_findings (count) - target: 0.
- security.vuln_critical (count) - target: 0.
- security.token_leak_attempts (events) - target: 0/week.

## API-1 - API Contract and Correctness
Description
- Clear input/output schemas, fixed specification (e.g. OpenAPI), stable status codes.

Measurable Criteria
- API spec (openapi.yaml) exists, versioned and accessible.
- Contract tests: 100% coverage of declared endpoints.
- p95_latency for key endpoint: < 250ms under test load.
- 5xx error rate: < 0.5% under test load.

Checks
- unit:
  Preconditions: DTO/schemas defined.
  Steps: validate serialization/deserialization for typical payloads.
  Expected: objects conform to schema, no exceptions.
- integration:
  Preconditions: service running in test environment.
  Steps: call service endpoints; validate responses against schemas.
  Expected: status codes correct, responses validate against openapi.yaml.
- e2e:
  Preconditions: end-to-end user scenario prepared.
  Steps: execute full user scenario calling API.
  Expected: functional outcome achieved, latency metrics within limits.
- contract:
  Preconditions: spec and consumers/providers fixed.
  Steps: run consumer/provider contract tests.
  Expected: contract matches actual behavior; no discrepancies.

## REL-1 - Reliability and Resilience
Description
- Timeouts, retries with exponential backoff, fallbacks to degraded modes.

Measurable Criteria
- Successful request ratio: >= 99% in test environment.
- p95_error_rate: < 1%.
- Recovery time for dependency failure: <= 30s.
- Fallback mechanisms exist for critical dependencies.

Checks
- unit:
  Preconditions: retry/timeout mechanisms implemented.
  Steps: test backoff growth and max-attempt enforcement.
  Expected: retries capped, timeouts enforced, backoff increases.
- integration:
  Preconditions: dependency can be made unavailable.
  Steps: simulate failure; observe fallback activation.
  Expected: service remains up; returns degraded response.
- e2e:
  Preconditions: scenario toggling dependencies is prepared.
  Steps: run scenario; measure recovery time.
  Expected: recovery <= 30s; user flow completes.
- contract:
  Preconditions: SLO/SLA documented (availability, latency).
  Steps: check observed metrics against thresholds.
  Expected: values within bounds; on breach - alert and incident procedure.

Metrics/Signals (OBS-1/REL-1)
- reliability.error_rate (fraction) - target: < 1%.
- reliability.availability (fraction) - target: >= 99%.
- reliability.recovery_time_seconds - target: <= 30.

## OUT-1 - Outputs/Artifacts
Description
- Deterministic, versioned outputs (files, reports, events), agreed format.

Measurable Criteria
- Output schema version pinned (schema_version pinned).
- Idempotency of artifact generation: repeat yields same result for same inputs.
- Standardized path and naming of artifacts.

Checks
- unit:
  Preconditions: output data schema defined.
  Steps: test function producing output structures.
  Expected: structure conforms to schema, fields valid.
- integration:
  Preconditions: artifact generation pipeline configured.
  Steps: run generation; check files/records exist.
  Expected: artifacts appear at expected paths and formats.
- e2e:
  Preconditions: full scenario consuming outputs prepared.
  Steps: reproduce scenario; compare reports to golden.
  Expected: report identical to golden, no diffs.
- contract:
  Preconditions: consumer format agreed.
  Steps: run consumer contract checks against artifact.
  Expected: consumer accepts artifact without errors.

## QA-1 - Quality and Testing
Description
- Test completeness and code quality: coverage thresholds, static analysis, mandatory CI checks.

Measurable Criteria
- Unit test coverage: >= 80% lines/branches.
- All tests (unit/integration/e2e/contract) green on main branch.
- Static checks (linters) - no errors.

Checks
- unit:
  Preconditions: test environment and coverage reporting configured.
  Steps: run unit suite; collect coverage.
  Expected: coverage >= 80%; tests green.
- integration:
  Preconditions: stubs/test dependencies ready.
  Steps: run integration tests.
  Expected: scenarios pass; interactions correct.
- e2e:
  Preconditions: end-to-end test scenarios documented.
  Steps: run e2e.
  Expected: functionality meets requirements; no regressions.
- contract:
  Preconditions: mandatory contract check in CI.
  Steps: run contract tests.
  Expected: all contracts pass; no violations.

## OBS-1 - Observability
Description
- Structured logs, metrics, and traces; request-id correlation; alerting on SLOs.

Measurable Criteria
- Logs: 100% of key operations logged in structured format.
- Metrics: export key metrics (latency, error_rate, throughput).
- Traces: > 80% coverage of critical paths.
- Alerting: SLO thresholds configured, ack time < 5 minutes.

Checks
- unit:
  Preconditions: logging/metrics module implemented.
  Steps: validate log format and counter increments.
  Expected: format matches agreed spec, metrics increment.
- integration:
  Preconditions: test sinks for logs/metrics available.
  Steps: run scenarios; collect logs/metrics.
  Expected: records arrive, metrics exposed, traces formed.
- e2e:
  Preconditions: all observability parts enabled.
  Steps: run working scenario; verify request-id correlation.
  Expected: events are linked; dashboards show expected values.
- contract:
  Preconditions: observability-spec approved (required log fields, metric list, trace format).
  Steps: run validator against logs/metrics/traces.
  Expected: spec satisfied; discrepancies = 0.

Metrics/Signals (OBS-1)
- observability.log_coverage (fraction) - target: 100% of key operations.
- observability.trace_coverage (fraction) - target: > 80%.
- observability.alert_ack_time_seconds - target: < 300.

---

Dependencies and Increments

Dependency List
- I0 (Setup) - environment and CI preparation. Deps: none.
- I1 (SEC-1 baseline) - secret-scan and policies. Deps: I0.
- I2 (API-1 contract) - API spec and contract tests. Deps: I0.
- I3 (QA-1 harness) - coverage thresholds and test harness. Deps: I1, I2.
- I4 (OBS-1 instrumentation) - metrics/logs/traces. Deps: I2, I3.
- I5 (REL-1 resilience) - timeouts/retries/fallbacks. Deps: I2, I4.
- I6 (OUT-1 outputs) - formats and artifacts. Deps: I2, I3.

Increments (table)

| ID | Name                     | Duration | Deps |
|----|--------------------------|----------|------|
| I0 | Setup                    | 0.5d     | -    |
| I1 | SEC-1 baseline           | 0.5d     | I0   |
| I2 | API-1 contract           | 1d       | I0   |
| I3 | QA-1 harness             | 1d       | I1,I2|
| I4 | OBS-1 instrumentation    | 1d       | I2,I3|
| I5 | REL-1 resilience         | 1d       | I2,I4|
| I6 | OUT-1 outputs            | 0.5d     | I2,I3|

Textual Gantt (dates/durations/dependencies)
- Start: 2026-09-19.
- 2026-09-19 (morning-afternoon): I0 Setup [no deps].
- 2026-09-19 (afternoon-evening): I1 SEC-1 baseline [after I0].
- 2026-09-20: I2 API-1 contract [after I0].
- 2026-09-21: I3 QA-1 harness [after I1, I2].
- 2026-09-22: I4 OBS-1 instrumentation [after I2, I3].
- 2026-09-23: I5 REL-1 resilience [after I2, I4].
- 2026-09-24 (morning): I6 OUT-1 outputs [after I2, I3].

Gantt Consistency
- All tasks are scheduled respecting the declared dependencies; no conflicting parallel starts.

---

AI (LLM) Section
- Role: assistant for documentation and check formulation; help generating test cases and specs.
- Constraints: does not change runtime-affecting code without review; adheres to SEC-1 (no secrets), API-1 (no contract violations), QA-1 (test formats), OBS-1 (records actions when needed).
- Tools: Read/Grep/Glob for search; apply_patch for documentation edits; no destructive git commands.
- Scope: only Scenario 1 and the current files; no non-focused sections.
- Verification: each proposed change includes measurable criteria and checks (unit/integration/e2e/contract) with expected outcomes; compliance proven by passing checks.

---



Minimality
- Non-focused improvements outside Scenario 1 are excluded; content is self-sufficient for traceability, verifiability, and planning.
