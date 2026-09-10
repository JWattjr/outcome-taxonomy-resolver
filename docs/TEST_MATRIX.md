# Test matrix

All direct tests are offline and reproducible. The captured-validator tests
exercise the validator function directly; they do not emulate five live
validators or prove real-model behavior.

| Security or behavior invariant | Named test coverage |
| --- | --- |
| Exact five-key result schema and no unchecked storage fields | test_resolves_category_from_frozen_vector_and_stores_exact_schema; test_validator_rejects_every_consensus_field_mutation_and_extra_key |
| Every consensus field mutation rejected | test_validator_rejects_every_consensus_field_mutation_and_extra_key |
| Unexpected/missing keys, malformed model output, invalid enums, wrong types | test_malformed_model_results_fail_closed |
| Malformed validator wrappers are rejected before comparison | test_validator_rejects_malformed_wrappers |
| Boolean source coverage and headline/vector/reason consistency | test_validator_rejects_every_consensus_field_mutation_and_extra_key |
| Typed criteria and bounded raw JSON | test_constructor_bounds_requirement_arrays_and_raw_json; test_constructor_rejects_oversized_raw_taxonomy_json |
| Unknown/duplicate/contradictory category references | test_constructor_rejects_unsafe_taxonomy_shapes |
| Requirement-array bounds and one fallback | test_constructor_bounds_requirement_arrays_and_raw_json; test_constructor_rejects_unsafe_taxonomy_shapes |
| Satisfiable overlap rejection | test_constructor_rejects_overlapping_nonfallback_categories |
| Exhaustive small three-outcome vector behavior | test_three_outcomes_are_deterministic_and_fallback_requires_known_facts |
| Unknowns block fallback but unrelated unknowns permit a unique match | test_three_outcomes_are_deterministic_and_fallback_requires_known_facts; test_unrelated_unknown_allows_unique_category_match |
| Non-HTTPS/private/duplicate source rejection | test_constructor_rejects_unsafe_or_duplicate_sources |
| Complete outage, partial outage, and transport failure | test_partial_source_outage_stays_unknown_not_negative; test_transport_failure_stays_wait_with_unknowns |
| Partial evidence resolves only when remaining facts are sufficient | test_partial_evidence_can_resolve_when_remaining_facts_are_sufficient; test_partial_source_outage_stays_unknown_not_negative |
| Truncation is identified as incomplete evidence and is not an automatic WAIT | test_truncated_evidence_is_marked_in_prompt_and_not_presented_as_complete; test_truncated_evidence_can_resolve_when_remaining_content_is_sufficient |
| Provisional evidence, conflict, and cancellation | test_cancellation_is_an_explicit_terminal_state; test_conflict_is_explicit_and_validator_agrees; malformed-model tests |
| Before-cutoff, exact cutoff, just-before-max-wait, exact max-wait | test_before_cutoff_exact_cutoff_and_max_wait_boundaries_are_deterministic; test_exact_max_wait_void_is_terminal_and_idempotent |
| Terminal idempotency and attempt count | test_cancellation_is_an_explicit_terminal_state; test_exact_max_wait_void_is_terminal_and_idempotent; test_resolved_replay_preserves_entire_state |
| Timezone-naive timestamps are rejected | test_constructor_rejects_timezone_naive_timestamps |
| Constructor criterion order is frozen and exposed by ID | test_reordered_input_criteria_are_sorted_and_exposed_by_id |
| Consensus closures do not capture mutable storage | tests/test_nondet_storage.py::test_consensus_closures_do_not_capture_contract_storage |
| Recorded deployment shape | tests/integration/test_studionet.py and tests/integration/test_bradbury.py |

Run:

~~~powershell
$env:GENVM_VERSION = "v0.3.0-rc7"
genvm-lint check contracts/OutcomeTaxonomyResolver.py
python -m pytest tests -q
~~~

The StudioNet manifest test checks the current hardened source, recorded
finalized deployment/resolve receipt fields, and read-back state; it is not a
live receipt verification. Independent read-only RPC verification is recorded
in the audit and Portal draft. The Bradbury manifest remains historical. The
optional live StudioNet test can independently re-read the address when
`GENLAYER_INTEGRATION=1` is set.
