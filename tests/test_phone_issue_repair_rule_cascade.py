import json
from app import create_app, db
from app.models.phone import Phone
from app.models.issue import Issue, Symptom
from app.models.repair import Repair
from app.models.rule import Rule


def test_phone_issue_repair_rule_cascade(tmp_path):
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Create a phone, issue, symptom, repair, and rule linking to repair
        p = Phone(brand='TestBrand', model='X', release_year=2022)
        db.session.add(p)
        db.session.commit()

        s = Symptom(code='S1', description='symptom 1')
        db.session.add(s)
        db.session.commit()

        issue = Issue(phone_id=p.id, category='Screen', name='Screen crack')
        issue.symptoms = [s]
        db.session.add(issue)
        db.session.commit()

        repair = Repair(issue_id=issue.id, solution='Replace screen')
        db.session.add(repair)
        db.session.commit()

        rule = Rule(name='rule-1', conditions=[{"function": "fact_equals"}], actions=[{"function": "set_diagnosis"}], repair_id=repair.id)
        db.session.add(rule)
        db.session.commit()

        # Sanity checks
        assert Phone.query.get(p.id) is not None
        assert Issue.query.get(issue.id) is not None
        assert Repair.query.get(repair.id) is not None
        r = Rule.query.get(rule.id)
        assert r is not None and r.repair_id == repair.id

        # Delete the phone -> issues and repairs should be removed, rules should remain with repair_id NULL
        db.session.delete(p)
        db.session.commit()

        assert Phone.query.get(p.id) is None
        assert Issue.query.get(issue.id) is None
        assert Repair.query.get(repair.id) is None

        r = Rule.query.get(rule.id)
        assert r is not None
        assert r.repair_id is None

        # Clean up
        db.session.remove()
        db.drop_all()
