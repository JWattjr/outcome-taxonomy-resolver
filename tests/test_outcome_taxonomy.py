import json


def _args(categories=None):
    return (
        "launch-1", "What happened to the launch?",
        json.dumps(categories or [
            {"id": "FULL", "label": "Full success", "required_true": ["launched"], "required_false": [], "fallback": False},
            {"id": "CANCELLED", "label": "Cancelled", "required_true": [], "required_false": ["launched"], "fallback": False},
        ]),
        json.dumps([{"id": "launched", "description": "The official launch occurred"}]),
        json.dumps(["https://official.example.org/launch"]),
        "2030-01-01T00:00:00Z", "2030-02-01T00:00:00Z", "taxonomy-v1",
    )


def test_resolves_category_from_frozen_vector(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/OutcomeTaxonomyResolver.py", *_args())
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r".*", {"status": 200, "body": "official launch record"})
    direct_vm.mock_llm(r".*", json.dumps({"evidence_state": "FINAL", "criterion_results": {"launched": "SATISFIED"}}))
    result = contract.resolve()
    assert result["category_id"] == "FULL"
    assert result["criterion_vector"] == ["SATISFIED"]
    assert direct_vm.run_validator()


def test_constructor_rejects_overlapping_nonfallback_categories(direct_vm, direct_deploy):
    categories = [
        {"id": "A", "label": "A", "required_true": ["launched"], "required_false": [], "fallback": False},
        {"id": "B", "label": "B", "required_true": ["launched"], "required_false": [], "fallback": False},
    ]
    with direct_vm.expect_revert("mutually exclusive"):
        direct_deploy("contracts/OutcomeTaxonomyResolver.py", *_args(categories))


def test_source_outage_stays_wait(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/OutcomeTaxonomyResolver.py", *_args())
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r".*", {"status": 503, "body": "offline"})
    assert contract.resolve()["state"] == "WAIT"
