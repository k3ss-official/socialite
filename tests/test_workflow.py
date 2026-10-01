"""Behavior checks use disposable data and mock all external services."""
import copy
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests
from bs4 import BeautifulSoup

from socialite import bible_v2, contracts, jobs, store
from socialite.config import ROOT
from socialite.stages import build, find, pitch, research
from socialite.web import sitecheck

spec = importlib.util.spec_from_file_location('test_dashboard', ROOT / 'dashboard/app.py')
dashboard = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = dashboard
spec.loader.exec_module(dashboard)


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data = self.root / 'data'
        self.data.mkdir()
        (self.root / 'templates').symlink_to(ROOT / 'templates', target_is_directory=True)
        self.lead = json.loads((ROOT / 'data/leads/scran-away-chorley/lead.json').read_text())
        self.bible = json.loads((ROOT / 'data/leads/scran-away-chorley/bible/v4.json').read_text())
        self.patches = [patch.object(store, 'data_dir', return_value=self.data),
                        patch.object(dashboard, 'data_dir', return_value=self.data),
                        patch.object(build, 'ROOT', self.root), patch.object(pitch, 'ROOT', self.root)]
        for p in self.patches:
            p.start()
        self.addCleanup(self.temp.cleanup)
        for p in self.patches:
            self.addCleanup(p.stop)
        dashboard.app.testing = True
        self.client = dashboard.app.test_client()

    def seed(self):
        store.save_json(self.data / 'leads' / self.lead['id'] / 'lead.json', self.lead)

    def seed_bible(self):
        self.seed()
        store.save_json(store.lead_dir(self.lead['id']) / 'bible/v4.json', self.bible)
        raw = store.lead_dir(self.lead['id']) / 'raw'
        for p in self.bible.get('photos', []):
            (raw / p['path']).parent.mkdir(parents=True, exist_ok=True)
            (raw / p['path']).write_bytes(b'fixture-image')

    def test_fresh_database_restores_leads_and_spend_once(self):
        self.seed()
        event = {'ts': store.now(), 'lead_id': self.lead['id'], 'stage': 'bible',
                 'action': 'generated', 'status': 'ok', 'cost_usd': .4, 'details': {}}
        (self.data / 'events.jsonl').write_text(json.dumps(event) + '\n')
        self.assertEqual(store.spend(self.lead['id']), .4)
        store.log_event('bible', 'generated', lead_id=self.lead['id'], cost_usd=.2)
        self.assertAlmostEqual(store.spend(self.lead['id']), .6)
        self.assertIn(self.lead['name'].encode(), self.client.get('/').data)
        store.rebuild_index()
        store.rebuild_index()
        self.assertAlmostEqual(store.spend(self.lead['id']), .6)

    def test_repeated_signup_and_backup_preserve_one_service(self):
        self.seed()
        for _ in range(2):
            store.sign_lead(self.lead['id'], ['r1_foundation'], {'r1_foundation': 39}, 'GBP')
        self.assertEqual(store.mrr_rollup()['GBP']['mrr'], 39)
        with self.assertRaises(ValueError):
            store.sign_lead(self.lead['id'], ['r1_foundation'], {'r1_foundation': 59}, 'GBP')
        store.rebuild_index()
        self.assertEqual(store.mrr_rollup()['GBP']['active_services'], 1)
        self.assertTrue(store.backup_database(self.root / 'backup.sqlite').is_file())

    def test_bible_image_links_resolve(self):
        self.seed_bible()
        page = self.client.get(f"/lead/{self.lead['id']}/bible/4")
        images = BeautifulSoup(page.data, 'html.parser').select('img[src]')
        self.assertTrue(images)
        for image in images:
            with self.client.get(image['src']) as response:
                self.assertEqual(response.status_code, 200)

    def test_minimal_valid_bible_builds_without_invented_rating(self):
        for k in ['typography', 'location', 'photos', 'alerts', 'sources']:
            self.bible.pop(k, None)
        self.bible['reviews'] = [{'quote': 'Sample', 'source': 'Google', 'rating': 5}]
        contracts.validate(self.bible, 'bible')
        self.seed_bible()
        manifest = build.build(self.lead['id'])
        html = (self.root / manifest['output_dir'] / 'index.html').read_text()
        self.assertNotIn('rating-badge', html)
        self.assertNotIn('Verified review', html)
        self.assertEqual(manifest['site_version'], build.build(self.lead['id'])['site_version'])

    def test_changed_photo_invalidates_build(self):
        self.seed_bible()
        first = build.build(self.lead['id'])
        photo = store.lead_dir(self.lead['id']) / 'raw' / self.bible['photos'][0]['path']
        photo.write_bytes(b'changed-image')
        second = build.build(self.lead['id'])
        self.assertGreater(second['site_version'], first['site_version'])

    def test_unrelated_contact_is_rejected_and_empty_search_stays_unknown(self):
        rows = [{'title': 'Different Business', 'href': 'https://unrelated.example',
                 'body': 'Preston, call 07802 111222'}]
        with patch.object(find.websearch, 'search', return_value=rows):
            lead = find.find_single('Audit Prospect, Preston', 'uk')
        self.assertIsNone(lead['contact']['phone'])
        self.assertEqual(lead['website']['verdict'], 'unknown')

    def test_affiliated_site_remains_real(self):
        rows = [{'title': 'Vestry Chorley', 'href': 'https://brunchnbubbles.co.uk/vestry/', 'body': 'Vestry Chorley'}]
        check = {'verdict': 'real', 'title': 'Vestry', 'text_sample': 'Vestry Chorley', 'signals': []}
        with patch.object(find.websearch, 'search', return_value=rows), patch.object(find.sitecheck, 'check', return_value=check):
            lead = find.find_single('Vestry, Chorley', 'uk')
        self.assertEqual(lead['website']['verdict'], 'real')

    def test_access_denial_is_unknown_not_dead(self):
        response = requests.Response()
        response.status_code = 403
        with patch.object(sitecheck.requests, 'get', return_value=response):
            self.assertEqual(sitecheck.check('https://example.com')['verdict'], 'unknown')

    def test_research_uses_actual_context_and_preserves_metadata_and_failures(self):
        lead = copy.deepcopy(self.lead)
        lead.update(id='audit-prospect-preston', name='Audit Prospect', locality='Preston', category='cocktail bar')
        lead['website'] = {'verdict': 'unknown', 'url': None}
        lead['qualification']['evidence'] = []
        lead['socials'] = [{'platform': 'facebook', 'url': 'https://facebook.com/audit'},
                           {'platform': 'instagram', 'url': 'https://instagram.com/audit'}]
        store.upsert_lead(lead)
        good = requests.Response()
        good.status_code = 200
        good.headers['content-type'] = 'text/html'
        good._content = b'<html><meta property="og:description" content="Audit Prospect, Preston, 123 followers"><body>Hi</body></html>'
        denied = requests.Response()
        denied.status_code = 403
        with patch.object(research.websearch, 'search', return_value=[]), patch.object(research, '_fetch', side_effect=[good, denied]):
            bundle = research.harvest(lead['id'])
        self.assertIn('cocktail bar Preston', bundle['queries'][-1])
        self.assertTrue(bundle['fetched'][0]['text_file'])
        self.assertEqual(bundle['fetched'][1]['status'], 403)
        self.assertEqual(bundle['fetched'][1]['outcome'], 'access_denied')

    def seed_v2(self):
        self.v2 = json.loads((ROOT / 'tests/fixtures/bible-v2.json').read_text())
        self.lead.update(id=self.v2['lead_id'], name='Demo Cafe', locality='Preston', category='cafe')
        self.seed()
        source = store.lead_dir(self.lead['id']) / 'raw/pages/demo.txt'
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(self.v2['evidence'][0]['excerpt'])
        self.v2['evidence'][0]['capture_file'] = 'pages/demo.txt'
        self.v2['evidence'][0]['content_hash'] = hashlib.sha256(source.read_bytes()).hexdigest()
        store.save_json(store.lead_dir(self.lead['id']) / 'bible/v1.json', self.v2)
        return self.v2

    def post(self, url, **data):
        self.client.get('/')
        with self.client.session_transaction() as session:
            data['csrf_token'] = session['csrf_token']
        return self.client.post(url, data=data, follow_redirects=True)

    def approve(self):
        return bible_v2.save_review(self.v2, {c['id']: 'approved' for c in self.v2['claims']}, {}, 'Tester')

    def test_review_gate_and_stale_review(self):
        self.seed_v2()
        with self.assertRaisesRegex(ValueError, 'Save a review'):
            build.build(self.lead['id'], 1)
        self.approve()
        manifest = build.build(self.lead['id'], 1)
        self.assertTrue((self.root / manifest['output_dir'] / 'index.html').is_file())
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.approve()
        self.v2['claims'][0]['value'] = 'Changed after review'
        with self.assertRaisesRegex(ValueError, 'exact Bible'):
            bible_v2.project(self.v2, bible_v2.load_review(self.lead['id'], 1))

    def test_unknown_and_snippet_claims_cannot_be_approved(self):
        self.seed_v2()
        claim = self.v2['claims'][0]
        claim.update(status='unknown', value=None)
        with self.assertRaisesRegex(ValueError, 'Only observed'):
            self.approve()
        claim.update(status='observed', value='Demo Cafe')
        self.v2['evidence'][0]['outcome'] = 'snippet'
        with self.assertRaisesRegex(ValueError, 'Only observed'):
            self.approve()

    def test_invalid_evidence_reference_and_missing_source_are_rejected(self):
        self.seed_v2()
        self.v2['claims'][0]['evidence_ids'] = ['invented']
        with self.assertRaisesRegex(ValueError, 'evidence'):
            bible_v2.validate(self.v2)
        self.v2['claims'][0]['evidence_ids'] = ['E-demo']
        self.v2['evidence'][0]['outcome'] = 'access_denied'
        with self.assertRaisesRegex(ValueError, 'unavailable'):
            bible_v2.validate(self.v2)

    def test_dashboard_forms_need_csrf_and_queue_only_once(self):
        self.seed_v2()
        url = f"/lead/{self.lead['id']}/research"
        self.assertEqual(self.client.post(url, data={'staff_name':'Tester'}).status_code, 400)
        self.assertEqual(self.post(url, staff_name='Tester').status_code, 200)
        self.post(url, staff_name='Tester')
        self.assertEqual(len(jobs.for_lead(self.lead['id'])), 1)
        job = jobs.for_lead(self.lead['id'])[0]
        self.assertEqual(self.client.get('/job/' + job['id']).json['status'], 'queued')
        self.post('/job/' + job['id'] + '/cancel')
        self.assertEqual(jobs.get(job['id'])['status'], 'cancelled')
        self.assertIsNone(jobs.run_next())

    def test_research_to_review_to_real_preview_job(self):
        self.seed_v2()
        job = jobs.enqueue(self.lead['id'], 'research', 'Tester')
        bundle = {'fetched': [{'outcome':'captured'}]}
        with patch.object(research, 'harvest', return_value=bundle), patch.object(bible_v2, 'generate', return_value=self.v2):
            done = jobs.run_next()
        self.assertEqual(done['status'], 'review')
        self.assertEqual(done['result']['bible_version'], 1)
        review_data = {'reviewer':'Tester', 'revision':0}
        review_data.update({'claim_'+c['id']:'approved' for c in self.v2['claims']})
        response = self.post(f"/lead/{self.lead['id']}/bible/1/review", **review_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Review saved', response.data)
        evidence = self.client.get(f"/lead/{self.lead['id']}/bible/1/evidence/E-demo")
        self.assertIn(b'&lt;script&gt;', evidence.data)
        self.assertNotIn(b"<script>alert('untrusted')", evidence.data)
        self.post(f"/lead/{self.lead['id']}/bible/1/preview", staff_name='Tester')
        done = jobs.run_next()
        self.assertEqual(done['status'], 'succeeded', done.get('error'))
        self.assertTrue(done['result']['site_version'])
        self.assertTrue(done['result']['pitch_version'])

    def test_failed_synthesis_preserves_collection_result_and_can_retry(self):
        self.seed_v2()
        first = jobs.enqueue(self.lead['id'], 'research', 'Tester')
        bundle = {'fetched':[{'outcome':'access_denied'}]}
        with patch.object(research, 'harvest', return_value=bundle), patch.object(bible_v2, 'generate', side_effect=RuntimeError('Provider unavailable')):
            done = jobs.run_next()
        self.assertEqual(done['status'], 'failed')
        self.assertEqual(done['result']['collection_failures'], 1)
        self.assertIn('Provider unavailable', done['error'])
        self.assertNotEqual(first['id'], jobs.enqueue(self.lead['id'], 'research', 'Tester')['id'])

    def test_changed_review_prevents_queued_preview(self):
        self.seed_v2()
        review = self.approve()
        jobs.enqueue(self.lead['id'], 'preview', 'Tester', bible_version=1)
        bible_v2.save_review(self.v2, review['claims'], {}, 'Tester', expected_revision=1)
        done = jobs.run_next()
        self.assertEqual(done['status'], 'failed')
        self.assertIn('Review changed', done['error'])

    def test_interrupted_worker_recovery_preserves_jobs(self):
        self.seed_v2()
        job = jobs.enqueue(self.lead['id'], 'research', 'Tester')
        jobs.update(job['id'], status='running', stage='collecting')
        self.assertEqual(jobs.recover_interrupted(), 1)
        store.rebuild_index()
        self.assertEqual(jobs.get(job['id'])['status'], 'failed')

    def test_printable_report_follows_reference_structure(self):
        self.seed_v2()
        report = self.client.get(f"/lead/{self.lead['id']}/bible/1/report")
        self.assertEqual(report.status_code, 200)
        for heading in ['Executive summary', 'Key findings', 'Priority overview', 'Action roadmap', 'Appendix: sources and receipts']:
            self.assertIn(heading.encode(), report.data)
        self.assertIn(b'window.print()', report.data)

    def test_changed_capture_blocks_an_approved_preview(self):
        self.seed_v2()
        review = self.approve()
        capture = store.lead_dir(self.lead['id']) / 'raw/pages/demo.txt'
        capture.write_text('Changed source after approval')
        with self.assertRaisesRegex(ValueError, 'source capture changed'):
            bible_v2.project(self.v2, review)

    def test_cancellation_after_collection_prevents_synthesis(self):
        self.seed_v2()
        job = jobs.enqueue(self.lead['id'], 'research', 'Tester')
        def collect(*args, **kwargs):
            jobs.cancel(job['id'])
            return {'fetched':[{'outcome':'captured'}]}
        with patch.object(research, 'harvest', side_effect=collect), patch.object(bible_v2, 'generate') as generate:
            done = jobs.run_next()
        self.assertEqual(done['status'], 'cancelled')
        generate.assert_not_called()

    def test_v2_synthesis_uses_canonical_capture_and_new_artifact_version(self):
        from socialite import llm
        self.seed_v2()
        entry = self.v2['evidence'][0]
        bundle = {'harvested_at':entry['captured_at'], 'fetched':[
            {'evidence_id':entry['id'],'url':entry['url'],'kind':'own_site',
             'captured_at':entry['captured_at'],'outcome':'captured',
             'text_file':entry['capture_file'],'content_hash':entry['content_hash']}],
             'results':[], 'images':[], 'query_outcomes':[]}
        response = copy.deepcopy(self.v2)
        response['evidence'][0]['url'] = 'https://invented.example/'
        with patch.object(llm, 'generate_json', return_value=response):
            output = bible_v2.generate(self.lead['id'], bundle)
        self.assertEqual(output['version'], 2)
        self.assertEqual(output['evidence'][0]['url'], entry['url'])
        self.assertTrue((store.lead_dir(self.lead['id']) / 'bible/v2.json').is_file())


if __name__ == '__main__':
    unittest.main()
