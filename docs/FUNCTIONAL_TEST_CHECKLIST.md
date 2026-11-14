# Manual functional and publication checklist

Mark `[x]` only when **you have personally observed** the expected result in the deployed application. Passing Python tests is not a substitute for browser verification.

## A. Overview

- [ ] 90 fictional list entries and 900 fictional customer identities display.
- [ ] Holdout contains 180 customers and the ML method produces 38 alerts.
- [ ] Bar chart shows **side-by-side** alert volume and false positives, not stacked percentage scores.
- [ ] The legal/production warning remains visible.

## B. Screen Identity

- [ ] Changing the scenario updates the customer selector.
- [ ] Selecting a fictional customer shows five candidate records.
- [ ] Inspecting one candidate displays name and identifier evidence and mathematically signed log-odds contributions.
- [ ] A name collision with conflicting identifiers is visible.
- [ ] A fictional candidate CSV downloads and opens.

## C. Validation

- [ ] Training, validation and test counts display as 540, 180 and 180.
- [ ] Threshold appears as 0.920 and the fixed ML test confusion matrix displays TP33 / FP5 / FN3 / TN139.
- [ ] The exact, fuzzy and model baselines show distinct alert burdens.
- [ ] Failure-case table and explicitly disclosed limitations are visible.
- [ ] The educational what-if threshold does not change the frozen published benchmark.

## D. Human Review

- [ ] Toggling 'model-flagged only' changes the selection table.
- [ ] A rationale shorter than 20 characters is rejected.
- [ ] A reviewer pseudonym shorter than two characters is rejected.
- [ ] A valid fictional decision adds a row with a UTC timestamp.
- [ ] The downloaded CSV contains customer ID, candidate watchlist ID, model score, reviewer, decision and rationale.
- [ ] A browser refresh/session reset does **not** falsely claim durable audit storage.

## E. AI Governance

- [ ] Twelve control domains and status/limitations appear.
- [ ] OFAC, UN, UK, MAS and NIST official reference links open.
- [ ] The manifest says `GENERATED FICTIONAL RECORDS` and never claims live data.
- [ ] The UK list transition is correctly described as of 28 January 2026.

## F. Public sharing

- [ ] In a separate unsigned browser window, the GitHub repository opens publicly.
- [ ] In a separate unsigned browser window, the deployed Streamlit app loads all tabs.
- [ ] No personal secrets, real identities or API keys appear in the repository.
- [ ] The README links to the **correct Project 02** Streamlit app, not Project 01.
- [ ] LinkedIn communications disclose fictional data and AI development assistance.

## Known limitations to mention in any showcase

Not an official list, not updated, no legal sanctions decision, no ownership/control or exemptions assessment, no production access control, no persistent signed audit log, no tested real-world fairness, drift or regulatory approval.
