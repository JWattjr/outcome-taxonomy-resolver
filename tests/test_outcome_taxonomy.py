import json

import pytest


DEFAULT_CRITERIA = [{"id": "launched", "description": "The official launch occurred"}]
DEFAULT_CATEGORIES = [
    {"id": "FULL", "label": "Full success", "required_true": ["launched"], "required_false": [], "fallback": False},
    {"id": "CANCELLED", "label": "Cancelled", "required_true": [], "required_false": ["launched"], "fallback": False},
]


def _args(
    categories=None,
    criteria=None,
    sources=None,
    cutoff="2030-01-01T00:00:00Z",
    max_wait="2030-02-01T00:00:00Z",
):
    return (
        "launch-1",
        "What happened to the launch?",
        json.dumps(DEFAULT_CATEGORIES if categories is None else categories),
        json.dumps(DEFAULT_CRITERIA if criteria is None else criteria),
        json.dumps(["https://official.example.org/launch"] if sources is None else sources),
        cutoff,
        max_wait,
        "taxonomy-v1",
    )


def _deploy(direct_deploy, **kwargs):
    return direct_deploy("contracts/OutcomeTaxonomyResolver.py", *_args(**kwargs))


def _mock_final(direct_vm, result, body="official launch record"):
    direct_vm.mock_web(r".*", {"status": 200, "body": body})
    direct_vm.mock_llm(r".*", json.dumps(result))


def test_resolves_category_from_frozen_vector_and_stores_exact_schema(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(
        direct_vm,
        {"evidence_state": "FINAL", "criterion_results": {"launched": "satisfied"}, "category_id": "INVENTED"},
    )
    result = contract.resolve()
    assert result == {
        "state": "RESOLVED",
        "category_id": "FULL",
        "criterion_vector": ["SATISFIED"],
        "reason_code": "CATEGORY_MATCH",
        "source_coverage": 1,
    }
    stored = json.loads(contract.get_state()["last_result"])
    assert set(stored) == {"state", "category_id", "criterion_vector", "reason_code", "source_coverage"}
    assert "INVENTED" not in contract.get_state()["last_result"]
    assert direct_vm.run_validator()


def test_validator_rejects_every_consensus_field_mutation_and_extra_key(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, {"evidence_state": "FINAL", "criterion_results": {"launched": "SATISFIED"}})
    accepted = contract.resolve()
    mutations = [
        {**accepted, "state": "WAIT"},
        {**accepted, "category_id": "CANCELLED"},
        {**accepted, "criterion_vector": ["UNSATISFIED"]},
        {**accepted, "reason_code": "NO_CATEGORY_MATCH"},
        {**accepted, "source_coverage": 0},
        {**accepted, "source_coverage": True},
        {**accepted, "reason_code": "X" * 12000},
        {**accepted, "unexpected": "stored later"},
        {key: value for key, value in accepted.items() if key != "reason_code"},
        ["not", "a", "result"],
    ]
    for mutation in mutations:
        assert direct_vm.run_validator(leader_result=mutation) is False


@pytest.mark.parametrize(
    "payload",
    [
        {"evidence_state": "FINAL", "criterion_results": {"launched": "SATISFIED", "extra": "UNKNOWN"}},
        {"evidence_state": "FINAL", "criterion_results": {}},
        {"evidence_state": "FINAL", "criterion_results": {"launched": True}},
        {"evidence_state": True, "criterion_results": {"launched": "UNKNOWN"}},
        {"evidence_state": "NOT_A_STATE", "criterion_results": {"launched": "UNKNOWN"}},
        [],
        "not-json",
    ],
)
def test_malformed_model_results_fail_closed(direct_vm, direct_deploy, payload):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r".*", {"status": 200, "body": "evidence"})
    response = payload if isinstance(payload, str) else json.dumps(payload)
    direct_vm.mock_llm(r".*", response)
    with direct_vm.expect_revert():
        contract.resolve()
    assert contract.get_state()["attempts"] == 0


def test_validator_rejects_malformed_wrappers(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, {"evidence_state": "FINAL", "criterion_results": {"launched": "SATISFIED"}})
    accepted = contract.resolve()
    for wrapper in (None, [], "not-json", {"calldata": accepted}):
        assert direct_vm.run_validator(leader_result=wrapper) is False


@pytest.mark.parametrize("timestamp_field", ["cutoff", "max_wait"])
def test_constructor_rejects_timezone_naive_timestamps(direct_vm, direct_deploy, timestamp_field):
    kwargs = {timestamp_field: "2030-01-15T00:00:00"}
    with direct_vm.expect_revert("timezone offset"):
        _deploy(direct_deploy, **kwargs)


