"""Reproducible, entirely fictitious watchlist and customer identity generator.

The 'watchlist' is not a governmental sanctions list and contains no asserted
real-world sanctions designations. Use only for educational testing.
"""
from __future__ import annotations

import random
from typing import Tuple
import pandas as pd

SEED = 20261115
GIVEN = [
    'Taren', 'Liora', 'Aven', 'Selin', 'Kiran', 'Vessa', 'Mariel', 'Narek',
    'Alira', 'Dalen', 'Sorin', 'Kavina', 'Renel', 'Orin', 'Avira', 'Ilyan',
    'Norven', 'Zarela', 'Emirin', 'Thalia', 'Varek', 'Nelia', 'Kaelen', 'Orena',
]
FAMILY = [
    'Veloran', 'Taverin', 'Mavrel', 'Daryen', 'Sorellan', 'Halvren',
    'Navorin', 'Keldran', 'Virelda', 'Orvellan', 'Falerin', 'Elvoret',
    'Nimarel', 'Baralen', 'Savelin', 'Corvanel', 'Delorin', 'Ravendor',
]
COMPANY_A = ['Veridian', 'Novera', 'Talvex', 'Alverin', 'Cordalis', 'Mavora',
             'Kestralyn', 'Virello', 'Teravon', 'Solvanta', 'Fenlora', 'Delmara']
COMPANY_B = ['Meridian', 'Maritime', 'Industrial', 'Ventures', 'Cargo',
             'Trading', 'Holdings', 'Logistics', 'Technologies', 'Commodities']
COUNTRIES = ['SG', 'AE', 'GB', 'IN', 'FR', 'MY', 'US', 'AU']
REGIMES = ['SIM-ALPHA', 'SIM-BETA', 'SIM-GAMMA']


def make_alias(name: str, is_org: bool) -> str:
    if is_org:
        return name.replace(' Limited', ' Ltd').replace(' Corporation', ' Corp')
    pieces = name.split(' ')
    if len(pieces) == 2:
        return f'{pieces[0][0]}. {pieces[1]}'
    return name


def mutate_name(name: str) -> str:
    """Fixed, readable one-character misspelling near the front of a name."""
    chars = list(name)
    for i in range(2, len(chars) - 1):
        if chars[i].isalpha() and chars[i+1].isalpha():
            chars[i], chars[i+1] = chars[i+1], chars[i]
            return ''.join(chars)
    return name


def generate(seed: int = SEED) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = random.Random(seed)
    watch = []
    used_names = set()
    for i in range(90):
        org = i >= 66
        if org:
            base = f'{COMPANY_A[(i-66) % len(COMPANY_A)]} {COMPANY_B[(i-66)//len(COMPANY_A) % len(COMPANY_B)]}'
            name = f'{base} {"Limited" if i % 2 else "Corporation"}'
        else:
            name = f'{GIVEN[i % len(GIVEN)]} {FAMILY[(i // len(GIVEN) + (i % 7)) % len(FAMILY)]}'
        if name in used_names:
            name += ' IV'  # deterministic collision guard
        used_names.add(name)
        watch.append({
            'watchlist_id': f'SIM-WL-{i+1:04d}',
            'primary_name': name,
            'aliases': make_alias(name, org),
            'entity_type': 'Organisation' if org else 'Individual',
            'birth_year': '' if org else str(rng.randint(1960, 2000)),
            'country': rng.choice(COUNTRIES),
            'identifier': f'SIM-TOKEN-{i+1:05d}',
            'simulated_regime': REGIMES[i % len(REGIMES)],
            'source': 'FICTIONAL REGISTRY - NOT AN OFFICIAL SANCTIONS LIST',
        })
    watch_df = pd.DataFrame(watch)
    customers = []
    seq = 1

    def add(source, name, scenario, true, *, birth=None, country=None, identifier=None):
        nonlocal seq
        customers.append({
            'customer_id': f'SIM-CU-{seq:05d}',
            'customer_name': name,
            'entity_type': source['entity_type'],
            'birth_year': birth if birth is not None else source['birth_year'],
            'country': country if country is not None else source['country'],
            'identifier': identifier if identifier is not None else source['identifier'],
            'scenario': scenario,
            'ground_truth_watchlist_id': source['watchlist_id'] if true else '',
            'ground_truth_match': int(true),
            'group_watchlist_id': source['watchlist_id'],
            'data_origin': 'SYNTHETIC ONLY',
        })
        seq += 1

    for i, w in watch_df.iterrows():
        # Positive matches in a synthetic world: exact and alias/typo variants.
        add(w, w.primary_name, 'simulated_true_exact', True)
        variant = w.aliases if i % 2 == 0 else mutate_name(w.primary_name)
        add(w, variant, 'simulated_true_variant', True,
            birth=(str(int(w.birth_year)+1) if (i % 9 == 0 and str(w.birth_year).isdigit()) else ('' if i % 3 == 0 else w.birth_year)),
            identifier='' if i % 4 != 0 else w.identifier)
        # Negative near-match: slightly similar names, no corroborating ID.
        add(w, mutate_name(w.primary_name), 'near_name_different_identity', False,
            birth=(w.birth_year if i % 3 == 0 else (str(int(w.birth_year)+7) if str(w.birth_year).isdigit() else '')),
            identifier='' if i % 3 == 0 else f'SIM-OTHER-{i+1:05d}')
        # Name collision: identical name, explicit independent identifier;
        # DOB intentionally conflicts when available.
        add(w, w.primary_name, 'same_name_conflicting_identifiers', False,
            birth=(w.birth_year if i % 7 == 0 else (str(int(w.birth_year)+9) if str(w.birth_year).isdigit() else '')),
            country=(w.country if i % 7 == 0 else COUNTRIES[(COUNTRIES.index(w.country)+2) % len(COUNTRIES)]),
            identifier=('' if i % 7 == 0 else f'SIM-CONFLICT-{i+1:05d}'))

    # Unrelated background cases. All remain fictional and are assigned a
    # scenario group for disjoint training / validation / test splitting.
    for j in range(540):
        idx = j % len(watch)
        w = watch[idx]
        org = j % 5 == 0
        if org:
            name = f'{COMPANY_A[(j+5) % len(COMPANY_A)]} {COMPANY_B[(j+4) % len(COMPANY_B)]} Partners'
        else:
            name = f'{GIVEN[(j+7) % len(GIVEN)]} {FAMILY[(j+9) % len(FAMILY)]}a'
        customers.append({
            'customer_id': f'SIM-CU-{seq:05d}',
            'customer_name': name,
            'entity_type': 'Organisation' if org else 'Individual',
            'birth_year': '' if org else str(rng.randint(1960, 2001)),
            'country': rng.choice(COUNTRIES),
            'identifier': f'SIM-BACKGROUND-{j+1:05d}',
            'scenario': 'unrelated_background',
            'ground_truth_watchlist_id': '',
            'ground_truth_match': 0,
            'group_watchlist_id': w['watchlist_id'],
            'data_origin': 'SYNTHETIC ONLY',
        })
        seq += 1
    customers_df = pd.DataFrame(customers)
    assert len(watch_df) == 90 and len(customers_df) == 900
    assert customers_df.ground_truth_match.sum() == 180
    return watch_df, customers_df


if __name__ == '__main__':
    w, c = generate()
    print(f'Fictional watchlist {len(w)} | fictional customers {len(c)} | labelled links {c.ground_truth_match.sum()}')
