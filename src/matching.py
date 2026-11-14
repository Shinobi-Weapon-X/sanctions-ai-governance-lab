"""Explainable candidate-matching features for a fictional sanctions registry.

Fuzzy matching and ML ranking are candidate-discovery tools, NOT legal
identification or sanctions status determinations.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Dict, List
import numpy as np
import pandas as pd
from rapidfuzz import fuzz

FEATURES = [
    'name_similarity', 'token_similarity', 'exact_primary', 'exact_alias',
    'type_match', 'year_agreement', 'year_conflict', 'country_agreement',
    'country_conflict', 'identifier_agreement', 'identifier_conflict',
]
LABELS = {
    'name_similarity': 'Character name similarity',
    'token_similarity': 'Name token similarity',
    'exact_primary': 'Exact primary name',
    'exact_alias': 'Exact known alias',
    'type_match': 'Entity type matches',
    'year_agreement': 'Birth year agreement',
    'year_conflict': 'Birth year conflict',
    'country_agreement': 'Country agreement',
    'country_conflict': 'Country conflict',
    'identifier_agreement': 'Identifier agreement',
    'identifier_conflict': 'Identifier conflict',
}


def normalise(value) -> str:
    if value is None or pd.isna(value):
        return ''
    s = unicodedata.normalize('NFKD', str(value)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]+', ' ', s.lower())).strip()


def alias_names(watch_row) -> List[str]:
    aliases = str(watch_row.get('aliases', '')).split('|')
    return [normalise(x) for x in [watch_row['primary_name'], *aliases] if normalise(x)]


def name_scores(customer_row, watch_row) -> Dict[str, float]:
    customer = normalise(customer_row['customer_name'])
    names = alias_names(watch_row)
    if not customer or not names:
        return {'name_similarity': 0.0, 'token_similarity': 0.0,
                'exact_primary': 0.0, 'exact_alias': 0.0}
    best = max(fuzz.ratio(customer, n) for n in names)
    token = max(fuzz.token_sort_ratio(customer, n) for n in names)
    return {
        'name_similarity': best / 100.0,
        'token_similarity': token / 100.0,
        'exact_primary': float(customer == normalise(watch_row['primary_name'])),
        'exact_alias': float(customer in names[1:]),
    }


def pair_features(customer_row, watch_row) -> Dict[str, float]:
    v = name_scores(customer_row, watch_row)
    v['type_match'] = float(str(customer_row['entity_type']) == str(watch_row['entity_type']))
    clean = lambda v: '' if v is None or pd.isna(v) else str(v).strip()
    cy, wy = clean(customer_row.get('birth_year', '')), clean(watch_row.get('birth_year', ''))
    co, wo = clean(customer_row.get('country', '')), clean(watch_row.get('country', ''))
    ci, wi = clean(customer_row.get('identifier', '')), clean(watch_row.get('identifier', ''))
    # Missing data is not falsely treated as an affirmative agreement or conflict.
    for prefix, left, right in [('year',cy,wy), ('country',co,wo), ('identifier',ci,wi)]:
        valid = bool(left and right)
        v[prefix + '_agreement'] = float(valid and left == right)
        v[prefix + '_conflict'] = float(valid and left != right)
    return v


def candidate_pairs(customers: pd.DataFrame, watchlist: pd.DataFrame, top_k: int = 5) -> pd.DataFrame:
    """Construct candidate pairs; name similarity retrieval is fixed, non-trained.

    top_k is a retrieval constraint and creates a measurable missed-candidate risk.
    """
    watches = [row for _, row in watchlist.iterrows()]
    rows = []
    for _, customer in customers.iterrows():
        # Rank by maximum character similarity to primary name or alias.
        retrieval = [(name_scores(customer, watch)['name_similarity'], n)
                     for n, watch in enumerate(watches)]
        retrieval.sort(key=lambda x: (-x[0], watches[x[1]]['watchlist_id']))
        for _, j in retrieval[:top_k]:
            watch = watches[j]
            features = pair_features(customer, watch)
            rows.append({
                'customer_id': customer.customer_id,
                'watchlist_id': watch.watchlist_id,
                'group_watchlist_id': customer.group_watchlist_id,
                'true_pair': int(bool(customer.ground_truth_watchlist_id) and
                                 customer.ground_truth_watchlist_id == watch.watchlist_id),
                **features,
            })
    return pd.DataFrame(rows)


def explain(model, features: pd.Series) -> pd.DataFrame:
    """Exact additive contributions to the log-odds for a scaler+logit pipeline."""
    scaler = model.named_steps['scale']
    clf = model.named_steps['logit']
    x = np.array([float(features[f]) for f in FEATURES])
    scaled = (x - scaler.mean_) / scaler.scale_
    terms = scaled * clf.coef_[0]
    result = pd.DataFrame({
        'factor': [LABELS[f] for f in FEATURES],
        'observed': x,
        'log_odds_effect': terms,
    }).sort_values('log_odds_effect', key=lambda v: v.abs(), ascending=False)
    return result.reset_index(drop=True)


def explain_identity_details(customer_row, watch_row) -> List[str]:
    """Plain-English corroboration and contradiction; not a legal conclusion."""
    feat = pair_features(customer_row, watch_row)
    out = []
    if feat['exact_primary'] or feat['exact_alias']:
        out.append('Name agrees with a fictional primary name or alias.')
    elif feat['name_similarity'] > .75:
        out.append('Name is similar but not identical to a fictional reference name.')
    else:
        out.append('Limited name similarity.')
    for label in ['identifier', 'year', 'country']:
        if feat[label+'_conflict']:
            out.append(f'{label.capitalize()} conflicts with the fictional reference record.')
        elif feat[label+'_agreement']:
            out.append(f'{label.capitalize()} agrees with the fictional reference record.')
    if not customer_row.get('identifier'):
        out.append('Customer identifier is absent, limiting corroboration.')
    return out
