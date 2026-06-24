# Changelog

## [Unreleased]
### Added
- V3-A connector adapter contract with fake providers, source snapshots, evidence
  JSONL, approval artifact validation, and source-safety quarantine.
- V3-A audits for connector adapters, approval artifacts, snapshot integrity, and
  no-scheduler proof.

## [0.2.0-alpha.1] - 2026-06-24
### Added
- First-run checkpoint protocol with strong spec validation, runtime policy gates,
  checkpoint folders, deterministic verifiers, runtime golden cases, and maker/checker
  review enforcement.
- Beginner and advanced golden cases for plain-language loop starts and concrete loop
  diagnosis.
- V2 alpha eval suites for conversation routing, design quality, advanced improvement,
  local operator runtime, connector policy placeholders, and source-safety red-team cases.
- Safe install dry-run mode for Claude and Codex release smoke checks.

### Changed
- README and skills now describe the supervised V2 alpha boundary: local/read-only first
  passes, approval-gated external actions, and no scheduler or real connector execution.
- `doctor.sh` now runs the full V1/V2 gate.

## [0.1.0] - 2026-06-22
### Added
- Initial public release: loop-doctor and loop-builder skills.
- Artifact-first README with real tool output, honest limits, and attribution.
- Local gate confirmed: 12 pytest tests pass, audit_kit 4/4, SCRUB CLEAN.
