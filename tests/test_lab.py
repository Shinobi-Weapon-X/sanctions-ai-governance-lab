"""Fast automated checks for synthetic matching lab."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import joblib

from src.synthetic import generate
from src.matching import FEATURES, normalise, pair_features, candidate_pairs, explain
from src.evaluation import (split_customers, fit_model, score_pairs,
                             evaluate_holdout, choose_threshold, customer_results, stats)
from src.governance import review_form_error

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    return generate()


def test_dataset_is_reproducible_and_fictional():
    w1,c1=fixture()
    w2,c2=fixture()
    pd.testing.assert_frame_equal(w1,w2)
    pd.testing.assert_frame_equal(c1,c2)
    assert len(w1)==90 and len(c1)==900
    assert c1.ground_truth_match.sum()==180
    assert w1['source'].str.contains('FICTIONAL').all()
    assert c1['data_origin'].eq('SYNTHETIC ONLY').all()
    assert w1.watchlist_id.is_unique
    assert c1.customer_id.is_unique


def test_normalise_and_alias():
    assert normalise('  VÈRÌDÍÁN   LTD. ') == 'veridian ltd'
    assert normalise(None) == ''
    assert normalise('N.O.V.E.R.A') == 'n o v e r a'


def test_missing_identifiers_cannot_be_false_agreement():
    w,c=fixture()
    test=c.iloc[1].copy()
    test['identifier']=''
    feat=pair_features(test,w.iloc[0])
    assert feat['identifier_agreement']==0
    assert feat['identifier_conflict']==0


def test_true_and_false_scenarios_are_distinct():
    w,c=fixture()
    pos=c[c.scenario=='simulated_true_exact']
    neg=c[c.scenario=='same_name_conflicting_identifiers']
    assert len(pos)==len(neg)==90
    assert pos.ground_truth_match.eq(1).all()
    assert neg.ground_truth_match.eq(0).all()


def test_candidate_retrieval_count_and_labels():
    w,c=fixture()
    pairs=candidate_pairs(c.head(10),w,top_k=5)
    assert len(pairs)==50
    assert pairs.groupby('customer_id').size().eq(5).all()
    assert set(FEATURES).issubset(pairs.columns)
    assert pairs.true_pair.isin([0,1]).all()


def test_scenario_group_splits_are_disjoint():
    _,c=fixture()
    train,val,test=split_customers(c)
    t,v,z=(set(x.group_watchlist_id) for x in (train,val,test))
    assert t.isdisjoint(v) and t.isdisjoint(z) and v.isdisjoint(z)
    assert sum(map(len,(train,val,test))) == len(c)


def test_model_explanations_reconstruct_log_odds():
    w,c=fixture()
    pairs=candidate_pairs(c.head(80),w,top_k=5)
    model=fit_model(pairs,c.head(80).customer_id)
    feat=pairs.iloc[0]
    contribution=explain(model,feat)
    x=pairs.iloc[[0]][FEATURES]
    expected=float(model.decision_function(x)[0])
    actual=float(model.named_steps['logit'].intercept_[0]+contribution.log_odds_effect.sum())
    assert abs(expected-actual)<1e-8


def test_audit_rationale_rules():
    assert '20 characters' in review_form_error('Reviewer','Too short')
    assert 'pseudonym' in review_form_error('','Detailed synthetic investigation review rationale here.')
    assert review_form_error('Demo reviewer','Detailed synthetic investigation review rationale here.')==''


def test_frozen_holdout_counts_and_threshold():
    m=json.loads((ROOT/'artifacts'/'evaluation_metrics.json').read_text())
    assert m['split_customer_counts']=={'training':540,'validation':180,'test':180}
    assert 0 < m['validation_selected_ml_threshold'] <= 1
    for method in ['ml','exact','fuzzy']:
        scores=m['holdout'][method]
        assert sum(scores[k] for k in ['tp','fp','fn','tn'])==180
        assert scores['alerts']==scores['tp']+scores['fp']


def test_generated_manifest_hashes():
    manifest=json.loads((ROOT/'artifacts'/'source_manifest.json').read_text())
    assert manifest['provenance'].startswith('GENERATED FICTIONAL')
    for filename, sha in manifest['source_files_sha256'].items():
        assert hashlib.sha256((ROOT/'data'/filename).read_bytes()).hexdigest()==sha


def test_public_assets_exclude_official_list_files():
    assert not any('ofac' in f.name.lower() or 'un_sanction' in f.name.lower()
                   for f in (ROOT/'data').iterdir())
    assert (ROOT/'artifacts'/'illustrative_match_model.joblib').is_file()


def test_generated_scoring_model_matches_artifacts():
    model=joblib.load(ROOT/'artifacts'/'illustrative_match_model.joblib')
    pairs=pd.read_csv(ROOT/'artifacts'/'all_candidate_pairs.csv')
    sample=pairs.head(20)
    assert np.allclose(model.predict_proba(sample[FEATURES])[:,1],sample.ml_score,atol=1e-7)