def test_constructor_rejects_overlapping_nonfallback_categories(direct_vm, direct_deploy):
    categories = [
        {"id": "A", "label": "A", "required_true": ["launched"], "required_false": [], "fallback": False},
        {"id": "B", "label": "B", "required_true": ["launched"], "required_false": [], "fallback": False},
    ]
    with direct_vm.expect_revert("mutually exclusive"):
        _deploy(direct_deploy, categories=categories)


@pytest.mark.parametrize(
    "categories,message",
    [
        (
            [{"id": "OTHER", "label": "Other", "required_true": ["launched"], "required_false": [], "fallback": True}],
            "fallback categories cannot contain requirements",
        ),
            (
                [
                    {"id": "A", "label": "A", "required_true": [], "required_false": [], "fallback": True},
                    {"id": "B", "label": "B", "required_true": [], "required_false": [], "fallback": True},
                ],
            "at most one fallback",
        ),
        (
            [{"id": "A", "label": "A", "required_true": ["unknown"], "required_false": [], "fallback": False}],
            "unknown criterion",
        ),
        (
            [{"id": "A", "label": "A", "required_true": ["launched", "launched"], "required_false": [], "fallback": False}],
            "references must be unique",
        ),
        (
            [{"id": "A", "label": "A", "required_true": ["launched"], "required_false": ["launched"], "fallback": False}],
            "both required true and false",
        ),
        (
            [{"id": "A", "label": "A", "required_true": [1], "required_false": [], "fallback": False}],
            "references must be strings",
        ),
    ],
)
def test_constructor_rejects_unsafe_taxonomy_shapes(direct_vm, direct_deploy, categories, message):
    with direct_vm.expect_revert(message):
        _deploy(direct_deploy, categories=categories)


def test_constructor_bounds_requirement_arrays_and_raw_json(direct_vm, direct_deploy):
    criteria = [{"id": f"c{index}", "description": f"criterion {index}"} for index in range(16)]
    too_many = [{"id": "A", "label": "A", "required_true": [f"c{index}" for index in range(17)], "required_false": [], "fallback": False}]
    with direct_vm.expect_revert("requirements are too long"):
        _deploy(direct_deploy, categories=too_many, criteria=criteria)


def test_constructor_rejects_oversized_raw_taxonomy_json(direct_vm, direct_deploy):
    huge = [{"id": "A", "label": "x" * 16000, "required_true": ["launched"], "required_false": [], "fallback": False}]
    with direct_vm.expect_revert("JSON is too large"):
        _deploy(direct_deploy, categories=huge)


@pytest.mark.parametrize(
    "sources,message",
    [
        (["http://official.example.org/launch"], "HTTPS"),
        (["https://127.0.0.1/launch"], "publicly reachable"),
        (["https://official.example.org:8443/launch"], "default HTTPS port"),
        (["https://official.example.org/launch", "https://official.example.org/launch"], "source URLs must be unique"),
    ],
)
def test_constructor_rejects_unsafe_or_duplicate_sources(direct_vm, direct_deploy, sources, message):
    with direct_vm.expect_revert(message):
        _deploy(direct_deploy, sources=sources)


@pytest.mark.parametrize(
    "vector,expected_state,expected_category",
    [
        ({"a": "SATISFIED", "b": "SATISFIED"}, "RESOLVED", "AB"),
        ({"a": "UNSATISFIED", "b": "SATISFIED"}, "RESOLVED", "NOT_A_B"),
        ({"a": "SATISFIED", "b": "UNSATISFIED"}, "RESOLVED", "OTHER"),
        ({"a": "UNSATISFIED", "b": "UNSATISFIED"}, "RESOLVED", "OTHER"),
        ({"a": "UNKNOWN", "b": "SATISFIED"}, "WAIT", ""),
        ({"a": "UNKNOWN", "b": "UNSATISFIED"}, "WAIT", ""),
        ({"a": "SATISFIED", "b": "UNKNOWN"}, "WAIT", ""),
        ({"a": "UNSATISFIED", "b": "UNKNOWN"}, "WAIT", ""),
        ({"a": "UNKNOWN", "b": "UNKNOWN"}, "WAIT", ""),
    ],
)
def test_three_outcomes_are_deterministic_and_fallback_requires_known_facts(
    direct_vm, direct_deploy, vector, expected_state, expected_category
):
    criteria = [
        {"id": "a", "description": "A is true"},
        {"id": "b", "description": "B is true"},
    ]
    categories = [
        {"id": "AB", "label": "A and B", "required_true": ["a", "b"], "required_false": [], "fallback": False},
        {"id": "NOT_A_B", "label": "Not A and B", "required_true": ["b"], "required_false": ["a"], "fallback": False},
        {"id": "OTHER", "label": "Other", "required_true": [], "required_false": [], "fallback": True},
    ]

    contract = _deploy(direct_deploy, categories=categories, criteria=criteria)
    direct_vm.clear_mocks()
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, {"evidence_state": "FINAL", "criterion_results": vector})
    result = contract.resolve()
    assert result["state"] == expected_state
    assert result["category_id"] == expected_category
    if expected_state == "WAIT":
        assert result["reason_code"] == "CRITERION_UNKNOWN"


