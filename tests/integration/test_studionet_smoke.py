import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address


def _ok(receipt):
    assert tx_execution_succeeded(receipt)
    return receipt


@pytest.mark.integration
def test_studionet_itinerary_claim(default_account, secondary_account):
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "insured_flight.py")
    rules = "TIER_1 covers delays of 120 to 239 minutes. TIER_2 covers 240 or more minutes or a canceled leg with same-day rerouting. TIER_3 covers a canceled trip or overnight missed connection. Otherwise NO_COVERAGE; missing times is UNCLEAR."
    deployed = _ok(factory.deploy_contract_tx(args=["Connection Care", rules], account=default_account, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    issuer = factory.build_contract(address, account=default_account)
    holder = factory.build_contract(address, account=secondary_account)
    itinerary = "Leg NW101 Harbor to Mesa scheduled 08:00-10:00; leg NW220 Mesa to Pine scheduled 11:00-13:00 on 25 August 2026."
    _ok(issuer.issue_policy(args=["P-001", secondary_account.address, itinerary, "Covers both listed legs and a missed connection caused by covered delay; excludes voluntary changes and missing records."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(holder.file_claim(args=["P-001", "NW101 arrived at 14:20 instead of 10:00. NW220 was missed and same-day rerouting arrived Pine at 18:00.", "Arrival was five hours late after the covered first-leg delay caused the listed connection to be missed."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    intelligent = _ok(holder.review_claim(args=["P-001"]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    record = issuer.get_policy_record(args=["P-001"]).call()
    assert record["claim_result"] in ("TIER_1", "TIER_2", "TIER_3", "NO_COVERAGE", "UNCLEAR")
    print("STUDIONET_RECORD=" + json.dumps({"address": address, "deploy_tx": deployed["hash"], "intelligent_tx": intelligent["hash"], "observed": record["claim_result"]}, sort_keys=True))
