# Model card | Explainable sanctions candidate ranking

**Model status** Educational prototype only. **Not suitable for real sanctions screening.**

## Intended purpose

Compare candidate identity matching approaches in a purely fictional sanctions-style setting. Create traceable numerical explanations, expose false-positive and missed-match trade-offs, support a simulated human adjudication workflow and document missing governance controls.

## Dataset and provenance

90 invented watchlist entries; 900 fictional customer identities; 180 synthetic true-identity links; 4,500 top-five name similarity candidate pairs. The synthetic labels are assigned by the generator before record attributes are sampled. They are **not independent verification of sanctions status**. Names and list regimes are imaginary. Country abbreviations are used as attributes, not as legal jurisdiction determinations.

**Saved model compatibility:** the included `joblib` artifact was produced with scikit-learn 1.8.0; use pinned `requirements.txt` or rebuild assets with the locally installed version. Never deserialize an untrusted file.

## Architecture

1. Normalise Latin-script names and candidate aliases.
2. Retrieve the five most name-similar fictional reference entries for each customer.
3. Compute eleven comparison features including name similarity, token overlap, exact aliases, entity type, birth year, country and identifier agreement/conflict.
4. Train a StandardScaler + class-weighted logistic regression pair classifier.
5. Select a single alert threshold on a validation partition.
6. Rank candidates by score and compare against exact and fuzzy baselines on the held-out partition.

## Split protocol

**540 training / 180 validation / 180 test customers**, grouped by the fictional reference scenario-generator ID. Related scenarios from the same generated reference do not cross partitions. The full reference registry remains available for retrieval in all partitions, which is appropriate for fixed-list candidate retrieval but not a real deployment design.

## Frozen synthetic holdout results

| Metric | Exact | Fuzzy | Explainable ML |
|---|---:|---:|---:|
| Alerts | 49 | 84 | 38 |
| Precision | 59.18% | 42.86% | 86.84% |
| Recall | 80.56% | 100.00% | 91.67% |
| False positives | 20 | 48 | 5 |
| False negatives | 7 | 0 | 3 |
| F1 | 68.24% | 60.00% | 89.19% |

The ML alert threshold **0.920** was chosen on validation. Fuzzy uses **0.900**; exact is equality. ML customer-level ROC-AUC is approximately **0.994**, a result made artificially high by seeded synthetic correlations and NOT predictive of actual screening efficacy.

## Explainability

The feature attribution table provides each standardised feature's exact contribution to logistic regression **log-odds**, plus an intercept. It is not a causal explanation. Scores are not calibrated probabilities of being sanctioned, and model explanations can encourage overconfidence in artificial scenarios.

## Human oversight

A screening alert opens a review workflow, not an automatic identity match. Reviewers can record evidence and select escalation, request for information, no confirmed match or false positive. Decisions are stored only in the active Streamlit session and can be exported as CSV. No real case management, immutable logging, sanctions blocking, sanctions notification or legal determination is implemented.

## Known limitations

- Neither real watchlist data nor real customer records are ingested.
- Artificial labels are seeded and correlated with model features; random name prevalence is not representative of production screening.
- Candidate retrieval top-five can miss the correct entity and requires separate recall testing.
- Identifier tokens are fictional and not comparable to authentic legal identification systems.
- Coverage of non-Latin scripts, transliteration, alternate ordering and accent handling is limited.
- No jurisdiction-specific regulatory applicability, sanctions ownership/control, licence or exemptions assessment.
- No independent fairness assessment, bias testing, robustness stress test or production validation.
- No safeguards for real customer privacy, secure audit retention, access control, drift monitoring or list updates.

## Human governance decision required before any real adoption

Fresh, provenance-verified official lists, comprehensive legal assessment and control ownership, authorised customer processing, independent evaluation against representative real scenarios, sanctions specialists' review, and security/privacy implementation. None of these requirements is met by this demonstrator.