def test_unrelated_unknown_allows_unique_category_match(direct_vm, direct_deploy):
    criteria = [
        {"id": "launched", "description": "The launch occurred"},
        {"id": "unrelated", "description": "An unrelated fact"},
    ]
    categories = [
        {"id": "FULL", "label": "Full", "required_true": ["launched"], "required_false": [], "fallback": False},
        {"id": "NOT_FULL", "label": "Not full", "required_true": [], "required_false": ["launched"], "fallback": False},
    ]
    contract = _deploy(direct_deploy, categories=categories, criteria=criteria)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, {"evidence_state": "FINAL", "criterion_results": {"launched": "SATISFIED", "unrelated": "UNKNOWN"}})
    result = contract.resolve()
    assert result["state"] == "RESOLVED"
    assert result["category_id"] == "FULL"


def test_reordered_input_criteria_are_sorted_and_exposed_by_id(direct_vm, direct_deploy):
    criteria = [
        {"id": "b", "description": "Fact B"},
        {"id": "a", "description": "Fact A"},
    ]
    categories = [
        {"id": "A_ONLY", "label": "A only", "required_true": ["a"], "required_false": ["b"], "fallback": False},
        {"id": "B_ONLY", "label": "B only", "required_true": ["b"], "required_false": ["a"], "fallback": False},
    ]
    contract = _deploy(direct_deploy, criteria=criteria, categories=categories)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(
        direct_vm,
        {"evidence_state": "FINAL", "criterion_results": {"a": "SATISFIED", "b": "UNSATISFIED"}},
    )
    result = contract.resolve()
    assert result["category_id"] == "A_ONLY"
    assert result["criterion_vector"] == ["SATISFIED", "UNSATISFIED"]
    state = contract.get_state()
    assert state["criteria_order"] == ["a", "b"]
    assert state["criterion_results"] == {"a": "SATISFIED", "b": "UNSATISFIED"}


def test_partial_source_outage_stays_unknown_not_negative(direct_vm, direct_deploy):
    criteria = [
        {"id": "a", "description": "Fact A"},
        {"id": "b", "description": "Fact B"},
    ]
    categories = [
        {"id": "A", "label": "A", "required_true": ["a"], "required_false": [], "fallback": False},
        {"id": "NOT_A", "label": "Not A", "required_true": [], "required_false": ["a"], "fallback": False},
    ]
    contract = _deploy(
        direct_deploy,
        categories=categories,
        criteria=criteria,
        sources=["https://a.example.org/fact", "https://b.example.org/fact"],
    )
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r"a\.example\.org", {"status": 503, "body": "offline"})
    direct_vm.mock_web(r"b\.example\.org", {"status": 200, "body": "partial evidence"})
    direct_vm.mock_llm(r".*", json.dumps({"evidence_state": "FINAL", "criterion_results": {"a": "UNKNOWN", "b": "UNKNOWN"}}))
    result = contract.resolve()
    assert result["state"] == "WAIT"
    assert result["reason_code"] == "CRITERION_UNKNOWN"
    assert result["criterion_vector"] == ["UNKNOWN", "UNKNOWN"]
    assert result["source_coverage"] == 1


def test_partial_evidence_can_resolve_when_remaining_facts_are_sufficient(direct_vm, direct_deploy):
    criteria = [
        {"id": "a", "description": "An unrelated fact"},
        {"id": "b", "description": "The decisive fact"},
    ]
    categories = [
        {"id": "B_TRUE", "label": "B is true", "required_true": ["b"], "required_false": [], "fallback": False},
        {"id": "B_FALSE", "label": "B is false", "required_true": [], "required_false": ["b"], "fallback": False},
    ]
    contract = _deploy(
        direct_deploy,
        criteria=criteria,
        categories=categories,
        sources=["https://a.example.org/fact", "https://b.example.org/fact"],
    )
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r"a\.example\.org", {"status": 503, "body": "offline"})
    direct_vm.mock_web(r"b\.example\.org", {"status": 200, "body": "decisive evidence"})
    direct_vm.mock_llm(
        r".*",
        json.dumps(
            {
                "evidence_state": "FINAL",
                "criterion_results": {"a": "UNKNOWN", "b": "SATISFIED"},
            }
        ),
    )
    result = contract.resolve()
    assert result["state"] == "RESOLVED"
    assert result["category_id"] == "B_TRUE"
    assert result["source_coverage"] == 1


