# Submission: InsuredFlight

Project name: InsuredFlight

Repository: https://github.com/stephengerald/insured-flight

StudioNet contract: https://explorer-studio.genlayer.com/address/0x9Ab4F31CBEd80790e418509960775bb7af2E9eDc

Deployment transaction: https://explorer-studio.genlayer.com/tx/0x577afea7d17f76fc9e6d439dda1f927d222e83d10125bbf986edd81d2067c783

Intelligent transaction: https://explorer-studio.genlayer.com/tx/0x822df4fd4eee309575edebd64b9dbf56908228a2c8f539a98fb9f5107c14a364

Summary: Issues reusable itinerary policies and turns stored disruption evidence into bounded coverage-tier signals.

Why it is GenLayer-native: Validators interpret itinerary, policy terms, and claim evidence and return TIER_1, TIER_2, TIER_3, NO_COVERAGE, or UNCLEAR.

Evidence/source model: The deployed contract judges claimant-provided on-chain evidence; it does not fetch airline data. Authentic flight records must be supplied and verified by an external adapter in production.

Declared scope: Reusable, non-custodial prototype. Entitlement tiers are signals only. The contract holds no premium or payout funds and is not an insurance product or legal coverage determination.

Review evidence: `AUDIT.md`, `SECURITY.md`, `SOURCE_POLICY.md`, and `deployments/studionet.json` bind the reviewed source hash to the public live result.
