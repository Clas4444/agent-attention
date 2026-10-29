"""Portable workflow contract tests; no model or downstream task execution."""
import copy
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from scripts.workflow_setup import (advance, agent_map, attach_attention, diagram, export, fingerprint, load,
                                    questions, select, start, template, validate)

ROOT = Path(__file__).resolve().parents[1]


class WorkflowSetupTests(unittest.TestCase):
    def document(self):
        return template('both')

    def test_generated_workflow_resources_match_source(self):
        from scripts.workflow_assets import check
        self.assertEqual(check(ROOT),[])

    def test_installed_setup_payload_is_self_contained(self):
        folder=ROOT/'.github/skills/loop'
        if not folder.is_dir(): folder=ROOT/'skills/agent-attention'
        with tempfile.TemporaryDirectory() as directory:
            installed=Path(directory)/'installed skill'
            shutil.copytree(folder,installed)
            command=[sys.executable,'-I','-B',str(installed/'scripts/workflow_setup.py'),
                     'check','--file',str(installed/'assets/workflow-example.json')]
            if (installed/'assets/catalog.json').is_file(): command+=['--catalog',str(installed/'assets/catalog.json')]
            result=subprocess.run(command,cwd=directory,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['installed_skills'],'NOT_RUN')

    def test_layers_and_questions_are_optional_and_valid(self):
        for layer in ('skills', 'attention', 'both'):
            document=template(layer);validate(document)
            choice=select(document,start(document,{'kind':'bug'}))
            self.assertEqual(bool(choice['skills']),layer!='attention')
            self.assertEqual(choice['attention_requested'],layer!='skills')
            self.assertEqual(len(questions(layer)),8)

    def test_selects_conditional_skill_and_profile_before_work(self):
        document=self.document()
        bug=select(document,start(document,{'kind':'bug'}))
        feature=select(document,start(document,{'kind':'feature'}))
        self.assertEqual(bug['skills'],['loop-debug'])
        self.assertEqual(feature['skills'],['loop-code'])
        self.assertEqual(bug['attention']['batch'],4)
        self.assertEqual(feature['attention']['batch'],3)
        self.assertEqual(bug['execution'],'NONE')

    def test_missing_or_wrong_fact_never_silently_selects_fallback(self):
        document=self.document()
        with self.assertRaisesRegex(ValueError,'missing condition'): select(document,start(document))
        with self.assertRaisesRegex(ValueError,'wrong fact type'): start(document,{'kind':True})
        with self.assertRaises(ValueError): start(document,{'typo':'bug'})
        with self.assertRaises(ValueError): start(document,[])

    def test_success_failure_completion_and_cycle_return(self):
        document=self.document()
        state=start(document,{'kind':'bug','risk':'high'})
        failed=advance(document,state,'FAIL','test exited 1')
        self.assertEqual(failed['step'],'work')
        self.assertEqual(failed['cycles_completed'],0)
        verified=advance(document,state,'PASS','item implemented')
        self.assertEqual(verified['step'],'verify')
        self.assertEqual(select(document,verified)['attention']['verify'],5)
        again=advance(document,verified,'PASS','checks pass, another item remains',{'done':False})
        self.assertEqual(again['step'],'work')
        self.assertEqual(again['cycles_completed'],1)
        self.assertEqual(select(document,again)['attention']['verify'],3)
        done=advance(document,verified,'PASS','acceptance criteria met',{'done':True})
        self.assertEqual(done['status'],'DONE')
        with self.assertRaises(ValueError): advance(document,done,'PASS','should not execute')

    def test_attention_inherits_task_profile_and_expires_per_step(self):
        document=self.document();document['attention']={'sync':4,'focus':2}
        state=start(document,{'kind':'bug','risk':'high'})
        state=advance(document,state,'PASS','work ready')
        self.assertEqual(select(document,state)['attention']['sync'],4)
        state=advance(document,state,'PASS','verified partial result',{'done':False})
        selected=select(document,state)
        self.assertEqual(selected['attention']['sync'],4)
        self.assertEqual(selected['attention']['verify'],3)

    def test_attention_attachment_preserves_skills_conditions_and_routes(self):
        original=template('skills');before=copy.deepcopy(original)
        updated=attach_attention(original,{'attention':{'sync':4},
            'steps':{'verify':[{'binding':0,'attention':{'verify':5}}]}})
        self.assertEqual(original,before)
        for old,new in zip(original['steps'],updated['steps']):
            self.assertEqual(old['transitions'],new['transitions'])
            for left,right in zip(old['bindings'],new['bindings']):
                self.assertEqual(left['skills'],right['skills'])
                self.assertEqual(left['when'],right['when'])
        state=advance(updated,start(updated,{'kind':'feature','risk':'high'}),'PASS','implemented')
        self.assertEqual(select(updated,state)['attention']['verify'],5)
        self.assertEqual(select(updated,state)['attention']['sync'],4)
        with self.assertRaises(ValueError): attach_attention(original,{'steps':{'absent':[]}})
        with self.assertRaises(ValueError): attach_attention(original,{'steps':{'work':[{'binding':True,'attention':{}}]}})

    def test_blocked_not_run_and_limits_stop_without_forcing_cycles(self):
        document=self.document();document['limits']['max_cycles']=1
        state=start(document,{'kind':'feature','risk':'normal'})
        for status in ('BLOCKED','NOT_RUN'):
            self.assertEqual(advance(document,state,status,'missing prerequisite')['status'],'STOP')
        state=advance(document,state,'PASS','work ready')
        stopped=advance(document,state,'PASS','partial result checked',{'done':False})
        self.assertEqual(stopped['last']['reason'],'MAX_CYCLES')
        document=self.document();document['limits']['max_steps']=1
        stopped=advance(document,start(document,{'kind':'bug'}),'FAIL','failed first attempt')
        self.assertEqual(stopped['last']['reason'],'MAX_STEPS')

    def test_changed_workflow_or_invalid_cursor_is_rejected(self):
        document=self.document();state=start(document,{'kind':'bug'})
        edited=copy.deepcopy(document);edited['goal']='Different goal'
        with self.assertRaises(ValueError): select(edited,state)
        for value in (-1,True,10000):
            changed=dict(state,steps_completed=value)
            with self.subTest(value=value),self.assertRaises(ValueError): select(document,changed)

    def test_bad_graphs_cannot_be_exported_or_routed(self):
        modifications=[lambda d:d['limits'].update(max_cycles=0),
                       lambda d:d.update(entry='missing'),
                       lambda d:d['steps'][0]['transitions'][0].update(next='missing'),
                       lambda d:d['steps'][0]['transitions'].pop(),
                       lambda d:d['steps'][0]['bindings'].reverse(),
                       lambda d:d['steps'][0].update(sources=['../outside']),
                       lambda d:d['steps'][1].update(cycle_end=False),
                       lambda d:d['steps'].append(dict(copy.deepcopy(d['steps'][0]),id='unreachable')),
                       lambda d:d['steps'][0]['bindings'][0].update(attention={'verify':True})]
        for mutate in modifications:
            document=self.document();mutate(document)
            with self.subTest(mutate=mutate),self.assertRaises(ValueError): validate(document)
        with self.assertRaisesRegex(ValueError,'unknown/unavailable'): validate(self.document(),{'loop-code'})

    def test_unknown_fields_and_fact_provenance_typos_are_not_ignored(self):
        for mutate in (lambda d:d.update(profile={'verify':5}),
                       lambda d:d['steps'][0].update(skill='loop-code'),
                       lambda d:d['steps'][0]['bindings'][0].update(mode={'verify':5}),
                       lambda d:d.update(fact_sources={'unknown':'invented location'})):
            document=self.document();mutate(document)
            with self.subTest(mutate=mutate),self.assertRaises(ValueError): validate(document)

    def test_condition_text_is_data_not_executable_code(self):
        document=self.document();document['steps'][0]['bindings'][0]['when']['kind']='__import__("os").system("never")'
        choice=select(document,start(document,{'kind':'__import__("os").system("never")'}))
        self.assertEqual(choice['skills'],['loop-debug'])

    def test_private_export_contains_map_and_refuses_overwrite_or_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            project=Path(directory);document=self.document()
            result=export(document,project)
            output=Path(result['directory'])
            self.assertEqual(set(p.name for p in output.iterdir()),{'workflow.json','AGENT-MAP.md','diagram.mmd','.gitignore'})
            self.assertEqual((output/'.gitignore').read_text(),'*\n')
            self.assertEqual(load(output/'workflow.json'),document)
            self.assertIn('Do not scan the whole project',agent_map(document))
            before={p.name:p.read_bytes() for p in output.iterdir()}
            with self.assertRaises(FileExistsError): export(document,project)
            self.assertEqual(before,{p.name:p.read_bytes() for p in output.iterdir()})
            with self.assertRaises(ValueError): export(document,project,'../outside')

    def test_invalid_graph_never_creates_export_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            document=self.document();document['steps'][0]['transitions'][0]['next']='absent'
            with self.assertRaises(ValueError): export(document,Path(directory))
            self.assertEqual(list(Path(directory).iterdir()),[])

    def test_portable_paths_reject_windows_parent_and_device_aliases(self):
        with tempfile.TemporaryDirectory() as directory:
            project=Path(directory)
            for path in ('.. /outside','new/../outside','con/file','new/name.','new/a|b','new/space ','.GiT/maps'):
                with self.subTest(path=path),self.assertRaises(ValueError):
                    export(self.document(),project,path)
            self.assertEqual(list(project.iterdir()),[])

    def test_export_is_ignored_in_a_project_without_global_ignore_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            project=Path(directory)
            subprocess.run(['git','init','--quiet',str(project)],check=True,capture_output=True)
            result=export(self.document(),project,'local-workflows/example')
            target=Path(result['directory'])/'AGENT-MAP.md'
            checked=subprocess.run(['git','check-ignore',str(target)],cwd=project,capture_output=True)
            self.assertEqual(checked.returncode,0)
            self.assertFalse((project/'.gitignore').exists())

    def test_output_symlink_is_rejected_without_writing_outside_project(self):
        with tempfile.TemporaryDirectory() as directory:
            project=Path(directory)/'project';outside=Path(directory)/'outside'
            project.mkdir();outside.mkdir()
            try: os.symlink(outside,project/'alias',target_is_directory=True)
            except OSError: self.skipTest('directory symlink creation is unavailable')
            with self.assertRaises(ValueError): export(self.document(),project,'alias/example')
            self.assertEqual(list(outside.iterdir()),[])

    def test_duplicate_json_and_boolean_status_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'bad.json';file.write_text('{"id":"one","id":"two"}')
            with self.assertRaises(ValueError): load(file)
        document=self.document()
        with self.assertRaises(ValueError): advance(document,start(document),True,'not a status')

    def test_large_input_is_rejected_and_mermaid_ids_avoid_reserved_words(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'large.json';file.write_bytes(b' '*1_000_001)
            with self.assertRaisesRegex(ValueError,'exceeds'): load(file)
        document=self.document();document['entry']='end';document['steps'][0]['id']='end'
        for step in document['steps']:
            for edge in step['transitions']:
                if edge['next']=='work': edge['next']='end'
        result=diagram(document)
        self.assertIn('step_end["end"]',result)
        self.assertIn('terminal_done',result)

    def test_cli_runs_under_isolated_python_and_uses_exact_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'workflow.json';file.write_text(json.dumps(self.document()))
            result=subprocess.run([sys.executable,'-I','-B',str(ROOT/'scripts/workflow_setup.py'),
                                   'check','--file',str(file)],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['workflow_sha256'],fingerprint(self.document()))

    def test_cli_facts_file_selects_without_shell_interpolation(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);document=self.document()
            (base/'workflow.json').write_text(json.dumps(document))
            (base/'facts.json').write_text(json.dumps({'kind':'bug','risk':'high'}))
            helper=str(ROOT/'scripts/workflow_setup.py')
            result=subprocess.run([sys.executable,'-I',helper,'start','--file',str(base/'workflow.json'),
                                   '--facts-file',str(base/'facts.json')],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            (base/'cursor.json').write_text(result.stdout)
            selected=subprocess.run([sys.executable,'-I',helper,'select','--file',str(base/'workflow.json'),
                                     '--state',str(base/'cursor.json')],capture_output=True,text=True,timeout=10)
            self.assertEqual(selected.returncode,0,selected.stderr)
            self.assertEqual(json.loads(selected.stdout)['skills'],['loop-debug'])

    def test_cli_reports_missing_facts_as_blocked_without_changing_state(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);document=self.document()
            (base/'workflow.json').write_text(json.dumps(document))
            state_file=base/'cursor.json';state_file.write_text(json.dumps(start(document)))
            before=state_file.read_bytes()
            result=subprocess.run([sys.executable,'-I',str(ROOT/'scripts/workflow_setup.py'),
                'select','--file',str(base/'workflow.json'),'--state',str(state_file)],
                capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'],'BLOCKED')
            self.assertEqual(json.loads(result.stdout)['missing_facts'],['kind'])
            self.assertEqual(state_file.read_bytes(),before)
