"""Fixed split, trained candidate classifier, and threshold validation on synthetic identities."""
from __future__ import annotations

from collections import defaultdict
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, average_precision_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from .matching import FEATURES

DEFAULT_FUZZY_THRESHOLD = 0.90


def split_customers(customers: pd.DataFrame, seed: int = 20261115):
    """Split scenario-generating watchlist groups to avoid overlapping cases."""
    splitter = GroupShuffleSplit(n_splits=1, test_size=.40, random_state=seed)
    ix_train, ix_rest = next(splitter.split(customers, groups=customers.group_watchlist_id))
    train = customers.iloc[ix_train].copy()
    remain = customers.iloc[ix_rest].copy()
    rest_split = GroupShuffleSplit(n_splits=1, test_size=.50, random_state=seed+1)
    ix_val, ix_test = next(rest_split.split(remain, groups=remain.group_watchlist_id))
    return train, remain.iloc[ix_val].copy(), remain.iloc[ix_test].copy()


def fit_model(pairs: pd.DataFrame, train_ids) -> Pipeline:
    train = pairs[pairs.customer_id.isin(train_ids)]
    model = Pipeline([
        ('scale', StandardScaler()),
        ('logit', LogisticRegression(class_weight='balanced', max_iter=1000, random_state=24)),
    ])
    model.fit(train[FEATURES], train['true_pair'])
    return model


def score_pairs(pairs: pd.DataFrame, model) -> pd.DataFrame:
    scored = pairs.copy()
    scored['ml_score'] = model.predict_proba(scored[FEATURES])[:, 1]
    scored['fuzzy_score'] = scored['name_similarity'].clip(0,1)
    scored['exact_score'] = ((scored.exact_primary > 0) | (scored.exact_alias > 0)).astype(float)
    # This is not an empirical probability of being sanctioned.
    return scored


def top_candidates(scored_pairs: pd.DataFrame, method: str = 'ml') -> pd.DataFrame:
    key = {'ml':'ml_score', 'fuzzy':'fuzzy_score', 'exact':'exact_score'}[method]
    return (scored_pairs.sort_values(
        [key,'name_similarity','watchlist_id'], ascending=[False,False,True]
    ).drop_duplicates('customer_id', keep='first').copy())


def customer_results(customers: pd.DataFrame, scored_pairs: pd.DataFrame, method: str, threshold: float):
    top = top_candidates(scored_pairs, method)
    key = {'ml':'ml_score','fuzzy':'fuzzy_score','exact':'exact_score'}[method]
    cols = ['customer_id','watchlist_id',key, 'name_similarity', 'identifier_conflict', 'year_conflict']
    merged = customers.merge(top[cols], on='customer_id', how='left')
    merged['selected_score'] = merged[key].fillna(0)
    merged['alert'] = (merged.selected_score >= threshold).astype(int)
    merged['correct_record'] = (
        (merged.ground_truth_match == 1) & (merged.watchlist_id == merged.ground_truth_watchlist_id)
    ).astype(int)
    return merged


def stats(results: pd.DataFrame) -> dict:
    actual = results.ground_truth_match.astype(int)
    predicted = results.alert.astype(int)
    p, r, f1, _ = precision_recall_fscore_support(actual, predicted, average='binary', zero_division=0)
    tp = int(((actual == 1) & (predicted == 1)).sum())
    fp = int(((actual == 0) & (predicted == 1)).sum())
    fn = int(((actual == 1) & (predicted == 0)).sum())
    tn = int(((actual == 0) & (predicted == 0)).sum())
    wrong_record = int(((actual == 1) & (predicted == 1) & (results.correct_record == 0)).sum())
    return dict(precision=float(p), recall=float(r), f1=float(f1),
                tp=tp, fp=fp, fn=fn, tn=tn, alerts=int(predicted.sum()),
                wrong_record_alerts=wrong_record,
                correct_record_alerts=int(((actual == 1)&(predicted == 1)&(results.correct_record == 1)).sum()))


def choose_threshold(customers: pd.DataFrame, scored_pairs: pd.DataFrame):
    """Choose once on validation data; fixed grid avoids optimizing holdout."""
    candidates = np.linspace(.20, .98, 40)
    scored = []
    for t in candidates:
        m = stats(customer_results(customers, scored_pairs, 'ml', float(t)))
        scored.append((m['f1'], -m['alerts'], float(t)))
    scored.sort(reverse=True)
    return scored[0][2]


def evaluate_holdout(customers: pd.DataFrame, scored_pairs: pd.DataFrame, threshold: float):
    result = {}
    for method, t in [('exact',1.0),('fuzzy',DEFAULT_FUZZY_THRESHOLD),('ml',threshold)]:
        result[method] = stats(customer_results(customers, scored_pairs, method, t))
        result[method]['threshold'] = round(t,4)
    # Customer-level AUC is only illustrative, and does not measure legal status.
    scores = customer_results(customers, scored_pairs, 'ml', threshold)
    result['ml']['roc_auc'] = float(roc_auc_score(scores.ground_truth_match, scores.selected_score))
    result['ml']['average_precision'] = float(average_precision_score(scores.ground_truth_match, scores.selected_score))
    return result
