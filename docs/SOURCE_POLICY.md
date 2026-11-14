# Source policy | Fictional screening versus official sanctions data

## Distinguish a fictional watchlist from official designations

`data/fictional_watchlist.csv` contains invented names, aliases, synthetic identity tokens and simulated regimes. No record is asserted to be designated by any country, organisation or regulator. `data/fictional_customers.csv` also contains invented identities. **These files must never be described as official OFAC, UN, UK or MAS sanctions data**.

### Current official reference pages (viewed 15 November 2026)

- **OFAC Sanctions List Service** — <https://ofac.treasury.gov/sanctions-list-service>. Offers access to US SDN and Non-SDN list data, list search and downloadable data formats. Not downloaded or bundled.
- **UN Security Council Consolidated List** — <https://main.un.org/securitycouncil/en/sanctions/un-sc-consolidated-list>. Provides consolidated reference records in XML, HTML and PDF. Applicability of measures varies by regime. Not downloaded or bundled.
- **UK Sanctions List** — <https://www.gov.uk/government/publications/the-uk-sanctions-list>. The sole current source for UK sanctions designations since 28 January 2026. The older OFSI Consolidated List stopped being updated on that date. Not downloaded or bundled. Background guidance <https://www.gov.uk/guidance/moving-to-a-single-list-for-uk-sanctions-designations-28-january-2026>.
- **MAS Guidelines on AI Risk Management for Financial Institutions** — <https://www.mas.gov.sg/regulation/guidelines/guidelines-on-artificial-intelligence-risk-management-for-financial-institutions>, issued 7 October 2026 and effective 7 October 2027. Used only for governance context.
- **NIST AI Risk Management Framework** — <https://www.nist.gov/itl/ai-risk-management-framework>. Used only for control framing.

**Important:** Official sanctions sources differ by jurisdiction, legal scope, regime, restrictions, fields, updates and ownership/control rules. This lab does not implement those obligations or a real ingestion pipeline.

## Provenance manifest

`artifacts/source_manifest.json` records the synthetic generation seed, SHA256 hashes of the two source CSV files, explicit synthetic origin and list update limitation. A rebuild can be independently checked against the manifest.

## Future optional extension, not implemented

A future approved production-like reference ingestion proof of concept would need source-specific schemas, trusted signed downloads, source/record timestamps, update reconciliation, deletion and revision handling, country/regime applicability and legal review. It must not silently replace this demonstration dataset or claim live compliance coverage.

Do not upload real customer identities, confidential account data, passport numbers or proprietary screening results to this public repository or the public Streamlit app.
