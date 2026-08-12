# Outcome Taxonomy Resolver

A standalone GenLayer Intelligent Contract for multi-outcome markets whose frozen categories are selected deterministically from a validator-agreed criterion vector.

## GenLayer-native decision

Validators independently classify each frozen criterion. Contract code—not the LLM—matches the exact ordered vector to mutually exclusive category conjunctions and an optional fallback.

## Lifecycle and API

`OPEN → WAIT/CONTESTED/RESOLVED/VOID`; missing or provisional evidence remains retryable, contradictions are explicit, and max-wait/cancellation are terminal.

Constructor: `market_id, question, categories, criteria, sources, cutoff, max_wait, spec_id`. Public methods: `resolve()` and `get_state()`.

Every evidence URL is frozen, bounded, public HTTPS. Fetched text is untrusted input; prompts instruct validators to ignore embedded commands. Leader and validator closures snapshot ordinary values and independently re-fetch evidence.

## Live evidence

- [StudioNet contract](https://explorer-studio.genlayer.com/address/0x6711568eeE29CD3F8B4050Ac069d72211bDC104E)
- [Bradbury contract](https://explorer-bradbury.genlayer.com/address/0xB7F1EE00f561994133D3A7CF481B7666Fdb916dE)
- Exact StudioNet transaction hashes, constructor arguments, state, and execution results are in `deployments/studionet.json`.

## Verify

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/OutcomeTaxonomyResolver.py
python -m pytest tests -q
```

The contract uses a concrete pinned GenVM runner. See `docs/SECURITY_AUDIT.md`, `docs/TEST_MATRIX.md`, and `PORTAL_SUBMISSION.md` for reviewer evidence. This primitive does not custody funds; consumers must wait for GenLayer finality and remain idempotent.
