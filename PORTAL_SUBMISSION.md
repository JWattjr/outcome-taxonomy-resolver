# GenLayer Portal submission draft

Status: ready for Portal review. The hardened source is deployed and finalized
on StudioNet; the receipt and read-back state are recorded below.

Contribution type: Builder → Intelligent Contracts
Title: Outcome Taxonomy Resolver
Contribution date: use the actual deployment/submission date

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
runner. The current source commit is deployed and finalized on StudioNet with
five validator votes and a successful resolve/read-back.

## Current evidence

1. GitHub Repository — https://github.com/JWattjr/outcome-taxonomy-resolver
2. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/contracts/OutcomeTaxonomyResolver.py
3. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/tests/test_outcome_taxonomy.py
4. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/tests/test_nondet_storage.py
5. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/docs/SECURITY_AUDIT.md
6. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/docs/TEST_MATRIX.md
7. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/deployments/studionet.json
8. GenLayer Explorer Contract — https://explorer-studio.genlayer.com/address/0x095abFA6c2DD73Bb2a60786e283f82FD4e997cAa
9. Deployment transaction — `0x7580aee999c75b217013f110375c9bb636d729a3bab619e2ac581e656ab795d5`
10. Resolve transaction — `0x52f2d38528aa1369b728514382aa1eee35ff3a02942e950852d7bf178d0da761`
11. Source commit — `474543505923cfa1008445046d9ad6788cc655f3`

Confirm that the repository is public and that every link resolves before
submission. Do not attach the old Bradbury deployment as current evidence.

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
