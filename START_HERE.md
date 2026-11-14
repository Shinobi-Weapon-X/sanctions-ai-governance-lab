# START HERE | Project 02 in 15 straightforward steps

## What you have

A new, independent sanctions screening educational lab containing a Streamlit dashboard, working Python model, fictional identities, a downloadable review log, 12 automated tests, and a four-page case study.

**No real sanctions list or real customer is included. Do not use this application for actual screening.**

## First run on your Mac (optional, for technical validation)

1. Unzip the package.
2. Open the extracted `sanctions-ai-governance-lab` folder.
3. Open **Terminal** and `cd` into that folder (you can drag the folder from Finder into Terminal after typing `cd `).
4. Run `python3 --version`. Python 3.11 or 3.12 is recommended.
5. Run `python3 -m venv .venv`.
6. Run `source .venv/bin/activate`.
7. Run `pip install -r requirements.txt`.
8. Run `python -m pytest -q` and confirm that **12 tests pass**.
9. Run `streamlit run app.py` and open the shown localhost URL.

## Publish in a NEW GitHub repository

10. Open <https://github.com/new>. Name the repository `sanctions-ai-governance-lab`. Set it to Public only after reviewing the files. Do **not** replace your existing Financial Crime AI Governance Lab.
11. On your empty repository, click **uploading an existing file**.
12. Open the extracted project's inner folder and drag **its contents** into GitHub. Preserve all subfolders. Do not upload just the ZIP. On macOS, show `.streamlit` and `.gitignore` with **Command + Shift + .** if hidden.
13. Commit with message `Initial release of sanctions screening AI governance lab`.
14. In <https://share.streamlit.io>, choose **Deploy a public app from GitHub**, select the new repository, branch `main`, main file path `app.py`; no Secrets needed.
15. After it loads, test all five tabs and audit CSV. Add the exact public Streamlit URL under the title of `README.md` and to **About → Website** on GitHub.

## Quick walkthrough of the FIVE tabs

**Overview** — confirm 90 fictional watchlist entries, 900 fictional customers, and holdout alert workloads. The three approaches should have different false-positive workloads. Separate, side-by-side chart bars are used, not stacked probabilities.

**Screen Identity** — choose the scenario `same_name_conflicting_identifiers`. Select a customer, inspect the top five candidate entries and explain why identical names are not proof of the same person. Review the `identifier_conflict` and `year_conflict` columns. Download a sample candidate CSV.

**Validation** — confirm 540 training, 180 validation and 180 holdout customers, and inspect the false positives and missed matches. The holdout benchmark stays fixed even if you explore a counterfactual threshold.

**Human Review** — choose a customer, select **Request further information**, enter `Too short`, and confirm the application rejects the rationale. Enter the longer example below, click **Record simulated review decision**, and download your session audit CSV.

> The name resembles the fictional reference, but some identity attributes conflict or are missing. Additional verified identifiers would be required before any determination.

**AI Governance** — inspect the Evidence status column, confirm the source manifest is labeled fictional, and open OFAC / UN / UK / MAS / NIST links. These are official reference links, **not the app's data feed**.

## Before you post on LinkedIn

- Use the **four-page case study** under `docs/PROJECT_CASE_STUDY.pdf` to explain the premise, experiment, model challenge and governance conclusions.
- Add your new GitHub and Streamlit links; keep links to Project 01 as a separate previous project.
- State clearly that the dataset, risk labels, fictional watchlist and benchmark are simulated.
- Disclose AI coding assistance. Only claim independent technical work you have actually performed and can explain.
- Do not call the demo an operational sanctions detection tool or claim it screens designated people.

## If the public Streamlit deployment fails

Open **Manage app → Logs**. Confirm `app.py` is the selected entry point, `requirements.txt` is in the root, Python 3.12 is selected if available, and `artifacts/illustrative_match_model.joblib` and the CSVs were uploaded. Copy the specific error text for debugging.
