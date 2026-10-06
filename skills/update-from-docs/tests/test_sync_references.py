"""Isolated maintenance behavior tests: no network, live actions or source refresh."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('sync', Path(__file__).parents[1] / 'sync_references.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = (Path(self.tmp.name) / 'source').resolve()
        for marker in ('.claude-plugin/plugin.json', '.codex-plugin/plugin.json', '.git/HEAD'):
            p = self.root / marker
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('fixture')
        for config in sync.REFERENCES.values():
            p = self.root / config['out']
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('- `old`\n')
    def contents(self):
        return {str(c['out']): (self.root/c['out']).read_bytes() for c in sync.REFERENCES.values()}
    def test_explicit_root_unrelated_cwd_and_symlink_cache(self):
        self.assertEqual(sync.validate_root(self.root), self.root)
        cache = Path(self.tmp.name) / '.claude/plugins/cache/vendor/plugin'
        cache.parent.mkdir(parents=True)
        cache.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(sync.RefreshError): sync.validate_root(cache)
        # Physical runtime cache destinations are rejected through aliases too.
        actual_cache = Path(self.tmp.name) / '.codex/plugins/cache/physical'
        actual_cache.mkdir(parents=True)
        alias = Path(self.tmp.name)/'alias'
        alias.symlink_to(actual_cache)
        with self.assertRaises(sync.RefreshError): sync.validate_root(alias)
        with self.assertRaises(sync.RefreshError): sync.validate_root(Path(self.tmp.name))
        old = Path.cwd()
        try:
            os.chdir(self.tmp.name)
            with patch.object(sync, 'fetch_names', return_value=['new']):
                self.assertEqual(sync.main(['--repo-root',str(self.root),'--check']),0)
        finally: os.chdir(old)
    def test_second_source_failure_preserves_outputs(self):
        before = self.contents()
        with patch.object(sync, 'fetch_names', side_effect=[['a'],sync.RefreshError('reference=purpose-keys; branch=current; source=_conditions; payload error')]):
            self.assertEqual(sync.main(['--repo-root',str(self.root)]),2)
        self.assertEqual(before,self.contents())
    def test_empty_and_malformed_payload_and_safe_error(self):
        class Response:
            def __init__(self,data): self.data=data
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self): return json.dumps(self.data).encode()
        for payload in ([],{},[{'name':42}],[{'name':'.markdown'}]):
            with patch.object(sync.urllib.request,'urlopen',return_value=Response(payload)):
                with self.assertRaisesRegex(sync.RefreshError,'reference=test; branch=next; source=_test'):
                    sync.fetch_names('_test','next','test')
        with patch.dict(os.environ,{'GITHUB_TOKEN':'super-secret'}),patch.object(sync.urllib.request,'urlopen',side_effect=OSError('super-secret')):
            with self.assertRaises(sync.RefreshError) as caught:sync.fetch_names('_test','next','test')
            self.assertNotIn('super-secret',str(caught.exception))
    def test_preview_drift_apply_and_idempotence(self):
        with patch.object(sync,'fetch_names',return_value=['new']):
            args=['--repo-root',str(self.root)]
            self.assertEqual(sync.main(args+['--check']),0)
            self.assertEqual(sync.main(args+['--check','--fail-on-drift']),1)
            self.assertEqual(sync.main(args),2) # explicit removal approval needed
            self.assertEqual(sync.main(args+['--approve-removals']),0)
            before=self.contents()
            self.assertEqual(sync.main(args+['--check','--fail-on-drift']),0)
            self.assertEqual(sync.main(args),0)
            self.assertEqual(before,self.contents())
    def test_replacement_failure_restores_originals(self):
        with patch.object(sync,'fetch_names',return_value=['new']):
            prepared=[sync.build(n,c,'current',self.root) for n,c in sync.REFERENCES.items()]
        before=self.contents();replace=os.replace;count=0
        def fail_second(src,dst):
            nonlocal count
            count+=1
            if count==2: raise OSError('fixture failure')
            return replace(src,dst)
        with patch.object(sync.os,'replace',side_effect=fail_second):
            with self.assertRaisesRegex(sync.RefreshError,'originals restored'):sync.replace_batch(prepared)
        self.assertEqual(before,self.contents())
    def test_output_symlink_escape(self):
        out=self.root / sync.REFERENCES['purpose-keys']['out']
        out.unlink();out.symlink_to(Path(self.tmp.name)/'elsewhere')
        with self.assertRaises(sync.RefreshError):sync.output_path(self.root,sync.REFERENCES['purpose-keys']['out'])

if __name__=='__main__':unittest.main()
