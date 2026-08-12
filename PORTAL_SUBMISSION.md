# GenLayer Portal submission

**Contribution type:** Builder → Intelligent Contracts
**Title:** Outcome Taxonomy Resolver
**Contribution date:** August 12, 2026

## Notes / Description

Built and deployed an MIT-licensed Outcome Taxonomy Resolver for reusable multi-outcome prediction markets. Deployment freezes criterion definitions, mutually exclusive category conjunctions, optional fallback, official HTTPS sources, cutoff, maximum wait, and spec ID. Validators independently re-fetch evidence and agree on an exact ordered criterion vector; deterministic contract code selects the category, so an LLM cannot invent a payout label. The constructor rejects satisfiable overlaps between non-fallback categories. Missing evidence stays WAIT, authoritative conflict becomes CONTESTED, and cancellation/max-wait becomes VOID. Includes pinned GenVM source, overlap and malicious-leader tests, full schema validation, security audit, test matrix, and finalized StudioNet deployment/consensus evidence. It does not custody market funds.

## Evidence to add

1. GitHub Repository — https://github.com/JWattjr/outcome-taxonomy-resolver
2. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/contracts/OutcomeTaxonomyResolver.py
3. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/tests/test_outcome_taxonomy.py
4. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/docs/SECURITY_AUDIT.md
5. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/docs/TEST_MATRIX.md
6. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/deployments/studionet.json
7. GitHub File — https://github.com/JWattjr/outcome-taxonomy-resolver/blob/main/deployments/bradbury.json
8. GenLayer Explorer Contract — https://explorer-bradbury.genlayer.com/address/0xB7F1EE00f561994133D3A7CF481B7666Fdb916dE

The repository is private. Grant Portal reviewers repository access before submission.
