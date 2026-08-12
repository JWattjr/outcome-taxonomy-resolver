# Security and consensus audit: OutcomeTaxonomyResolver

Audit date: 2026-08-12
Scope: `contracts/OutcomeTaxonomyResolver.py`
Method: manual review, full GenVM lint and pinned-runner schema validation, direct-mode adversarial tests, explicit independent-validator execution, and finalized StudioNet receipt/state inspection.

## Result

No unresolved critical or high-severity code issue was found after remediation. The contract does not custody or transfer value.

## Remediated findings

| ID | Severity | Finding | Remediation |
| --- | --- | --- | --- |
| OT-01 | High | Overlapping category rules could make one fact vector match multiple payouts. | Reject every satisfiable overlap between non-fallback categories at deployment. |
| OT-02 | High | An LLM-selected category could escape frozen market semantics. | Consensus covers only criterion facts; contract code derives the category. |
| OT-03 | Medium | Unavailable sources could be mistaken for negative evidence. | Force WAIT with UNKNOWN criteria when every source is unavailable. |

## Verification

- Exact runner pin: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`.
- `genvm-lint check` passes AST and SDK schema validation.
- Direct tests exercise lifecycle, failure, and independent-validator paths.
- AST regression proves nondeterministic closures do not reference `self`.
- StudioNet deployment and consensus transaction are finalized with successful leader execution; exact evidence is in `deployments/studionet.json`.
- Bradbury is accepted only after successful execution and state reads, then finalized independently.

## Residual risk

See `SECURITY.md`. This is an engineering assessment, not formal verification, a financial guarantee, or legal advice.
