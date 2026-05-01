# Project State Review (2026-05-01)

## Current health snapshot

- `pytest -q` fails during collection because the package is not importable in a plain checkout without installation or `PYTHONPATH` overrides.
- Even after using `PYTHONPATH=.`, tests still fail at import time because runtime dependencies (e.g., `pydantic`) are not installed in the current environment.
- Core simulation logic is cleanly segmented, but there are validation and robustness gaps that can cause brittle behavior as scenarios evolve.

## Problem areas and likely bugs

### 1) Test bootstrapping is fragile
- The repository does not define a pytest configuration that injects the repo root into `sys.path`.
- Result: `ModuleNotFoundError: src_trainer` during test collection in a fresh environment.
- Risk: contributors and CI pipelines can fail before reaching real tests.

### 2) Environment reproducibility is under-specified
- Dependencies are declared in `pyproject.toml`, but local test instructions/tooling are not enforcing environment setup before running tests.
- Result: import-time failures (`ModuleNotFoundError: pydantic`) mask actual logic regressions.
- Risk: low signal-to-noise in CI and slower onboarding/debug cycles.

### 3) Scenario loading is all-or-nothing
- `list_scenarios()` validates every JSON file and raises immediately on first invalid scenario.
- Result: one malformed scenario blocks all scenario loading.
- Risk: poor fault isolation when content grows.

### 4) Strict message matching may reject acceptable user inputs
- `_correctness_feedback` requires exact normalized string equality for expected values.
- Result: punctuation/order/spacing variants may be marked incorrect even if operationally acceptable.
- Risk: user frustration and overfitting training to exact strings rather than procedure intent.

### 5) Metadata auto-fill may hide content quality issues
- `Scenario.fill_training_metadata()` silently fills missing fields such as `required_assessment`, `correct_procedure`, and `final_explanation`.
- Result: scenarios can pass validation while still being incomplete from an instructional perspective.
- Risk: inconsistent pedagogical quality and weak content governance.

## Recommended RBS (risk-based sequencing) improvement plan

### RBS-1 (High risk / immediate)
1. Stabilize test invocation:
   - Add a pytest config (`[tool.pytest.ini_options]`) with `pythonpath = ["."]` or equivalent.
   - Add a documented one-command local setup (e.g., `uv sync` + `uv run pytest`).
2. Add a CI gate that runs tests in a clean environment.

### RBS-2 (High risk / short-term)
1. Harden scenario loading:
   - Wrap per-file validation to collect errors by filename.
   - Return valid scenarios plus structured diagnostics (or fail with aggregated error report).
2. Add tests for invalid scenario files to ensure error reporting quality.

### RBS-3 (Medium risk / short-term)
1. Improve phrase evaluation:
   - Introduce rule-based normalization/token checks for `SPEAK_PHRASE`.
   - Separate "critical keywords required" from "exact phrase preferred".
2. Add parametrized tests with realistic phrasing variants.

### RBS-4 (Medium risk / medium-term)
1. Strengthen model validation:
   - Add explicit scenario quality checks (e.g., minimum learning objectives, non-empty steps, explicit objectives).
   - Keep autofill for UX but emit warnings/diagnostics when fallback defaults are used.

### RBS-5 (Lower risk / medium-term)
1. Add lightweight observability for simulator decisions:
   - Optional debug traces for action mismatch reasons and step transitions.
2. Capture anonymized mismatch patterns to improve hints and scenario wording.

## Suggested acceptance criteria for next iteration

- Tests run successfully from a clean clone with one documented command.
- Scenario validation errors are aggregated and actionable (file + field + message).
- At least 5 non-identical but valid phrase variants pass for each distress/urgency/safety scenario family.
- Content quality warnings are visible for scenarios relying on defaulted metadata.
