# Changes

## 0.1.1 — 2026-10-28

- Align all five axes: lower levels reduce discretionary effort; higher levels
  increase it, with level 3 preserving ordinary balanced behavior.
- Change `batch` from batch size to decomposition depth. Re-select non-default
  batch values when migrating. Optional checkpoints reject unversioned or
  mismatched semantic profiles instead of silently reinterpreting them.
- Apply profiles directly to reads, edits and checks. Persistence is explicitly
  optional; no state file or helper call is needed for activation.
- Add real-Codex behavioral and effort-direction measurements, retaining failed
  attempts and limitations. Token ordering is an expectation, not a guarantee.
- Repair the isolated-Python optional helper and validate usage accounting.

## 0.1.0 — 2026-10-28

Initial independent attention-layer prototype extracted from agent-workflows.
