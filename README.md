# InsuredFlight

Issues reusable itinerary policies and turns stored disruption evidence into bounded coverage-tier signals.

## Why GenLayer

Validators interpret itinerary, policy terms, and claim evidence and return TIER_1, TIER_2, TIER_3, NO_COVERAGE, or UNCLEAR.

## Reusable workflow

The issuer creates policies, each policyholder files one claim, consensus reviews the stored packet, and a bounded revision or issuer challenge can trigger reconsideration. Constructor parameters create a new independent instance, so the code is reusable; state is not shared between deployments.

The contract is deliberately non-custodial. It records a decision, entitlement, score, or approval signal and never transfers GEN.

## Evidence boundary

The deployed contract judges claimant-provided on-chain evidence; it does not fetch airline data. Authentic flight records must be supplied and verified by an external adapter in production.

## Verify locally

```powershell
genvm-lint check contracts/insured_flight.py
genvm-lint typecheck contracts/insured_flight.py
pytest tests/direct -q
python tests/run_glsim.py --validators 5
```

With GLSim running in another terminal:

```powershell
gltest tests/integration/test_glsim_consensus.py --network localnet -q
```

The live smoke test requires fresh test-only keys in `GENLAYER_PRIVATE_KEY`, `GENLAYER_SECONDARY_PRIVATE_KEY`. Never commit a `.env` file or use a production wallet.

```powershell
gltest tests/integration/test_studionet_smoke.py --network studionet -s -q --default-wait-interval=6000 --default-wait-retries=240
```

Use the documented 6-second StudioNet polling interval to stay comfortably below public endpoint limits.

See `ARCHITECTURE.md`, `SOURCE_POLICY.md`, `SECURITY.md`, `AUDIT.md`, and `deployments/studionet.json` for the review boundary and exact public evidence.
