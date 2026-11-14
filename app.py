"""Financial Crime AI Governance Lab 02 - synthetic sanctions matching demo.

Launch: streamlit run app.py
No actual sanctions designations, real customer data, or production decisions.
"""
from __future__ import annotations

from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
import json

import joblib
import pandas as pd
import streamlit as st

from src.matching import FEATURES, explain, explain_identity_details
from src.governance import review_form_error
from src.evaluation import stats, customer_results

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='Sanctions AI Governance Lab', page_icon='🛡️', layout='wide')

st.markdown('''
<style>
.block-container {padding-top: 1.8rem; max-width: 1440px;}
.hero-sub {color: #aabbd0; letter-spacing: .02em; margin-top: -.65rem;}
.small-note {color: #aabbd0; font-size: .85rem;}
div[data-testid="stMetric"] {background: #162439; border:1px solid #273950; border-radius: 12px; padding: 12px 14px;}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def load_data():
    watch = pd.read_csv(ROOT/'data'/'fictional_watchlist.csv', dtype=str, keep_default_na=False)
    customer = pd.read_csv(ROOT/'data'/'fictional_customers.csv', dtype=str, keep_default_na=False)
    customer['ground_truth_match'] = customer['ground_truth_match'].astype(int)
    pairs = pd.read_csv(ROOT/'artifacts'/'all_candidate_pairs.csv', dtype={'customer_id':str,'watchlist_id':str})
    metrics = json.loads((ROOT/'artifacts'/'evaluation_metrics.json').read_text(encoding='utf8'))
    manifest = json.loads((ROOT/'artifacts'/'source_manifest.json').read_text(encoding='utf8'))
    return watch, customer, pairs, metrics, manifest

@st.cache_resource
def load_model():
    # SECURITY: joblib is loaded from trusted assets bundled with this repo only.
    # Never allow arbitrary user uploads of model or pickle files.
    return joblib.load(ROOT/'artifacts'/'illustrative_match_model.joblib')

try:
    watch, customers, pairs, metrics, manifest = load_data()
    model = load_model()
except Exception as error:
    st.error('Required generated assets could not be loaded. Run `python -m scripts.build_assets` before deployment.')
    st.exception(error)
    st.stop()

if 'decisions' not in st.session_state:
    st.session_state.decisions = []

ML_THRESHOLD = float(metrics['validation_selected_ml_threshold'])

st.title('🛡️ Sanctions AI Governance Lab')
st.markdown('<p class="hero-sub">Lab 02 &nbsp; | &nbsp; Explainable identity matching, false positives and accountable human review</p>', unsafe_allow_html=True)
st.warning('FICTIONAL WATCHLIST AND CUSTOMERS ONLY. No real sanctions designations are bundled or screened. A match score is not a legal finding, verified identity, or a probability that someone is sanctioned.')

with st.sidebar:
    st.header('Lab 02')
    st.caption('An educational financial crime AI assurance portfolio project')
    st.divider()
    st.metric('Fictional watchlist entries', len(watch))
    st.metric('Fictional customer identities', len(customers))
    st.caption(f'Synthetic snapshot seed {metrics["seed"]}')
    st.divider()
    st.markdown('**About the controls**')
    st.caption('Scores assist with illustrative alert prioritisation. They cannot decide a sanctions designation or reporting obligation.')
    st.markdown('**Development transparency**')
    st.caption('Developed with AI coding and drafting assistance. Test results and design limitations are public in the repository.')

overview, screen, validation, review, gov = st.tabs([
    '📊 Overview', '🔍 Screen Identity', '⚖️ Validation', '👤 Human Review', '🛡️ AI Governance'
])

# A static holdout subset is used for transparent reporting. It must not be used
# to tune the frozen validation-selected ML threshold.
test_ids = set(pd.read_csv(ROOT/'artifacts'/'holdout_ml.csv')['customer_id'])
test = customers[customers.customer_id.isin(test_ids)].copy()
test_pairs = pairs[pairs.customer_id.isin(test.customer_id)].copy()

with overview:
    st.subheader('What can a similar name really tell us?')
    st.write('This lab studies the gap between **candidate discovery** and **identity verification**. Exact names and fuzzy similarity may create alerts, while conflicting identifiers can materially change an investigator’s assessment.')
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Fictional watchlist', len(watch))
    c2.metric('Synthetic customers', len(customers))
    c3.metric('Holdout cases', len(test))
    c4.metric('ML alerts on holdout', metrics['holdout']['ml']['alerts'])
    st.markdown('#### Three screening methods')
    methods = [
        {'Approach':'Exact name / alias', 'Description':'Literal normalised equality with primary name or alias; ignores corroborating identifiers'},
        {'Approach':'Fuzzy name', 'Description':'Character similarity, fixed 90% threshold; susceptible to name collisions'},
        {'Approach':'Explainable ML', 'Description':'Logistic regression combining name, identifier, birth year, country and entity type; threshold frozen on validation data'},
    ]
    st.dataframe(pd.DataFrame(methods),hide_index=True,use_container_width=True)
    st.markdown('#### Holdout alert workload')
    workload = pd.DataFrame([
        {'method':'Exact names', 'alerts':metrics['holdout']['exact']['alerts'], 'false_positives':metrics['holdout']['exact']['fp']},
        {'method':'Fuzzy name', 'alerts':metrics['holdout']['fuzzy']['alerts'], 'false_positives':metrics['holdout']['fuzzy']['fp']},
        {'method':'Explainable ML', 'alerts':metrics['holdout']['ml']['alerts'], 'false_positives':metrics['holdout']['ml']['fp']},
    ]).set_index('method')
    st.bar_chart(workload, stack=False)
    st.caption('Numbers reflect only a synthetic, scenario-driven benchmark. High performance here does not establish real-world screening quality.')
    st.markdown('#### How to explore this lab')
    st.write('**Screen Identity** → inspect a fictional name and ranked reference candidates. **Validation** → compare the different methods. **Human Review** → record an illustrative decision and export an audit file. **AI Governance** → examine controls, gaps and official reference sources.')

with screen:
    st.subheader('Candidate discovery and identity resolution')
    st.info('Select a fictional customer from the supplied dataset. Do not enter actual customer information into this public educational application.')
    s1,s2=st.columns([1,2])
    scenario_options = ['All scenarios']+sorted(customers.scenario.unique().tolist())
    with s1:
        scenario = st.selectbox('Fictional scenario', scenario_options)
    subset = customers if scenario == 'All scenarios' else customers[customers.scenario == scenario]
    choices = subset.customer_id.tolist()
    with s2:
        customer_id = st.selectbox('Choose a fictional customer identity', choices,
            format_func=lambda id: f'{id} · {customers.loc[customers.customer_id == id,"customer_name"].iloc[0]}')
    customer = customers.loc[customers.customer_id == customer_id].iloc[0]
    cand = pairs[pairs.customer_id == customer_id].sort_values('ml_score', ascending=False)
    st.markdown(f'#### Customer · {customer.customer_name}')
    d1,d2,d3,d4=st.columns(4)
    d1.metric('Type', customer.entity_type)
    d2.metric('Country', customer.country)
    d3.metric('Birth year', customer.birth_year or 'Not supplied')
    d4.metric('Synthetic scenario', str(customer.scenario).replace('_',' ').title())
    shown = cand[['watchlist_id','ml_score','fuzzy_score','exact_score','name_similarity',
                  'identifier_conflict','year_conflict']].merge(
        watch[['watchlist_id','primary_name','simulated_regime']],on='watchlist_id',how='left')
    shown = shown[['watchlist_id','primary_name','simulated_regime','ml_score','fuzzy_score',
                   'exact_score','name_similarity','identifier_conflict','year_conflict']]
    st.markdown('#### Top five fictional reference candidates')
    st.dataframe(shown, hide_index=True, use_container_width=True,
                 column_config={'ml_score':st.column_config.NumberColumn('ML score',format='%.3f'),
                                'fuzzy_score':st.column_config.NumberColumn('Fuzzy score',format='%.3f'),
                                'name_similarity':st.column_config.NumberColumn('Name similarity',format='%.3f')})
    selected_watch = st.selectbox('Inspect candidate details', cand.watchlist_id.tolist(),
                format_func=lambda id: f'{id} · {watch.loc[watch.watchlist_id==id,"primary_name"].iloc[0]}')
    detail = cand.loc[cand.watchlist_id == selected_watch].iloc[0]
    reference = watch.loc[watch.watchlist_id == selected_watch].iloc[0]
    a,b=st.columns([1,1])
    with a:
        st.metric('ML ranking score', f'{float(detail.ml_score):.3f}',
                  help='Classifier output on artificial labels; not calibrated as a sanctions probability.')
        st.caption(f'Frozen validation threshold {ML_THRESHOLD:.3f} · {"Demo alert" if float(detail.ml_score) >= ML_THRESHOLD else "Below demo alert threshold"}')
        st.write(f'**Fictional registry record:** {reference.primary_name}')
        st.write(f'**Aliases:** {reference.aliases}')
        st.write(f'**Country:** {reference.country} · **Birth year:** {reference.birth_year or "Not provided"}')
        st.write('**Corroboration and contradictions**')
        for message in explain_identity_details(customer,reference):
            st.write('• '+message)
    with b:
        st.markdown('**Exact model-local explanation**')
        why = explain(model,detail)
        st.dataframe(why[['factor','observed','log_odds_effect']],hide_index=True,use_container_width=True,
            column_config={'observed':st.column_config.NumberColumn('Feature',format='%.2f'),
                           'log_odds_effect':st.column_config.NumberColumn('Log-odds contribution',format='%+.3f')})
        st.caption('Positive contributions increase the classifier log-odds; negative contributions reduce them. These explanations are mathematical, not proof of identity.')
    st.download_button('Download this fictional candidate list (CSV)',
        shown.to_csv(index=False).encode('utf-8'),
        file_name=f'synthetic_candidates_{customer_id}.csv',mime='text/csv')
    st.warning('Human adjudication requires independent source confirmation, current list data and jurisdiction-specific legal assessment. None are provided by this demo.')

with validation:
    st.subheader('Synthetic holdout test evidence')
    x1,x2,x3,x4=st.columns(4)
    x1.metric('Train customers', metrics['split_customer_counts']['training'])
    x2.metric('Validation customers', metrics['split_customer_counts']['validation'])
    x3.metric('Test customers', metrics['split_customer_counts']['test'])
    x4.metric('Frozen ML threshold',f'{ML_THRESHOLD:.3f}')
    st.caption('Train, validation and test use disjoint scenario-generating watchlist groups. Candidate retrieval is limited to five name-similar entries. Threshold is selected on validation only.')
    table=[]
    for key,label in [('exact','Exact names'),('fuzzy','Fuzzy name'),('ml','Explainable ML')]:
        d=metrics['holdout'][key]
        table.append({'System':label,'Precision':d['precision'], 'Recall':d['recall'],
            'F1':d['f1'],'Alerts':d['alerts'], 'TP':d['tp'],'FP':d['fp'],
            'FN':d['fn'],'TN':d['tn'], 'Wrong-record alerts':d['wrong_record_alerts']})
    st.dataframe(pd.DataFrame(table),hide_index=True,use_container_width=True,
        column_config={col:st.column_config.NumberColumn(col,format='%.1f%%') for col in []})
    chart = pd.DataFrame([{'method':r['System'], 'Precision':r['Precision'],
                           'Recall':r['Recall'],'F1':r['F1']} for r in table]).set_index('method')
    st.markdown('#### Precision, recall and F1 are different measures')
    st.bar_chart(chart, stack=False)
    st.caption('No stacked rates. Values are fractions from 0 to 1. Synthetic labels are not independently validated designations.')
    st.markdown('#### Investigate synthetic failure cases')
    test_result = customer_results(test, test_pairs, 'ml', ML_THRESHOLD)
    failures = test_result[(test_result.ground_truth_match != test_result.alert) |
                           ((test_result.alert == 1)&(test_result.correct_record == 0))]
    st.dataframe(failures[['customer_id','customer_name','scenario','ground_truth_match',
                           'selected_score','alert','watchlist_id']],hide_index=True,use_container_width=True)
    st.warning('No validation on real sanctions lists, false associations involving real people, multilingual robustness, temporal drift or jurisdiction-specific obligations. This is not a production model.')
    with st.expander('Educational threshold sensitivity (does NOT change frozen reported test results)'):
        what_if = st.slider('Explore an illustrative threshold', .20,.99,ML_THRESHOLD,.01)
        sensitivity = stats(customer_results(test,test_pairs,'ml',what_if))
        st.write(f'At this illustrative setting, {sensitivity["alerts"]} test alerts would occur, with {sensitivity["fp"]} false positives and {sensitivity["fn"]} missed synthetic links.')
        st.caption('This is test-set exploration, not proper threshold tuning. The published benchmark remains frozen at the validation-selected threshold.')

with review:
    st.subheader('Documented human decision workflow')
    st.write('The simulation preserves a distinction between an automated screening alert and an investigator conclusion. Records exist **in your current browser session only**.')
    top_ml = pairs.sort_values(['customer_id','ml_score'],ascending=[True,False]).drop_duplicates('customer_id')
    reviewed = customers.merge(top_ml[['customer_id','watchlist_id','ml_score']],on='customer_id',how='left')
    reviewed['alert'] = reviewed.ml_score >= ML_THRESHOLD
    flag_only = st.checkbox('Show model-flagged fictional customers only',value=True)
    available = reviewed[reviewed.alert] if flag_only else reviewed
    st.dataframe(available[['customer_id','customer_name','watchlist_id','ml_score','alert']].head(180),
                 hide_index=True,use_container_width=True)
    chosen = st.selectbox('Select a customer case', available.customer_id.tolist(),
        format_func=lambda id: f'{id} · {customers.loc[customers.customer_id==id,"customer_name"].iloc[0]}',key='review_case')
    rec = reviewed.loc[reviewed.customer_id==chosen].iloc[0]
    st.write(f'**Fictional candidate:** {rec.watchlist_id} · **Model score:** {rec.ml_score:.4f} · **Alert:** {"Yes" if rec.alert else "No"}')
    with st.form('decision_form', clear_on_submit=False):
        reviewer = st.text_input('Reviewer pseudonym',value='Demo reviewer',max_chars=60)
        decision = st.selectbox('Human review outcome',[
            'Request further information',
            'Escalate for independent verification',
            'False positive (fictional scenario)',
            'No confirmed match based on available information',
        ])
        rationale = st.text_area('Document evidence and rationale (minimum 20 characters)',
          placeholder='Describe the agreeing/conflicting identity attributes and what information is missing.',height=115)
        save = st.form_submit_button('Record simulated review decision',type='primary')
    if save:
        error = review_form_error(reviewer, rationale)
        if error:
            st.error(error)
        else:
            st.session_state.decisions.append({
                'event_time_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
                'customer_id':chosen,'candidate_watchlist_id':str(rec.watchlist_id),
                'model_score':round(float(rec.ml_score),6),'model_alert':int(rec.alert),
                'reviewer_pseudonym':reviewer.strip(),'human_decision':decision,
                'rationale':rationale.strip(),
                'data_provenance':'SYNTHETIC - FICTIONAL WATCHLIST',
                'persistence':'Browser session only',
            })
            st.success('Simulated decision recorded in the current session.')
    st.markdown('#### Current session review log')
    if st.session_state.decisions:
        logs=pd.DataFrame(st.session_state.decisions)
        st.dataframe(logs,hide_index=True,use_container_width=True)
        st.download_button('Download simulated decisions CSV',logs.to_csv(index=False).encode('utf-8'),
           file_name='sanctions_lab02_session_review_audit.csv',mime='text/csv')
    else:
        st.caption('No simulated reviewer decisions yet. Record a decision above to test the export.')
    st.caption('The session log is not tamper resistant, does not persist across sessions and must never be used as a regulatory case management record.')

with gov:
    st.subheader('AI governance by design and by limitation')
    st.write('The control matrix distinguishes **demonstrated prototype mechanisms** from safeguards that would require substantial work before any operational application.')
    control_matrix = [
        ('Source provenance','Seeded fictional records, dataset hashes and source manifest','Demonstrated in demo'),
        ('List freshness','No scheduled updates or live official sanctions feed','Not implemented'),
        ('Entity resolution','Compare names, aliases and corroborating/conflicting attributes','Demonstrated in demo'),
        ('Human oversight','No automatic regulatory action; human case rationale is required','Demonstrated in demo'),
        ('Model explainability','Exact logistic regression log-odds contributions','Demonstrated in demo'),
        ('Independent model validation','Synthetic holdout only; no independent production challenger','Partial'),
        ('False positive management','Record false positives and compare alert workloads','Demonstrated in demo'),
        ('Bias and multilingual fairness','No structured multilingual/fairness test suite','Not implemented'),
        ('Audit trail security','CSV export exists; no signed, retained or access-controlled audit store','Partial'),
        ('Model drift and change governance','No ongoing drift, retraining or approval workflow','Not implemented'),
        ('Cybersecurity and access','No authentication or enterprise data-access controls','Not implemented'),
        ('Legal sanctions determination','No jurisdiction screening logic, designation verification, ownership/control assessment or blocking','Not implemented'),
    ]
    controls=pd.DataFrame(control_matrix,columns=['Control domain','Evidence and limitation','Evidence status'])
    st.dataframe(controls,hide_index=True,use_container_width=True)
    st.markdown('#### Source hierarchy and published frameworks')
    st.markdown('''
* [OFAC Sanctions List Service](https://ofac.treasury.gov/sanctions-list-service) — official US sanctions data and download access; **not ingested** by this app.
* [United Nations Security Council Consolidated List](https://main.un.org/securitycouncil/en/sanctions/un-sc-consolidated-list) — official consolidated list; **not ingested** by this app.
* [UK Sanctions List](https://www.gov.uk/government/publications/the-uk-sanctions-list) — the current UK source. The prior OFSI Consolidated List ceased updates on **28 January 2026**; **not ingested** by this app.
* [MAS AI Risk Management Guidelines](https://www.mas.gov.sg/regulation/guidelines/guidelines-on-artificial-intelligence-risk-management-for-financial-institutions) — published October 2026, effective October 2027; referenced for AI risk control discussion, not certification.
* [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) — Govern, Map, Measure and Manage risk concepts.
''')
    st.warning('The framework mapping is illustrative and not a legal opinion, sanctions screening service, regulatory approval, or MAS certification.')
    st.markdown('#### Artifact provenance')
    st.json({k:v for k,v in manifest.items() if k!='source_files_sha256'},expanded=False)
    st.caption('No production-ready legal or sanctions compliance functionality is implemented. For methodology and risk register, see the accompanying public repository.')
