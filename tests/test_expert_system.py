import unittest
import json
from app import create_app, db
from app.utils.helpers import get_advisor
from app.expert_system.advisor import PhoneRepairAdvisor
from app.models.rule import Rule as RuleModel
from app.models.issue import Issue, Symptom
from app.models.repair import Repair

class TestExpertSystem(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.seed_symptoms_and_issues()
        self.seed_rules()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def seed_symptoms_and_issues(self):
        symptoms_data = [
            ('screen_cracked', 'Screen is cracked or shattered', 'Is your screen cracked?'),
            ('screen_black', 'Screen is completely black', 'Is the screen completely black?'),
            ('test_symptom', 'A test symptom', 'Is this a test?'),
        ]
        for code, desc, question in symptoms_data:
            db.session.add(Symptom(code=code, description=desc, question=question))
        
        issues_data = [
            {'category': 'Screen', 'name': 'Glass Damage', 'description': 'Only the glass is cracked, LCD is fine', 'severity': 'Medium'},
            {'category': 'Screen', 'name': 'LCD Damage', 'description': 'LCD screen is damaged and needs replacement', 'severity': 'High'},
        ]
        for i_data in issues_data:
            db.session.add(Issue(**i_data))
        db.session.commit()

        repairs_data = [
            {'issue_id': 1, 'solution': 'Replace front glass only'},
            {'issue_id': 2, 'solution': 'Replace entire screen assembly (LCD + glass)'},
        ]
        for r_data in repairs_data:
            db.session.add(Repair(**r_data))
        db.session.commit()

        issue_symptom_mapping = {
            'Glass Damage': ['screen_cracked'],
            'LCD Damage': ['screen_black'],
        }
        for issue_name, symptom_codes in issue_symptom_mapping.items():
            issue = Issue.query.filter_by(name=issue_name).first()
            if issue:
                for code in symptom_codes:
                    symptom = Symptom.query.filter_by(code=code).first()
                    if symptom:
                        issue.symptoms.append(symptom)
        db.session.commit()

    def seed_rules(self):
        rules_data = [
            {
                "name": "Diagnose Cracked Screen - Glass Damage",
                "conditions": [
                    {"function": "symptom_is_present", "args": {"symptom_code": "screen_cracked"}}
                ],
                "actions": [
                    {"function": "set_diagnosis", "args": {
                        "diagnosis_code": "Glass Damage",
                        "category": "Screen",
                        "severity": "Medium", # Added severity
                        "confidence": 0.9
                    }}
                ],
                "priority": 10,
                "confidence": 0.9
            },
            {
                "name": "Diagnose Cracked Screen - LCD Damage",
                "conditions": [
                    {"function": "symptom_is_present", "args": {"symptom_code": "screen_black"}}
                ],
                "actions": [
                    {"function": "set_diagnosis", "args": {
                        "diagnosis_code": "LCD Damage",
                        "category": "Screen",
                        "severity": "High", # Added severity
                        "confidence": 0.95
                    }}
                ],
                "priority": 11,
                "confidence": 0.95
            },
            { # This rule will be used for test_rule_reloading
                "name": "Diagnose Test Rule",
                "conditions": [
                    {"function": "symptom_is_present", "args": {"symptom_code": "test_symptom"}}
                ],
                "actions": [
                    {"function": "set_diagnosis", "args": {
                        "diagnosis_code": "Test Diagnosis",
                        "category": "Test",
                        "severity": "Low", # Added severity
                        "confidence": 1.0
                    }}
                ],
                "priority": 12,
                "confidence": 1.0
            }
        ]
        for rule_data in rules_data:
            # The conditions and actions are already JSON objects,
            # but RuleModel expects them as strings, so we dump them again.
            rule_data['conditions'] = json.dumps(rule_data['conditions'])
            rule_data['actions'] = json.dumps(rule_data['actions'])
            rule = RuleModel(**rule_data)
            db.session.add(rule)
        db.session.commit()

    def test_diagnosis_glass_damage(self):
        with self.app.test_request_context():
            advisor = get_advisor()
            symptoms = {'screen_cracked': True}
            result = advisor.diagnose(symptoms)
            self.assertEqual(result['diagnosis'], 'Glass Damage')
            self.assertEqual(result['confidence'], 0.9)
            self.assertGreater(len(result['recommendations']), 0)
            self.assertEqual(result['recommendations'][0]['solution'], 'Replace front glass only')

    def test_diagnosis_lcd_damage(self):
        with self.app.test_request_context():
            advisor = get_advisor()
            symptoms = {'screen_black': True}
            result = advisor.diagnose(symptoms)
            self.assertEqual(result['diagnosis'], 'LCD Damage')
            self.assertEqual(result['confidence'], 0.95)
            self.assertGreater(len(result['recommendations']), 0)
            self.assertEqual(result['recommendations'][0]['solution'], 'Replace entire screen assembly (LCD + glass)')

    def test_rule_reloading(self):
        with self.app.test_request_context():
            # 1. Run diagnosis
            advisor = get_advisor()
            symptoms = {'screen_cracked': True}
            result = advisor.diagnose(symptoms)
            self.assertEqual(result['diagnosis'], 'Glass Damage')

            # 2. Add a new rule
            new_rule = {
                "name": "Diagnose Test Rule Reloaded", # Changed name to avoid conflict with seeded rule
                "conditions": [
                    {"function": "symptom_is_present", "args": {"symptom_code": "test_symptom"}}
                ],
                "actions": [
                    {"function": "set_diagnosis", "args": {
                        "diagnosis_code": "Test Diagnosis Reloaded",
                        "category": "Test",
                        "severity": "High", # Added severity
                        "confidence": 1.0
                    }}
                ],
                "priority": 12,
                "confidence": 1.0
            }
            db.session.add(RuleModel(
                name=new_rule['name'],
                conditions=json.dumps(new_rule['conditions']),
                actions=json.dumps(new_rule['actions']),
                priority=new_rule['priority'],
                confidence=new_rule['confidence']
            ))
            db.session.commit()

            # 3. Run diagnosis again
            advisor_reloaded = get_advisor()
            symptoms = {'test_symptom': True}
            result = advisor_reloaded.diagnose(symptoms)
            self.assertEqual(result['diagnosis'], 'Test Diagnosis Reloaded')

if __name__ == '__main__':
    unittest.main()