# Architecture

## State machine

The issuer creates policies, each policyholder files one claim, consensus reviews the stored packet, and a bounded revision or issuer challenge can trigger reconsideration.

The relevant roles are program issuer and policyholder. Write methods enforce role, phase, uniqueness, and bounded-storage rules before any state transition.

## Consensus boundary

Validators interpret itinerary, policy terms, and claim evidence and return TIER_1, TIER_2, TIER_3, NO_COVERAGE, or UNCLEAR. The leader returns a small JSON schema; validators independently rerun the same decision function and accept only exact enum or bitmask values. Malformed model output raises a tagged model error and writes no decision.

## Deterministic boundary

Enrollment, authorization, commitments, counters, phase changes, caps, masks, and any score or credit arithmetic are deterministic contract logic. Only semantic interpretation of the stored evidence occurs inside `run_nondet_unsafe`.

## Off-chain boundary

Wallet custody, identity verification, indexing, notifications, private file storage, source authentication, money movement, legal process, and user-interface behavior are outside this repository. Entitlement tiers are signals only. The contract holds no premium or payout funds and is not an insurance product or legal coverage determination.
