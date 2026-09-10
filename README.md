# Outcome Taxonomy Resolver

Outcome Taxonomy Resolver is a standalone GenLayer Intelligent Contract for
turning messy public evidence into one outcome from a frozen taxonomy. It is
useful when validators must interpret documents or reports, while the final
category selection must remain deterministic and auditable.

## Why GenLayer is needed

The source documents are external and may be ambiguous, incomplete, or
inconsistent. The leader and validators independently fetch the frozen HTTPS
sources and classify every frozen criterion as SATISFIED, UNSATISFIED, or
UNKNOWN. Exact agreement is required on the canonical result. Deterministic
contract code—not a model—matches that vector to the frozen categories. A
conventional contract could store a user-supplied label, but it could not
independently interpret arbitrary public evidence at the state transition.

Evidence is treated as untrusted data. The prompt marks unavailable and
truncated material as incomplete and tells the model not to follow embedded
instructions or infer negative facts from it. This bounds the contract and
consensus boundary but does not guarantee real-model prompt-injection
resistance. An all-source outage deterministically forces WAIT; partial or
truncated evidence does not mechanically force WAIT when validators agree that
the remaining material is sufficient, but an insufficient criterion must stay
UNKNOWN. HTTPS, hostname, port, length, and public-IP checks constrain the
input; they do not prove publisher authority or prevent every network-level
attack.

## Frozen taxonomy and lifecycle

The constructor bounds and canonicalizes criteria, categories, requirements,
sources, timestamps, and JSON sizes. Criterion references must be typed,
known, unique, and non-contradictory. Requirement arrays are bounded. Fallback
categories are unconditional and there can be at most one. Every pair of
ordinary categories must be mutually exclusive.

OPEN can resolve to:

- RESOLVED with a uniquely matching ordinary category or a fallback after all
  required facts are known;
- WAIT before the cutoff, while evidence is provisional, or when an insufficient
  criterion remains unknown;
- CONTESTED for an authoritative conflict or a known vector with no category;
- VOID for cancellation or the deterministic maximum-wait boundary.

Before the cutoff no evidence is assessed. The cutoff is the earliest
assessment time, not a historical as-of guarantee for the documents. At or
after max_wait, the result is the terminal VOID / MAX_WAIT_EXPIRED state.
Terminal RESOLVED and VOID calls are idempotent and do not increase the
attempt count.

Every accepted consensus result has exactly these fields:
state, category_id, criterion_vector, reason_code, and source_coverage. The
same schema, exact types, enum checks, vector length, coverage bound, and
state/category/reason consistency are enforced on the leader result, the
independent result, and the value written to storage.

## Three-outcome example

NO_RESULT is an explicitly evidenced final disposition, not the absence of
evidence. For a proposal market, use three criteria and require the matching
criterion to be SATISFIED:

~~~json
{
  "criteria": [
    {"id":"passed","description":"An authoritative source records that the proposal passed."},
    {"id":"failed","description":"An authoritative source records that the proposal failed."},
    {"id":"no_final_disposition","description":"An authoritative source explicitly records that no final disposition occurred by the cutoff."}
  ],
  "categories": [
    {"id":"PASSED","label":"Passed","required_true":["passed"],"required_false":["failed","no_final_disposition"],"fallback":false},
    {"id":"FAILED","label":"Failed","required_true":["failed"],"required_false":["passed","no_final_disposition"],"fallback":false},
    {"id":"NO_RESULT","label":"No final disposition","required_true":["no_final_disposition"],"required_false":["passed","failed"],"fallback":false}
  ]
}
~~~

Consensus interprets the evidence; deterministic code applies this taxonomy.
An UNKNOWN required fact prevents a category from being selected, while an
unrelated UNKNOWN does not prevent a unique category match. If all facts are
known and none of the three explicitly evidenced dispositions matches, the
result is CONTESTED / NO_CATEGORY_MATCH rather than NO_RESULT.

## API and checks

Constructor arguments are market_id, question, categories, criteria, sources,
cutoff, max_wait, spec_id. Public methods are resolve() and get_state(). The
positional criterion_vector is in the frozen, alphabetically sorted
criteria_order; get_state() also returns an ID-keyed criterion_results mapping
so consumers cannot mistake constructor-input order for the frozen order. The
contract holds no funds; downstream payout code must consume only finalized
state and implement its own authorization and idempotency.

~~~powershell
$env:GENVM_VERSION = "v0.3.0-rc7"
genvm-lint check contracts/OutcomeTaxonomyResolver.py
python -m pytest tests -q
~~~

The direct suite uses offline, reproducible mocks and captured validator
execution. It cannot prove real-model prompt-injection resistance or every
possible live-network behavior. The current StudioNet deployment and finalized
resolve/read-back receipt are recorded in `deployments/studionet.json`.

## Deployment evidence

`deployments/studionet.json` is the current hardened-source record for commit
`474543505923cfa1008445046d9ad6788cc655f3`, including finalized deployment and
resolve receipts plus the read-back state. Independent read-only StudioNet RPC
verification on 2026-09-10 confirmed both receipts as FINALIZED with SUCCESS
execution, the manifest contract address, and the recorded `get_state()`.
The deployment was unanimous (5 AGREE); the resolve was MAJORITY_AGREE (3
AGREE, 2 DISAGREE), not unanimous. `gen_getContractCode` returned source whose
normalized UTF-8 SHA-256 is
`86697000c51a0c93b012c9f3a040feede2436501294616250dc2f4ae6e96bfd2`, matching
the local source and commit `4745435...`; this verifies source identity, not
EVM bytecode identity. `deployments/bradbury.json` remains a clearly marked
historical pre-hardening record and must not be presented as current evidence.

The configured GitHub origin returned HTTP 404 to unauthenticated public
requests, and the configured Explorer URL returned HTTP 503 on the same date.
GovInfo and the supplemental Congress report were reachable. Do not submit the
GitHub or Explorer links until those public evidence links resolve.
