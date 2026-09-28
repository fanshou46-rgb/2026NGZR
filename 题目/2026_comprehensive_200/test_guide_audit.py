"""Regression mutations for previously missed guide requirements."""
import re
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from guide_audit import audit, HERE

class GuideRegression(unittest.TestCase):
    def codes(self, change):
        text=(HERE/'cases/stage1/A02-01-s1.xml').read_text(encoding='utf-8')
        changed=change(text)
        self.assertNotEqual(text,changed)
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'case.xml'; p.write_text(changed,encoding='utf-8')
            return {i['code'] for i in audit(p)}

    def test_type_condition_required(self):
        self.assertIn('condition_schema_order',self.codes(lambda s:s.replace('(type Y container)','',1)))

    def test_container_field_order(self):
        self.assertIn('environment_field_order',self.codes(lambda s:re.sub(r'(\(at 4 \d+\)) (\(type 4 container\))',r'\2 \1',s,count=1)))

    def test_condition_order(self):
        self.assertIn('condition_schema_order',self.codes(lambda s:re.sub(r'(\(sort X book\))(\(color X white\))',r'\2\1',s,count=1)))

    def test_human_id(self):
        self.assertIn('parse_state_alignment',self.codes(lambda s:s.replace('(sort 1 human)','(sort 1 chair)',1)))

    def test_nonconsecutive_id(self):
        self.assertIn('parse_state_alignment',self.codes(lambda s:s.replace('(sort 14 bottle)','(sort 18 bottle)',1)))

    def test_missing_color(self):
        self.assertIn('parse_state_alignment',self.codes(lambda s:s.replace('(color 11 white)','',1)))

    def test_wrong_field_object_id(self):
        self.assertIn('parse_state_alignment',self.codes(lambda s:s.replace('(size 6 big)','(size 5 big)',1)))

    def test_big_location_collision(self):
        def mutate(s):
            loc=re.search(r'\(at 7 (\d+)\)',s)[1]
            return re.sub(r'\(at 6 \d+\)',f'(at 6 {loc})',s,count=1)
        self.assertIn('big_position_collision',self.codes(mutate))

    def test_washmachine_container(self):
        self.assertIn('container_type',self.codes(lambda s:s.replace('microwave','washmachine')))

    def test_please_rejected(self):
        self.assertIn('parse_state_alignment',self.codes(lambda s:s.replace('Give the','Please give the',1)))

    def test_goal_count(self):
        def mutate(s):
            root=ET.fromstring(s)
            root.find('instr').text=root.findtext('instr').replace('(:ins','(:ins\n(:task (open X) (:cond (sort X microwave)(type X container)))',1)
            root.find('nl').text='\nOpen the microwave.\n'+root.findtext('nl')
            return ET.tostring(root,encoding='unicode')
        self.assertIn('task_count',self.codes(mutate))

    def test_two_small_relation(self):
        def mutate(s):
            root=ET.fromstring(s)
            root.find('instr').text=root.findtext('instr').replace('(:ins','(:ins\n(:cons_not (:info (near X Y) (:cond (sort X can)(color X red)(sort Y cup)(color Y white))))',1)
            root.find('nl').text='\nThe red can must not be near the white cup.\n'+root.findtext('nl')
            return ET.tostring(root,encoding='unicode')
        self.assertTrue({'two_small_objects','color_Y','relation_types'} <= self.codes(mutate))

if __name__=='__main__': unittest.main()
