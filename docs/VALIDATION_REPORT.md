# Validation report | Synthetic identity matching challenge

## Test design

Fictional records only. Deterministic seed 20261115. Groups split by watchlist scenario-generator ID, not by random candidate pair. The fixed logistic-regression alert threshold was selected to maximise validation F1 on a predefined threshold grid. Performance below was then evaluated on the disjoint synthetic holdout without refitting or reselecting thresholds.

## Holdout evaluation

180 customer identities, of which 36 carry synthetic true-match labels and 144 are synthetic negatives.

| Approach | TP | FP | FN | TN | Precision | Recall | Alerts |
|---|---:|---:|---:|---:|---:|---:|---:|
| Exact name / alias | 29 | 20 | 7 | 124 | 59.18% | 80.56% | 49 |
| Fuzzy name (0.900) | 36 | 48 | 0 | 96 | 42.86% | 100.00% | 84 |
| Explainable ML (0.920) | 33 | 5 | 3 | 139 | 86.84% | 91.67% | 38 |

The ML approach also yielded an illustrative ROC-AUC of 0.994, an artificially high figure strongly conditioned by engineered synthetic features. The model results should never be used to estimate actual sanctions hit rates.

## Case types intentionally challenged

- **Exact identity link:** fictional person and reference share primary name and corroborating attributes.
- **Alias or typo identity link:** true synthetic link, while a name variant or missing identifier makes the comparison more difficult.
- **Near-name unrelated person:** a name variation can resemble a listed fictional entry even with no true relationship.
- **Same name, different identity:** name equality conflicts with identifiers; in some deliberately ambiguous examples, corroborating data is missing.
- **Unrelated background:** randomly assembled fictional identities that may coincidentally share name fragments.

## Key governance interpretation

Name-only methods demonstrate that a high-alert workload does not necessarily mean reliable identity resolution. The model performs better on these artificial cases largely because the scenarios are generated with distinguishing identifier patterns. This is a model demonstration, NOT evidence of successful sanctions compliance.

An alert classified against the customer-level synthetic label might still point to the **wrong reference record**. Separate wrong-record counters are included in the evaluation artifacts. The early top-five retrieval stage itself can fail to include the correct record; the downstream model cannot restore it.

## Required additional evidence before any operational use

1. Verifiable current official lists and change/provenance controls.
2. Regulatory analysis of persons, regimes, ownership/control, licensing and entity relationships.
3. Data protection assessment and authorised processing of actual customer data.
4. Independent realistic validation of both candidate retrieval and final identity adjudication.
5. Bias, transliteration, script coverage, adversarial and robustness testing.
6. Calibration and threshold governance for representative operational workloads.
7. Authenticated audit store, SSO/RBAC, monitoring, drift management and incident response.

## Automated evidence

Run `python -m pytest -q`. The repository includes **12** checks covering data determinism, blank-identifier handling, disjoint groups, additive explanation integrity, audit input validation, provenance hashes, stored model consistency and absence of official lists.

Static evaluation JSON is `artifacts/evaluation_metrics.json`; the CSV outputs can be independently inspected or rebuilt with `python -m scripts.build_assets`.
