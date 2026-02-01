import unittest
from app import create_app, db
from app.models.phone import Phone
from app.models.issue import Issue, Symptom
from app.models.repair import Repair
from app.models.rule import Rule

class TestAdminRelationships(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_symptom_issue_repair_cascade_and_rule_link(self):
        # Create phone
        phone = Phone(brand='TestBrand', model='TestModel', release_year=2020)
        db.session.add(phone)
        db.session.commit()

        # Create symptoms
        s1 = Symptom(code='TEST001', description='Test symptom 1', question='Is it test?')
        s2 = Symptom(code='TEST002', description='Test symptom 2', question='Is it test2?')
        db.session.add_all([s1, s2])
        db.session.commit()

        # Create issue linked to phone and symptoms
        issue = Issue(phone_id=phone.id, category='Test', name='Test Issue', description='desc', severity='Low')
        issue.symptoms = [s1, s2]
        db.session.add(issue)
        db.session.commit()

        # Create repair linked to issue
        repair = Repair(issue_id=issue.id, solution='Do something')
        db.session.add(repair)
        db.session.commit()

        # Create rule linked to repair
        rule = Rule(name='Test Rule', conditions=[], actions=[], repair_id=repair.id)
        db.session.add(rule)
        db.session.commit()

        # Verify links
        self.assertIsNotNone(Issue.query.get(issue.id))
        self.assertEqual(len(issue.symptoms), 2)
        self.assertEqual(repair.issue_id, issue.id)
        self.assertEqual(rule.repair_id, repair.id)

        # Delete issue and ensure repair and rule are handled (cascade)
        db.session.delete(issue)
        db.session.commit()

        self.assertIsNone(Repair.query.get(repair.id), "Repair should be deleted when Issue is deleted (cascade)")
        # The rule was attached to the repair; since repair deleted, rule.repair_id should be null or rule deleted (depending on cascade)
        remaining_rule = Rule.query.filter_by(id=rule.id).first()
        # If rule still exists, repair_id should be None
        if remaining_rule:
            self.assertIsNone(remaining_rule.repair_id)

    def test_standardized_issues_have_phone(self):
        # Create some phones so the standardization can assign them to issues
        p1 = Phone(brand='TestBrandA', model='ModelA', release_year=2021)
        p2 = Phone(brand='TestBrandB', model='ModelB', release_year=2022)
        db.session.add_all([p1, p2])
        db.session.commit()

        # Run the standardization seeder that should attach phones to issues
        from app.seeding.standardize_data import seed_data
        seed_data()

        # Ensure no standardized Issue is left without a phone assignment
        issues_without_phone = Issue.query.filter(Issue.phone_id == None).count()
        self.assertEqual(issues_without_phone, 0, "All standardized issues should have a phone assigned")

if __name__ == '__main__':
    unittest.main()
