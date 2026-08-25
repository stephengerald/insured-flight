from pathlib import Path
import json

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "insured_flight.py"
SDK = "v0.2.16"
PROMPT = "Independently assess an itinerary-disruption insurance claim"
RULES = "TIER_1 covers an arrival delay of 120 to 239 minutes. TIER_2 covers 240 or more minutes or one canceled leg with same-day rerouting. TIER_3 covers a canceled trip or documented overnight missed connection. Otherwise NO_COVERAGE. Missing scheduled and actual times is UNCLEAR."


def deploy(vm, direct_deploy, alice):
    vm.sender = alice
    return direct_deploy(str(CONTRACT), "Connection Care", RULES, sdk_version=SDK)


def issue(contract, bob):
    contract.issue_policy("P-001", "0x" + bob.hex(), "Leg 1 NW101 Harbor to Mesa scheduled 08:00-10:00; leg 2 NW220 Mesa to Pine scheduled 11:00-13:00 on 25 August 2026.", "Covers both listed legs and a missed connection caused by a covered delay; excludes voluntary changes and missing travel records.")


def test_policyholder_claim_and_acceptance(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    issue(contract, direct_bob)
    direct_vm.sender = direct_bob
    contract.file_claim("P-001", "NW101 arrived at 14:20 instead of 10:00. NW220 was missed and the traveler was rerouted the same day, arriving Pine at 18:00.", "Arrival was five hours late after the covered first-leg delay caused the listed connection to be missed.")
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "TIER_2"}))
    contract.review_claim("P-001")
    contract.accept_provisional_result("P-001")
    assert contract.get_policy_record("P-001")["state"] == "FINAL"
    assert contract.get_policy_record("P-001")["entitlement_tier"] == 2
    leader = direct_vm._captured_validators[-1][0]
    assert direct_vm.run_validator(leader_result=leader) is True


def test_issuer_challenge_gets_independent_final_review(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    issue(contract, direct_bob)
    direct_vm.sender = direct_bob
    contract.file_claim("P-001", "The holder record says NW101 arrived at 12:30 and the second leg was boarded normally at a revised gate.", "The holder claims a delay exceeding two hours.")
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "TIER_1"}))
    contract.review_claim("P-001")
    direct_vm.sender = direct_alice
    contract.challenge_claim("P-001", "The issuer counter-record confirms a 90-minute arrival delay and shows the original connection departed after the holder boarded it.")
    direct_vm.clear_mocks()
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "NO_COVERAGE"}))
    contract.reconsider_challenged_claim("P-001")
    assert contract.get_policy_record("P-001")["claim_result"] == "NO_COVERAGE"
    assert contract.get_policy_record("P-001")["issuer_challenge_used"] is True


def test_holder_identity_and_bad_model_result_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    issue(contract, direct_bob)
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("only_policyholder"):
        contract.file_claim("P-001", "An unrelated travel record must not be attached to another person's issued policy or start its claim workflow.", "An unrelated account claims a disruption.")
    direct_vm.sender = direct_bob
    contract.file_claim("P-001", "NW101 arrived at 14:20 instead of 10:00 and caused the listed same-day connection to be missed.", "The traveler arrived more than four hours late after the missed connection.")
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "PAY_ALL"}))
    with direct_vm.expect_revert("invalid_claim_result"):
        contract.review_claim("P-001")
    assert contract.get_policy_record("P-001")["state"] == "CLAIM_FILED"

