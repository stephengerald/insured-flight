from __future__ import annotations
import json
from pathlib import Path
from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

PROMPT = "Independently assess an itinerary-disruption insurance claim"


def context():
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {PROMPT: json.dumps({"result": "TIER_2"})}})
    return {"validators": [validator.to_dict() for validator in validators]}


def ok(receipt):
    assert tx_execution_succeeded(receipt)


def test_five_validator_policy_claim():
    issuer, holder = create_accounts(2)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "insured_flight.py")
    rules = "TIER_1 covers delays of 120 to 239 minutes. TIER_2 covers 240 or more minutes or a canceled leg with same-day rerouting. TIER_3 covers a canceled trip or overnight missed connection. Otherwise NO_COVERAGE; missing times is UNCLEAR."
    deployed = factory.deploy_contract_tx(args=["Connection Care", rules], account=issuer, wait_transaction_status=TransactionStatus.FINALIZED)
    ok(deployed)
    address = extract_contract_address(deployed)
    insurer = factory.build_contract(address, account=issuer)
    claimant = factory.build_contract(address, account=holder)
    itinerary = "Leg NW101 Harbor to Mesa scheduled 08:00-10:00; leg NW220 Mesa to Pine scheduled 11:00-13:00 on 25 August 2026."
    terms = "Covers both listed legs and a missed connection caused by covered delay; excludes voluntary changes and missing records."
    ok(insurer.issue_policy(args=["P-001", holder.address, itinerary, terms]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(claimant.file_claim(args=["P-001", "NW101 arrived at 14:20 instead of 10:00. NW220 was missed and same-day rerouting arrived Pine at 18:00.", "Arrival was five hours late after the covered first-leg delay caused the listed connection to be missed."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(claimant.review_claim(args=["P-001"]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    ok(claimant.accept_provisional_result(args=["P-001"]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert insurer.get_policy_record(args=["P-001"]).call()["entitlement_tier"] == 2

