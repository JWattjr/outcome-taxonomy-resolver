# GenLayer Portal submission draft

Status: ready for Portal review. The hardened source is deployed and
independently verified on StudioNet, and every evidence link below returned
HTTP 200 in an anonymous public check on 2026-09-10.

Contribution type: Builder → Intelligent Contracts
Title: Outcome Taxonomy Resolver
Contribution date: 2026-09-10

## Notes / Description

Outcome Taxonomy Resolver is an MIT-licensed, standalone GenLayer primitive for
turning ambiguous public evidence into one result from a frozen multi-outcome
taxonomy. The constructor bounds and canonicalizes typed criteria, mutually
exclusive category conjunctions, an optional unconditional fallback, unique
HTTPS sources, timezone-aware cutoffs, maximum wait, and a spec ID. Validators
independently fetch and classify each criterion; an exact canonical result
schema is required on both sides. Deterministic contract code derives the
category, so a model cannot invent a payout label. Missing, provisional, or
truncated evidence is labeled incomplete. An all-source outage forces WAIT;
partial or truncated evidence can resolve only when both validators agree that
the remaining material is sufficient, and insufficient criteria remain
UNKNOWN. Conflicts are explicit; cancellation and maximum wait produce VOID.
The contract holds no funds and is intended to feed a finality-aware consumer.

The reviewed source includes bounded constructor inputs, exact-type and
state-consistency validation, adversarial direct tests, and a pinned GenVM
runner. The source commit is deployed and finalized on StudioNet. Deployment
reached 5/5 AGREE; the recorded resolve reached MAJORITY_AGREE with 3 AGREE
and 2 DISAGREE, followed by a successful read-back. This design does not
guarantee real-model prompt-injection resistance. The cutoff is the earliest
assessment time, not an enforced historical as-of evidence boundary.

## Current evidence

1. GitHub Repository — https://github.com/JWattjr/outcome-taxonomy-resolver
2. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/contracts/OutcomeTaxonomyResolver.py
3. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/tests/test_outcome_taxonomy.py
4. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/tests/test_nondet_storage.py
5. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/docs/SECURITY_AUDIT.md
6. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/docs/TEST_MATRIX.md
7. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/deployments/studionet.json
8. GenLayer Explorer Contract — https://explorer-studio.genlayer.com/contracts/0x095abFA6c2DD73Bb2a60786e283f82FD4e997cAa
9. Deployment transaction — https://explorer-studio.genlayer.com/transactions/0x7580aee999c75b217013f110375c9bb636d729a3bab619e2ac581e656ab795d5
10. Resolve transaction — https://explorer-studio.genlayer.com/transactions/0x52f2d38528aa1369b728514382aa1eee35ff3a02942e950852d7bf178d0da761
11. Source commit — https://github.com/JWattjr/outcome-taxonomy-resolver/commit/474543505923cfa1008445046d9ad6788cc655f3
12. Supplemental official Congress report — https://www.congress.gov/117/crpt/hrpt694/CRPT-117hrpt694.pdf

## Independent verification record (2026-09-10)

- Both recorded transactions returned `FINALIZED` with `SUCCESS` execution and
  the manifest contract address from read-only StudioNet RPC.
- `get_state()` matched the manifest: `RESOLVED`, `ENACTED`,
  `CATEGORY_MATCH`, source coverage `1`, and the recorded criterion mapping.
- `gen_getContractCode` returned source exactly matching the local source and
  commit `474543505923cfa1008445046d9ad6788cc655f3` after newline normalization.
  This verifies deployed source identity; it does not claim EVM bytecode
  identity.
- Anonymous public checks returned HTTP 200 for the repository/files, official
  Studio Explorer contract and transaction pages, GovInfo, and the supplemental
  Congress report.

Do not attach the old Bradbury deployment as current evidence.

## Three-outcome constructor demonstration

Use these arguments for an offline or fresh StudioNet demonstration of a
completed, named event. The ordinary categories are mutually exclusive and
deterministic; NO_RESULT requires an explicitly evidenced final disposition:

1. market_id: pl117-58-status-v2
2. question: What was the final official disposition of H.R. 3684 in the 117th Congress?
3. categories:

[
  {"id":"ENACTED","label":"Became law","required_true":["became_law"],"required_false":["failed_in_congress","no_final_disposition"],"fallback":false},
  {"id":"NOT_ENACTED","label":"Did not become law","required_true":["failed_in_congress"],"required_false":["became_law","no_final_disposition"],"fallback":false},
  {"id":"NO_RESULT","label":"No final disposition","required_true":["no_final_disposition"],"required_false":["became_law","failed_in_congress"],"fallback":false}
]

4. criteria:

[
  {"id":"became_law","description":"The official GovInfo record identifies H.R. 3684 as Public Law 117-58 with an approval date."},
  {"id":"failed_in_congress","description":"An authoritative congressional record explicitly states that H.R. 3684 failed or was rejected before enactment."},
  {"id":"no_final_disposition","description":"An authoritative record explicitly states that H.R. 3684 had no final disposition by the cutoff."}
]

5. sources: ["https://www.govinfo.gov/app/details/PLAW-117publ58/summary"]
6. cutoff: 2024-01-01T00:00:00Z
7. max_wait: 2027-01-01T00:00:00Z
8. spec_id: outcome-taxonomy-pl117-58-v2

The GovInfo Public Law 117-58 summary is a completed, public, authoritative
record and the cutoff is already past. HTTPS shape checks still do not prove
publisher authority. The current deployment record contains the exact
constructor JSON, source commit, finalized receipts, and read-back state.
