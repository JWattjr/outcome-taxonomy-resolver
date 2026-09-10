# Security and consensus audit: OutcomeTaxonomyResolver

Audit scope: contracts/OutcomeTaxonomyResolver.py
Review status: hardened source deployed and finalized on StudioNet. Independent
read-only RPC verification on 2026-09-10 confirmed the recorded receipts,
contract address, source identity, and read-back state. A subsequent anonymous
public-link check confirmed HTTP 200 responses for the repository, referenced
files, official Studio Explorer contract/transaction pages, GovInfo, and the
supplemental Congress report. The evidence packet is ready for Portal review.

## Boundary

The only nondeterministic input that can affect stored state is the canonical
result with exactly five fields: state, category_id, criterion_vector,
reason_code, and source_coverage. The leader and validator independently fetch
the same frozen source list and classify the same frozen criteria. Both results
pass exact key, type, enum, vector-length, coverage, and state/category/reason
checks and are compared as canonical dictionaries. The accepted value is
canonicalized again before any storage write.

Deterministic code derives categories from the criterion vector. Models cannot
invent categories, fallback requirements, or payout labels.

## Findings and remediations

| ID | Severity | Finding | Remediation |
| --- | --- | --- | --- |
| OT-01 | High | Accepted leader dictionaries could contain unchecked keys and later be serialized into storage. | Require the exact five-key result schema, canonicalize leader and independent results, and persist only the canonical value. |
| OT-02 | High | Python equality allowed booleans to compare equal to integers in consensus fields. | Require exact string/list/int types; source coverage rejects booleans and out-of-range values. |
| OT-03 | High | Category requirement arrays and fallback conditions were under-constrained. | Bound each array, require typed known references, reject duplicates/contradictions, reject fallback requirements, and retain one-fallback/overlap checks. |
| OT-04 | Medium | Category matching was duplicated and could drift. | Use one _taxonomy_category implementation for candidate derivation and result validation. |
| OT-05 | Medium | Web transport failures and truncated bodies were not explicit. | Treat exceptions and non-200 responses as unavailable; mark truncation in evidence and prompt; all-source outage returns WAIT with UNKNOWN criteria. |
| OT-06 | Medium | Tests did not cover malicious accepted output or lifecycle boundaries. | Add captured-validator mutation tests, malformed-model tests, taxonomy-shape tests, exhaustive small-vector cases, evidence failures, truncation, cancellation, idempotency, and cutoff/max-wait boundaries. |
| OT-07 | Medium | Consumers could misread a positional criterion vector after constructor input reordering. | Freeze criteria alphabetically and expose both `criteria_order` and an ID-keyed `criterion_results` view. |
| OT-08 | Low | Evidence completeness semantics could be overstated as an automatic WAIT rule. | Document that unavailable/truncated evidence is marked incomplete; only an all-source outage forces WAIT mechanically. Partial or truncated evidence may resolve when validators agree that the remaining material is sufficient, while insufficient facts remain UNKNOWN. Add sufficient and insufficient regression tests. |

## Checks performed

- Pinned runner header remains
  py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6.
- GenVM lint and SDK validation pass with the cached v0.3.0-rc7 toolchain.
- Offline direct tests exercise the named invariants in
  tests/test_outcome_taxonomy.py and closure isolation in
  tests/test_nondet_storage.py.
- The StudioNet integration manifest test checks the current hardened source,
  receipt fields, and read-back state recorded in the manifest; it is not a
  substitute for a live receipt query. Independent StudioNet RPC verification
  confirmed both transactions as FINALIZED with SUCCESS execution, matching
  contract address, and the recorded state. Deployment votes were 5 AGREE; the
  resolve was MAJORITY_AGREE with 3 AGREE and 2 DISAGREE. Bradbury remains a
  historical pre-hardening record.
- `gen_getContractCode` returned source that exactly matched the local source
  and source commit `474543505923cfa1008445046d9ad6788cc655f3` after newline
  normalization. This verifies source identity; no EVM bytecode identity claim
  is made for StudioNet.
- Public-link rechecks on 2026-09-10 returned HTTP 200 for the configured GitHub
  repository/files, official Studio Explorer contract/transaction pages,
  GovInfo, and the supplemental Congress report. The unavailable legacy
  Explorer URL was replaced with the live official Studio Explorer.

## Residual risks and limitations

HTTPS/hostname/public-IP checks are bounded URL-shape checks. They do not prove
publisher authority, eliminate DNS rebinding, or prevent all network attacks.
Documents and model output remain untrusted. Bounded prompts and deterministic
category derivation do not guarantee real-model prompt-injection resistance.
Mocked responses cannot prove that property. Partial or truncated evidence may still
yield a consensus result only when the validators agree that the remaining
material is sufficient and the deterministic taxonomy permits it; an unavailable
fact must never be treated as UNSATISFIED by this contract. If the material is
insufficient, the criterion remains UNKNOWN and resolution stays WAIT.
Downstream payout code, caller authorization, and finality handling are out of
scope.

The cutoff is the earliest assessment time. The contract does not enforce that a
document reflects a historical as-of state. At or after max_wait it records a
deterministic terminal VOID result. `deployments/studionet.json` is current
hardened-source evidence; `deployments/bradbury.json` remains a pre-hardening
historical record and must not be represented as current evidence.
