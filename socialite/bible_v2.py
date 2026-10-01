"""Evidence-backed Bible and explicit, reviewed projection for legacy consumers."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from jsonschema import ValidationError

from . import contracts, store
from .config import ROOT, settings
from .stages.find import prospect_area, research_context

SECTIONS = ('identity', 'company', 'operators', 'audience', 'social', 'reviews',
            'services', 'brand', 'credentials', 'competitors')
REQUIRED_BINDINGS = ('name', 'category', 'story', 'headline', 'subheadline',
                     'about_heading', 'about', 'cta_label', 'cta_type', 'cta_value')


def evidence_pack(lead_id: str, bundle: dict) -> list[dict]:
    raw = store.lead_dir(lead_id) / 'raw'
    evidence = []
    for f in bundle.get('fetched', []):
        if not f.get('evidence_id'):
            continue  # Legacy bundles must be refreshed to gain traceable captures.
        excerpt = (raw / f['text_file']).read_text()[:6000] if f.get('text_file') else ''
        evidence.append({'id': f['evidence_id'], 'url': f['url'], 'kind': f['kind'],
                         'scope': 'competitor' if f['kind'] == 'competitor' else
                                  'unmatched' if f.get('outcome') == 'entity_unmatched' else 'prospect',
                         'captured_at': f['captured_at'], 'outcome': f['outcome'],
                         'capture_file': f.get('text_file'), 'content_hash': f.get('content_hash'),
                         'excerpt': excerpt})
    for i, r in enumerate(bundle.get('results', [])):
        evidence.append({'id': f'S-{i:03d}', 'url': r['href'], 'kind': 'search_snippet',
                         'scope': 'competitor' if r['kind'] == 'competitor' else 'prospect',
                         'captured_at': bundle['harvested_at'], 'outcome': 'snippet',
                         'capture_file': None, 'content_hash': None,
                         'excerpt': r['title'] + '\n' + r['body']})
    return evidence


def validate(bible: dict) -> dict:
    contracts.validate(bible, 'bible-v2')
    def index(items, label):
        values = {item['id']: item for item in items}
        if len(values) != len(items):
            raise ValueError(f'Duplicate {label} ids')
        return values
    evidence = index(bible['evidence'], 'evidence')
    claims = index(bible['claims'], 'claim')
    assets = index(bible['assets'], 'asset')
    roadmap = index(bible['roadmap'], 'roadmap')
    for entry in evidence.values():
        if entry['outcome'] == 'captured' and (not entry['capture_file'] or not entry['content_hash']):
            raise ValueError('Captured evidence needs its saved file and content hash')
    coverage = {item['section'] for item in bible['coverage']}
    if coverage != set(SECTIONS) or len(bible['coverage']) != len(SECTIONS):
        raise ValueError('Coverage must describe every research section exactly once')
    for item in bible['claims'] + bible['coverage'] + bible['roadmap']:
        if not set(item['evidence_ids']) <= evidence.keys():
            raise ValueError('Unknown evidence reference')
    for claim in claims.values():
        if claim['status'] == 'observed' and not claim['evidence_ids']:
            raise ValueError('Observed claims need evidence')
        if claim['status'] == 'observed' and not any(evidence[e]['outcome'] in ('captured', 'snippet') for e in claim['evidence_ids']):
            raise ValueError('An unavailable source cannot establish an observed claim')
        if claim['status'] == 'unknown' and claim['value'] is not None:
            raise ValueError('Unknown claims must have null value')
    if not set(bible['site']['bindings'].values()) <= claims.keys():
        raise ValueError('Unknown site claim binding')
    if not set(bible['site']['asset_ids']) <= assets.keys():
        raise ValueError('Unknown site asset')
    for asset in assets.values():
        if asset['source_evidence_id'] not in evidence:
            raise ValueError('Asset needs a known source')
    for comparison in bible['comparisons']:
        if comparison['prospect_claim_id'] not in claims or comparison['competitor_claim_id'] not in claims:
            raise ValueError('Comparison needs both claims')
    for item in roadmap.values():
        if not set(item['claim_ids']) <= claims.keys() or not set(item['dependencies']) <= roadmap.keys():
            raise ValueError('Unknown roadmap dependency')
        if item['id'] in item['dependencies']:
            raise ValueError('Roadmap cannot depend on itself')
    palette = bible['site']['design']['palette']
    for key in ('primary', 'secondary', 'accent', 'background', 'text'):
        if palette.get(key) and not re.fullmatch(r'#[0-9a-fA-F]{6}', palette[key]):
            raise ValueError('Palette colors must use six-digit hex')
    for font in bible['site']['design']['typography'].values():
        if not re.fullmatch(r'[A-Za-z0-9 -]{1,60}', font):
            raise ValueError('Font names must be plain names')
    return bible


def generate(lead_id: str, bundle: dict) -> dict:
    from . import llm
    lead = store.get_lead(lead_id)
    evidence = evidence_pack(lead_id, bundle)
    if not evidence:
        raise ValueError('No usable source records; review collection failures before synthesis')
    template = (ROOT / 'prompts/bible-v2.md').read_text()
    materials = {'lead': research_context(lead), 'area': prospect_area(lead), 'bundle': bundle,
                 'evidence': evidence, 'schema': contracts.schema('bible-v2'),
                 'prompt': template, 'llm': settings()['llm']}
    inputs_hash = hashlib.sha256(json.dumps(materials, sort_keys=True).encode()).hexdigest()
    parent = store.lead_dir(lead_id) / 'bible'
    version = store.next_version(parent)
    metadata = {'schema_version': '2.0', 'lead_id': lead_id, 'version': version,
                'generated_at': store.now(), 'inputs_hash': inputs_hash}
    inventory = [{'id': f'A-{i:03d}', 'path': image['file'], 'source_evidence_id': image['evidence_id'],
                  'original_url': image['original_url'], 'content_hash': image['content_hash'],
                  'rights': 'unknown', 'use': 'gallery', 'caption': ''}
                 for i, image in enumerate(bundle.get('images', []))]
    prompt = (template + '\n\nINPUT BRIEF\n' + json.dumps(materials['lead'], ensure_ascii=False) +
              '\nCOLLECTION OUTCOMES\n' + json.dumps(bundle.get('query_outcomes', [])) +
              '\nOUTPUT METADATA\n' + json.dumps(metadata) +
              '\nCANONICAL EVIDENCE\n' + json.dumps(evidence, ensure_ascii=False) +
              '\nCANONICAL ASSETS\n' + json.dumps(inventory) +
              '\nOUTPUT SCHEMA\n' + json.dumps(materials['schema']))
    if len(prompt) > settings()['llm'].get('max_v2_input_chars', 140000):
        raise ValueError('Evidence exceeds synthesis input limit; narrow collection rather than silently dropping sources')
    result = llm.generate_json(prompt, 'bible-v2', lead_id, 'bible', estimated_cost_usd=.30)
    result.update(metadata)
    # The model cannot mint source captures, permissions, or asset provenance.
    result['evidence'], result['assets'] = evidence, inventory
    validate(result)
    store.save_json(parent / f'v{version}.json', result)
    store.advance_status(lead_id, 'bible')
    store.log_event('bible', 'generated_v2', lead_id=lead_id, version=version)
    return result


def review_path(lead_id: str, version: int) -> Path:
    return store.lead_dir(lead_id) / 'review' / f'v{version}.json'


def load_review(lead_id: str, version: int) -> dict:
    path = review_path(lead_id, version)
    return store.load_json(path) if path.exists() else {'claims': {}, 'assets': {}, 'revision': 0}


def approvable(claim: dict, evidence: dict) -> bool:
    return claim['status'] == 'observed' and any(
        evidence[e]['outcome'] == 'captured' and evidence[e]['scope'] == 'prospect'
        for e in claim['evidence_ids'])


def verify_capture(entry: dict, lead_id: str) -> None:
    raw = store.lead_dir(lead_id) / 'raw'
    capture = (raw / entry['capture_file']).resolve()
    if not capture.is_relative_to(raw.resolve()) or not capture.is_file():
        raise ValueError('A source capture is missing; collect and review it again')
    if hashlib.sha256(capture.read_bytes()).hexdigest() != entry['content_hash']:
        raise ValueError('A source capture changed; collect and review it again')


def save_review(bible: dict, decisions: dict, assets: dict, reviewer: str, note: str = '',
                expected_revision: int = 0) -> dict:
    validate(bible)
    if not reviewer.strip():
        raise ValueError('A reviewer name is required')
    evidence = {e['id']: e for e in bible['evidence']}
    claims = {c['id']: c for c in bible['claims']}
    inventory = {a['id']: a for a in bible['assets']}
    if not decisions.keys() <= claims.keys() or not assets.keys() <= inventory.keys():
        raise ValueError('Unknown review item')
    for key, decision in decisions.items():
        if decision not in ('approved', 'hold', 'rejected'):
            raise ValueError('Invalid claim decision')
        if decision == 'approved' and not approvable(claims[key], evidence):
            raise ValueError('Only observed, captured prospect claims can be approved for the page')
        if decision == 'approved':
            for entry_id in claims[key]['evidence_ids']:
                if evidence[entry_id]['outcome'] == 'captured':
                    verify_capture(evidence[entry_id], bible['lead_id'])
    for key, asset in assets.items():
        if asset.get('rights') not in ('owner_supplied', 'licensed', 'permission_confirmed') or not asset.get('note', '').strip():
            raise ValueError('Approved assets need a permission basis and note')
        if asset.get('use') not in ('hero', 'gallery', 'menu', 'about'):
            raise ValueError('Select an asset role')
    # Serialize concurrent staff reviews and detect stale form submissions.
    with store.db() as conn:
        conn.execute('BEGIN IMMEDIATE')
        prior = load_review(bible['lead_id'], bible['version'])
        if prior.get('revision', 0) != expected_revision:
            raise ValueError('This review changed; reload before saving')
        result = {'lead_id': bible['lead_id'], 'bible_version': bible['version'],
                  'bible_hash': hashlib.sha256(json.dumps(bible, sort_keys=True).encode()).hexdigest(),
                  'revision': expected_revision + 1, 'reviewer': reviewer.strip(), 'reviewed_at': store.now(),
                  'note': note, 'claims': decisions, 'assets': assets}
        store.save_json(review_path(bible['lead_id'], bible['version']), result)
        store.save_json(store.lead_dir(bible['lead_id']) / 'review' /
                        f"v{bible['version']}-r{result['revision']}.json", result)
    store.log_event('review', 'saved', lead_id=bible['lead_id'], version=bible['version'],
                    revision=result['revision'], reviewer=result['reviewer'])
    return result


def project(bible: dict, review: dict) -> tuple[dict, dict]:
    """Only explicitly approved bindings enter the classic site's data contract."""
    validate(bible)
    digest = hashlib.sha256(json.dumps(bible, sort_keys=True).encode()).hexdigest()
    if review.get('bible_hash') != digest:
        raise ValueError('Save a review for this exact Bible before generating a preview')
    claims = {c['id']: c for c in bible['claims']}
    evidence = {e['id']: e for e in bible['evidence']}
    values = {}
    for key, claim_id in bible['site']['bindings'].items():
        claim = claims[claim_id]
        if review['claims'].get(claim_id) == 'approved' and approvable(claim, evidence):
            for entry_id in claim['evidence_ids']:
                if evidence[entry_id]['outcome'] == 'captured':
                    verify_capture(evidence[entry_id], bible['lead_id'])
            values[key] = claim['value']
    missing = [key for key in REQUIRED_BINDINGS if key not in values]
    if missing:
        raise ValueError('Approve sourced page fields first: ' + ', '.join(missing))
    if values['cta_type'] in ('messenger',) and not re.match(r'^https://', values['cta_value']):
        raise ValueError('Contact link must use HTTPS')
    projected = {k: bible[k] for k in ('lead_id', 'version', 'generated_at', 'inputs_hash')}
    projected.update({'identity': {k: values[k] for k in ('name', 'category', 'story')},
                      'brand_voice': {'tone': 'Approved source copy', 'keywords': []},
                      **bible['site']['design'], 'usps': values.get('usps', []),
                      'reviews': values.get('reviews', []), 'services': values.get('services', []),
                      'hours': values.get('hours'), 'location': {k: values.get(k) for k in ('address', 'maps_query')},
                      'competitors': [], 'gap_matrix': [], 'photos': [],
                      'alerts': [c['note'] for c in bible['claims'] if c['status'] in ('unknown', 'conflicted') and c['note']],
                      'sources': sorted({evidence[e]['url'] for cid in bible['site']['bindings'].values()
                                         if review['claims'].get(cid) == 'approved' for e in claims[cid]['evidence_ids']})})
    projected['identity']['tagline'] = values.get('tagline')
    projected['site_copy'] = {k: values.get(k) for k in ('headline', 'subheadline', 'about_heading', 'about',
                            'menu_heading', 'reviews_heading', 'visit_heading', 'footer_line')}
    projected['site_copy']['cta_primary'] = {'label': values['cta_label'], 'type': values['cta_type'],
                                           'value': values['cta_value']}
    for asset in bible['assets']:
        if asset['id'] in review['assets']:
            permission = review['assets'][asset['id']]
            if permission.get('rights') not in ('owner_supplied', 'licensed', 'permission_confirmed') or not permission.get('note'):
                raise ValueError('Asset permission is unresolved')
            source = store.lead_dir(bible['lead_id']) / 'raw' / asset['path']
            if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != asset['content_hash']:
                raise ValueError('An approved asset is missing or changed; collect and review it again')
            projected['photos'].append({'path': asset['path'], 'use': permission['use'], 'caption': asset['caption']})
    aggregate = values.get('review_aggregate')
    if aggregate:
        try:
            contracts.validate(aggregate, 'review-aggregate')
        except ValidationError as exc:
            raise ValueError('Review aggregate is incomplete: ' + exc.message) from exc
        projected['review_aggregate'] = {**aggregate, 'verified': True}
    # Unknown gaps are not converted into false/missing capabilities.
    for claim in bible['claims']:
        if claim['field'].startswith('gap.') and review['claims'].get(claim['id']) == 'approved' and approvable(claim, evidence) and isinstance(claim['value'], bool):
            from .config import ladder
            key = claim['field'].removeprefix('gap.')
            if key in ladder()['gaps']:
                projected['gap_matrix'].append({'gap_key': key, 'label': ladder()['gaps'][key]['label'],
                                               'prospect_has': claim['value'], 'competitors_with': 0,
                                               'note': claim['note'] or ladder()['gaps'][key]['label'],
                                               'comparison_verified': False})
    try:
        contracts.validate(projected, 'bible')
    except ValidationError as exc:
        raise ValueError('Approved page fields have an invalid shape: ' + exc.message) from exc
    lead = store.get_lead(bible['lead_id'])
    lead = {**lead, 'socials': values.get('social_links', [])}
    if not isinstance(lead['socials'], list) or any(not isinstance(s, dict) or s.get('platform') not in ('facebook','instagram','tiktok','other') or not isinstance(s.get('url'), str) or not s['url'].startswith('https://') for s in lead['socials']):
        raise ValueError('Social links must be supported HTTPS profile links')
    return projected, lead
