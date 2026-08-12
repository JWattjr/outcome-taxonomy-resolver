# Security model

## Threats addressed

- **Malicious leader:** validators independently re-fetch evidence and recompute consequential fields.
- **Prompt injection:** source text is bounded and explicitly treated as untrusted data.
- **Source outage and drift:** missing evidence fails closed; substantive validator disagreement prevents accepted consensus.
- **Premature resolution:** frozen UTC deadlines are checked deterministically before nondeterministic work.
- **Replay and double settlement:** terminal/idempotent state transitions prevent duplicate consequences.
- **Unsafe evidence URLs:** userinfo, private/internal hosts, literal private IPs, IPv6 literals, whitespace, and non-default ports are rejected.

## Contract-specific boundary

Validators independently classify each frozen criterion. Contract code—not the LLM—matches the exact ordered vector to mutually exclusive category conjunctions and an optional fallback.

`OPEN → WAIT/CONTESTED/RESOLVED/VOID`; missing or provisional evidence remains retryable, contradictions are explicit, and max-wait/cancellation are terminal.

## Residual risks

HTTPS reachability does not prove publisher authority. DNS rebinding remains possible without a deployment-specific domain allowlist. Dynamic sources can legitimately cause validator disagreement. LLM classifications can remain unresolved on ambiguous language. Downstream payout code is out of scope and must consume only finalized state with its own idempotency guard.
