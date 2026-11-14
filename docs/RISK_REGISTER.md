# AI governance and sanctions screening risk register

Illustrative research control register. The risk ratings are a qualitative exercise, not an enterprise risk acceptance decision.

| ID | Risk | Potential consequence | Inherent risk | Demonstrated response | Residual gap | Suggested owner |
|---|---|---|---|---|---|---|
| S01 | Similar or identical name misidentified as the same person | Unwarranted adverse treatment or investigation | High | Separate name similarity from birth year and identifier conflicts; human review | Robust verified-identifier process absent | Sanctions compliance |
| S02 | True match missed due to name variations or retrieval cap | Missed potential match | High | Alias support and missed-case reporting | Transliteration, multilingual coverage and recall benchmark unvalidated | Model risk |
| S03 | Artificial scores misread as sanctions probability | Overconfidence and automation bias | High | Prominent nonprobability warning, log-odds explanation and disclaimers | No human factors/usage monitoring | AI governance |
| S04 | Outdated or incomplete official list | Missed current designations | Critical | Synthetic manifest flags absence of live lists | No automated official data ingestion or refresh validation | Sanctions operations |
| S05 | Wrong jurisdiction, regime or designation interpretation | Incorrect legal decision or controls | Critical | All list references explicitly marked background only | No legal applicability engine or controls | Legal/compliance |
| S06 | Label leakage or synthetic overfitting | Misleadingly strong evaluation | High | Scenario-group split, heldout metrics, model card | Independent realistic validation required | Model validation |
| S07 | Adverse impact on protected or language groups | Unequal screening outcomes | High | None; explicitly flagged in governance matrix | Independent fairness and transliteration tests | AI ethics |
| S08 | Inaccurate or missing source identifiers | Misleading matches and unsupported decisions | High | Identifier/year/country comparison | Verified source documentation and evidence chaining | KYC operations |
| S09 | Insecure or mutable case records | Unreliable evidence, breaches and lack of accountability | High | Session CSV export | No immutable logs, retention, SSO, RBAC or encryption design | Information security |
| S10 | Unauthorised user submits actual PII | Privacy breach or unsuitable processing | High | UI warns to use fictional dataset only; no free-text name screening | No enterprise privacy controls | Data protection |
| S11 | Model deterioration after source/list updates | Increasing error rates | High | Fixed reproducible seed and source hashes | No change approval, drift or recalibration | Model operations |
| S12 | Misleading public claim about real sanctions performance | Reputational and professional misrepresentation | Medium | READMEs and PDF label all data simulated | Human author must verify claims before publication | Project author |

**No risk is formally accepted**. Actual use would require independent legal, sanctions, security, privacy and model risk assessment.
