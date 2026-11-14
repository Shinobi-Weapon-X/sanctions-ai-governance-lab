"""Generate all fictional screening records and reproducible evaluation artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

import joblib
import pandas as pd
from src.synthetic import generate, SEED
from src.matching import candidate_pairs
from src.evaluation import (split_customers, fit_model, score_pairs,
                            choose_threshold, evaluate_holdout, customer_results)


def main():
    outdata, outartifacts = ROOT/'data', ROOT/'artifacts'
    outdata.mkdir(exist_ok=True)
    outartifacts.mkdir(exist_ok=True)
    wl, cu = generate()
    wl.to_csv(outdata/'fictional_watchlist.csv', index=False)
    cu.to_csv(outdata/'fictional_customers.csv', index=False)
    pairs = candidate_pairs(cu, wl, top_k=5)
    train, val, test = split_customers(cu)
    model = fit_model(pairs, train.customer_id)
    scored = score_pairs(pairs, model)
    scored.to_csv(outartifacts/'all_candidate_pairs.csv', index=False)
    val_pairs = scored[scored.customer_id.isin(val.customer_id)]
    test_pairs = scored[scored.customer_id.isin(test.customer_id)]
    threshold = choose_threshold(val, val_pairs)
    methods = evaluate_holdout(test, test_pairs, threshold)
    # CSV export is a static illustrative holdout prediction file. No real identities.
    for meth in ['ml', 'fuzzy', 'exact']:
        sub = customer_results(test, test_pairs, meth,
                               threshold if meth=='ml' else (1.0 if meth=='exact' else .9))
        sub[['customer_id','customer_name','scenario','ground_truth_match',
             'ground_truth_watchlist_id','watchlist_id','selected_score','alert',
             'correct_record']].to_csv(outartifacts/f'holdout_{meth}.csv',index=False)
    test_pair_list = test_pairs.sort_values(['customer_id','ml_score'],ascending=[True,False]).copy()
    test_pair_list.to_csv(outartifacts/'holdout_candidate_pairs.csv', index=False)
    joblib.dump(model, outartifacts/'illustrative_match_model.joblib')
    summary = {
        'dataset_type':'SYNTHETIC DEMONSTRATION - NO ACTUAL SANCTIONS LISTS OR REAL CUSTOMERS',
        'seed':SEED,
        'watchlist_records':int(len(wl)),
        'customer_records':int(len(cu)),
        'synthetic_positive_customers':int(cu.ground_truth_match.sum()),
        'candidate_pairs':int(len(pairs)),
        'split_customer_counts':{'training':len(train), 'validation':len(val),'test':len(test)},
        'split_group_counts':{'training':train.group_watchlist_id.nunique(),
                               'validation':val.group_watchlist_id.nunique(),
                               'test':test.group_watchlist_id.nunique()},
        'validation_selected_ml_threshold':round(threshold,4),
        'holdout':methods,
        'limitations':[
            'Artificial labels and seeded fictional names; not independently verified real-world outcomes',
            'Candidate retrieval restricted to top five name-similar reference records',
            'Score is a synthetic-scenario ranking output, not a probability of sanctions designation',
            'No official sanctions data ingestion, list update process, regulatory applicability assessment or legal decisioning',
            'No independent bias, robustness, adversarial, drift or production security validation',
        ],
    }
    (outartifacts/'evaluation_metrics.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    hashes = {}
    for f in (outdata/'fictional_watchlist.csv', outdata/'fictional_customers.csv'):
        hashes[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
    manifest = {
        'title':'Synthetic demonstration source manifest',
        'provenance':'GENERATED FICTIONAL RECORDS; NOT OFAC, UN, UK OR ANY GOVERNMENT LIST',
        'random_seed':SEED,
        'source_files_sha256':hashes,
        'update_frequency':'Rebuild manually; no automated official list refresh',
        'official_references_used_only_for_context':[
            'https://ofac.treasury.gov/sanctions-list-service',
            'https://main.un.org/securitycouncil/en/sanctions/un-sc-consolidated-list',
            'https://www.gov.uk/government/publications/the-uk-sanctions-list',
        ],
    }
    (outartifacts/'source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k!='limitations'},indent=2))
    return summary

if __name__ == '__main__':
    main()
