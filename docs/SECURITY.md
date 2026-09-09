# Security model

## Consensus boundary

The leader and validators independently classify the frozen criteria from
frozen source URLs. A strict canonicalization path requires the exact result
schema, exact value types, allowed enums, vector length, source-coverage
range, deterministic category derivation, and state/reason consistency. Exact
canonical dictionaries are compared; approximate agreement is not used.
Unchecked leader fields are never serialized into storage.

## Threats addressed

- Malicious leaders: validators re-fetch evidence and recompute every
  state-affecting result field.
- Prompt injection: source text is bounded and explicitly treated as untrusted
  data; embedded instructions cannot change deterministic taxonomy selection.
- Source outage and drift: transport failures and non-200 responses are
  unavailable; an all-source outage returns WAIT with UNKNOWN criteria.
- Partial or truncated evidence: incomplete material is labeled in the prompt;
  missing facts are not silently converted to UNSATISFIED. This is a
  validator-judgment boundary, not a blanket mechanical WAIT rule: if the
  remaining material is sufficient, validators may agree on FINAL and a
  resolved category; otherwise the affected criterion remains UNKNOWN and the
  contract stays WAIT.
- Premature resolution: frozen timezone-aware deadlines are checked
  deterministically before nondeterministic work.
- Replay and double settlement: terminal RESOLVED and VOID transitions return
  the existing state without increasing attempts.
- Unsafe evidence URLs: HTTPS, length, userinfo, private/internal hosts,
  malformed hostnames, non-default ports, and non-public IP literals are
  rejected.
- Taxonomy ambiguity: bounded typed requirements, duplicate/contradiction
  checks, one unconditional fallback, and satisfiable-overlap rejection keep
  category selection deterministic.

## Time and evidence semantics

The cutoff is the earliest assessment time. It is not a historical observation
cutoff; the contract does not prove that a fetched document reflects a past
state. At or after max_wait, the contract records VOID / MAX_WAIT_EXPIRED.
The URL validator constrains shape and reachability assumptions only; it does
not prove publisher authority, prevent DNS rebinding, or stop every
network-level attack.

`get_state()` exposes both the frozen alphabetic `criteria_order` and an
ID-keyed `criterion_results` mapping. The stored positional vector remains
canonical, but consumers have an explicit way to map each status to its
criterion ID.

## Residual risks

External documents can be ambiguous or change between validator fetches, so
consensus may remain contested or retryable. Offline mocks exercise schema and
state invariants but cannot prove real-model prompt-injection resistance.
Downstream consumers must wait for GenLayer finality and implement their own
authorization, payout, and idempotency guards. `deployments/studionet.json`
records the current hardened deployment; the Bradbury record remains
historical pre-hardening evidence.