def test_transport_failure_stays_wait_with_unknowns(direct_vm, direct_deploy):
    criteria = [
        {"id": "a", "description": "Fact A"},
        {"id": "b", "description": "Fact B"},
    ]
    categories = [
        {"id": "A", "label": "A", "required_true": ["a"], "required_false": [], "fallback": False},
        {"id": "NOT_A", "label": "Not A", "required_true": [], "required_false": ["a"], "fallback": False},
    ]
    contract = _deploy(direct_deploy, categories=categories, criteria=criteria)
    direct_vm.warp("2030-01-15T00:00:00Z")
    result = contract.resolve()
    assert result["state"] == "WAIT"
    assert result["reason_code"] == "SOURCE_UNAVAILABLE"
    assert result["criterion_vector"] == ["UNKNOWN", "UNKNOWN"]


def test_truncated_evidence_is_marked_in_prompt_and_not_presented_as_complete(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r".*", {"status": 200, "body": "x" * 6001})
    direct_vm.mock_llm(
        r"SOURCE_TRUNCATED",
        json.dumps({"evidence_state": "FINAL", "criterion_results": {"launched": "UNKNOWN"}}),
    )
    result = contract.resolve()
    assert result["state"] == "WAIT"
    assert result["reason_code"] == "CRITERION_UNKNOWN"


def test_truncated_evidence_can_resolve_when_remaining_content_is_sufficient(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    body = "official launch record\n" + ("supporting detail\n" * 500)
    direct_vm.mock_web(r".*", {"status": 200, "body": body})
    direct_vm.mock_llm(
        r"SOURCE_TRUNCATED",
        json.dumps({"evidence_state": "FINAL", "criterion_results": {"launched": "SATISFIED"}}),
    )
    result = contract.resolve()
    assert result["state"] == "RESOLVED"
    assert result["category_id"] == "FULL"


def test_provisional_evidence_stays_retryable_wait(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, {"evidence_state": "PROVISIONAL", "criterion_results": {"launched": "SATISFIED"}})
    result = contract.resolve()
    assert result["state"] == "WAIT"
    assert result["category_id"] == ""
    assert result["reason_code"] == "EVIDENCE_PROVISIONAL"


def test_cancellation_is_an_explicit_terminal_state(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, {"evidence_state": "CANCELLED", "criterion_results": {"launched": "UNKNOWN"}})
    result = contract.resolve()
    assert result["state"] == "VOID"
    assert result["reason_code"] == "EVENT_CANCELLED"
    attempts = contract.get_state()["attempts"]
    assert contract.resolve()["state"] == "VOID"
    assert contract.get_state()["attempts"] == attempts


def test_resolved_replay_preserves_entire_state(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, {"evidence_state": "FINAL", "criterion_results": {"launched": "SATISFIED"}})
    contract.resolve()
    state_before = contract.get_state()
    result = contract.resolve()
    assert result == state_before
    assert contract.get_state() == state_before


def test_conflict_is_explicit_and_validator_agrees(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, {"evidence_state": "CONFLICT", "criterion_results": {"launched": "SATISFIED"}})
    result = contract.resolve()
    assert result["state"] == "CONTESTED"
    assert result["reason_code"] == "AUTHORITATIVE_CONFLICT"
    assert direct_vm.run_validator()


def test_before_cutoff_exact_cutoff_and_max_wait_boundaries_are_deterministic(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy, cutoff="2030-01-15T00:00:00Z", max_wait="2030-02-01T00:00:00Z")
    direct_vm.warp("2030-01-14T23:59:59Z")
    before = contract.resolve()
    assert before["state"] == "WAIT"
    assert before["reason_code"] == "BEFORE_CUTOFF"
    assert before["criterion_vector"] == []

    direct_vm.clear_mocks()
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, {"evidence_state": "FINAL", "criterion_results": {"launched": "SATISFIED"}})
    assert contract.resolve()["state"] == "RESOLVED"


def test_exact_max_wait_void_is_terminal_and_idempotent(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-31T23:59:59Z")
    just_before = contract.resolve()
    assert just_before["state"] == "WAIT"
    assert just_before["reason_code"] == "SOURCE_UNAVAILABLE"
    direct_vm.warp("2030-02-01T00:00:00Z")
    expired = contract.resolve()
    assert expired["state"] == "VOID"
    assert expired["reason_code"] == "MAX_WAIT_EXPIRED"
    attempts = contract.get_state()["attempts"]
    assert contract.resolve()["state"] == "VOID"
    assert contract.get_state()["attempts"] == attempts
