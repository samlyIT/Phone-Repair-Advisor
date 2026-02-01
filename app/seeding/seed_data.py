import random
from faker import Faker
from app import db
from app.models.issue import Symptom, Issue
from app.models.repair import Repair
from app.models.rule import Rule
from app.models.phone import Phone # Import the Phone model
from app.models.associations import issue_symptoms
from datetime import datetime, timedelta

fake = Faker()

def generate_phones(num_phones=15): # Generate a curated set of phones plus random extras
    phones = []

    # Curated models requested and enriched attributes
    curated_phones = [
        {'brand': 'Apple', 'model': 'iPhone 14', 'release_year': 2021, 'screen_size': 6.1, 'battery_capacity': 3279, 'waterproof_rating': 'IP68', 'has_wireless_charging': True},
        {'brand': 'Google', 'model': 'Pixel 7', 'release_year': 2020, 'screen_size': 6.3, 'battery_capacity': 4355, 'waterproof_rating': 'IP68', 'has_wireless_charging': True},
        {'brand': 'Google', 'model': 'Pixel 8 Pro', 'release_year': 2022, 'screen_size': 6.7, 'battery_capacity': 5050, 'waterproof_rating': 'IP68', 'has_wireless_charging': True},
        {'brand': 'Google', 'model': 'Pixel Fold', 'release_year': 2022, 'screen_size': 7.6, 'battery_capacity': 4800, 'waterproof_rating': 'IPX8', 'has_wireless_charging': True},
        {'brand': 'Huawei', 'model': 'Mate 50 Pro', 'release_year': 2017, 'screen_size': 6.74, 'battery_capacity': 4700, 'waterproof_rating': 'IP68', 'has_wireless_charging': False},
        {'brand': 'Huawei', 'model': 'Nova 11 Pro', 'release_year': 2020, 'screen_size': 6.67, 'battery_capacity': 4500, 'waterproof_rating': 'IP53', 'has_wireless_charging': False},
        {'brand': 'OnePlus', 'model': 'OnePlus Open', 'release_year': 2022, 'screen_size': 7.8, 'battery_capacity': 5000, 'waterproof_rating': 'IPX4', 'has_wireless_charging': True},
        {'brand': 'Sony', 'model': 'Xperia 1 V', 'release_year': 2022, 'screen_size': 6.5, 'battery_capacity': 5000, 'waterproof_rating': 'IP65', 'has_wireless_charging': False},
        {'brand': 'Sony', 'model': 'Xperia 1 V', 'release_year': 2023, 'screen_size': 6.5, 'battery_capacity': 5050, 'waterproof_rating': 'IP65', 'has_wireless_charging': False},
        {'brand': 'Xiaomi', 'model': 'Xiaomi 13', 'release_year': 2024, 'screen_size': 6.36, 'battery_capacity': 4500, 'waterproof_rating': 'IP68', 'has_wireless_charging': True},
    ]

    for item in curated_phones:
        phone = Phone(
            brand=item['brand'],
            model=item['model'],
            release_year=item.get('release_year'),
            screen_size=item.get('screen_size'),
            battery_capacity=item.get('battery_capacity'),
            waterproof_rating=item.get('waterproof_rating'),
            has_wireless_charging=item.get('has_wireless_charging', False),
            serial_number=fake.uuid4(),
            imei=fake.bothify(text='############'),
            storage_gb=random.choice([64, 128, 256, 512]),
            color=fake.color_name(),
            price=round(random.uniform(300, 1500), 2),
            created_at=fake.date_time_between(start_date="-3y", end_date="now")
        )
        phones.append(phone)

    # Add random phones to reach requested count
    brands = ['Apple', 'Samsung', 'Google', 'OnePlus', 'Xiaomi', 'Huawei', 'Motorola', 'Sony', 'LG', 'Nokia']
    models_by_brand = {
        'Apple': ['iPhone 12', 'iPhone 13', 'iPhone 15', 'iPhone SE'],
        'Samsung': ['Galaxy S21', 'Galaxy S22', 'Galaxy S23', 'Galaxy S24', 'Galaxy A54', 'Galaxy Fold5'],
        'Google': ['Pixel 6', 'Pixel 8', 'Pixel 8 Pro'],
        'OnePlus': ['OnePlus 9', 'OnePlus 10', 'OnePlus 11'],
        'Xiaomi': ['Redmi Note 10', 'Xiaomi 12', 'POCO F5'],
        'Huawei': ['P40 Pro'],
        'Motorola': ['Moto G Power', 'Edge+'],
        'Sony': ['Xperia 5 V'],
        'LG': ['Wing'],
        'Nokia': ['X20', 'G400']
    }

    while len(phones) < num_phones:
        brand = random.choice(brands)
        model = random.choice(models_by_brand.get(brand, ['Unknown']))
        phone = Phone(
            brand=brand,
            model=model,
            release_year=random.randint(2017, 2024),
            screen_size=round(random.uniform(5.5, 7.8), 2),
            battery_capacity=random.choice([3000, 3500, 4000, 4500, 5000]),
            waterproof_rating=random.choice(['N/A', 'IP53', 'IP65', 'IP68', 'IPX4']),
            has_wireless_charging=random.choice([True, False]),
            serial_number=fake.uuid4(),
            imei=fake.bothify(text='############'),
            storage_gb=random.choice([64, 128, 256, 512]),
            color=fake.color_name(),
            price=round(random.uniform(200, 1500), 2),
            created_at=fake.date_time_between(start_date="-3y", end_date="now")
        )
        phones.append(phone)

    db.session.add_all(phones)
    db.session.commit()
    return phones


def generate_symptoms(num_symptoms=25):
    symptoms = []
    for i in range(num_symptoms):
        symptom_code = f"SYM{i+1:03d}"
        description = fake.sentence(nb_words=6, variable_nb_words=True) + " issue."
        question = fake.sentence(nb_words=10, variable_nb_words=True) + "?"
        symptoms.append(Symptom(code=symptom_code, description=description, question=question))
    db.session.add_all(symptoms)
    db.session.commit()
    return symptoms

def generate_issues(symptoms, phones, num_issues=25): # Modified to accept phones
    issues = []
    categories = ['Screen', 'Battery', 'Charging', 'Software', 'Camera', 'Audio']
    severities = ['Low', 'Medium', 'High', 'Critical']

    for i in range(num_issues):
        issue_name = fake.catch_phrase() + " Failure"
        description = fake.paragraph(nb_sentences=3, variable_nb_sentences=True)
        issue = Issue(
            phone_id=random.choice(phones).id, # Link to actual phone ID
            category=random.choice(categories),
            name=issue_name,
            description=description,
            severity=random.choice(severities),
            created_at=fake.date_time_between(start_date="-2y", end_date="now")
        )
        # Add the issue to the session BEFORE linking symptoms so relationship operations occur on-session
        db.session.add(issue)
        # Link 1-3 random symptoms to each issue
        num_linked_symptoms = random.randint(1, 3)
        issue.symptoms = random.sample(symptoms, min(num_linked_symptoms, len(symptoms)))
        issues.append(issue)
    db.session.add_all(issues)
    db.session.commit()
    return issues

def generate_repairs(issues, num_repairs=25):
    repairs = []
    difficulties = ['Easy', 'Medium', 'Hard', 'Expert']

    for i in range(num_repairs):
        issue = random.choice(issues)
        solution = fake.paragraph(nb_sentences=5, variable_nb_sentences=True)
        parts_needed = ", ".join(fake.words(nb=random.randint(1, 4)))
        tools_needed = ", ".join(fake.words(nb=random.randint(1, 3)))
        repair = Repair(
            issue_id=issue.id,
            solution=solution,
            estimated_cost_min=round(random.uniform(10, 100), 2),
            estimated_cost_max=round(random.uniform(100, 500), 2),
            estimated_time_hours=round(random.uniform(0.5, 8), 1),
            difficulty=random.choice(difficulties),
            parts_needed=parts_needed,
            tools_needed=tools_needed,
            warranty_affected=fake.boolean(),
            priority=random.randint(1, 10),
            created_at=fake.date_time_between(start_date="-1y", end_date="now")
        )
        repairs.append(repair)
    db.session.add_all(repairs)
    db.session.commit()
    return repairs

def generate_rules(repairs, num_rules=25):
    rules = []
    for i in range(num_rules):
        repair = random.choice(repairs)
        # To access issue properties from repair, ensure issue relationship is loaded
        # For simplicity, we'll assume the repair object has its issue loaded.
        # In a more complex scenario, you might need to query the issue explicitly or use joinedload.
        
        # Example conditions based on issue/symptom related to the repair
        conditions = []
        
        issue_for_rule = Issue.query.get(repair.issue_id) if not hasattr(repair, 'issue') or not repair.issue else repair.issue

        if issue_for_rule:
            conditions.append({
                "function": "fact_equals",
                "args": {"fact_name": "category", "expected_value": issue_for_rule.category}
            })
            conditions.append({
                "function": "fact_equals",
                "args": {"fact_name": "severity", "expected_value": issue_for_rule.severity}
            })
            if issue_for_rule.symptoms:
                conditions.append({
                    "function": "symptom_is_present",
                    "args": {"symptom_code": random.choice([s.code for s in issue_for_rule.symptoms])}
                })
        else:
            # Fallback condition if no issue is linked
            conditions.append({
                "function": "fact_equals",
                "args": {"fact_name": "repair_id", "expected_value": repair.id}
            })

        # If there are multiple conditions, wrap them in an "AND" operator.
        # If there's only one, or none, use the list directly.
        if len(conditions) > 1:
            conditions = [{"function": "AND", "args": {"conditions": conditions}}]
        elif len(conditions) == 0:
            conditions = [] # Ensure it's an empty list if no conditions were added
        # If len(conditions) == 1, it's already a list with one item, so no change needed.

        actions = [
            {
                "function": "set_diagnosis",
                "args": {
                    "diagnosis_code": issue_for_rule.name if issue_for_rule else "UNKNOWN_ISSUE",
                    "category": issue_for_rule.category if issue_for_rule else "Unknown",
                    "severity": issue_for_rule.severity if issue_for_rule else "Unknown",
                    "confidence": round(random.uniform(0.7, 1.0), 2),
                    "explanation": f"Diagnosed based on conditions related to {issue_for_rule.name if issue_for_rule else 'an issue'} and recommending repair ID {repair.id}"
                }
            },
            {
                "function": "add_to_working_memory",
                "args": {
                    "key": "recommended_repair_id",
                    "value": repair.id
                }
            }
        ]
        
        rule = Rule(
            name=f"Rule for {issue_for_rule.name if issue_for_rule else 'Repair ID ' + str(repair.id)} - {fake.unique.word()} strategy - {fake.uuid4()}",
            conditions=conditions,
            actions=actions,
            priority=random.randint(1, 10),
            confidence=round(random.uniform(0.5, 1.0), 2),
            description=fake.sentence(nb_words=10, variable_nb_words=True),
            repair_id=repair.id, # Link rule to repair
            created_at=fake.date_time_between(start_date="-6m", end_date="now")
        )
        rules.append(rule)
    db.session.add_all(rules)
    db.session.commit()
    return rules

def seed_all_data():
    print("Seeding database with sample data...")
    all_phones = generate_phones() # Generate phones first
    print(f"Generated {len(all_phones)} phones.")

    all_symptoms = generate_symptoms()
    print(f"Generated {len(all_symptoms)} symptoms.")
    
    # Pass all_phones to generate_issues
    all_issues = generate_issues(all_symptoms, all_phones) 
    print(f"Generated {len(all_issues)} issues.")
    
    # Repairs need existing issues
    all_repairs = generate_repairs(all_issues)
    print(f"Generated {len(all_repairs)} repairs.")
    
    # Rules need existing repairs
    all_rules = generate_rules(all_repairs)
    print(f"Generated {len(all_rules)} rules.")
    print("Seeding complete.")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        print("Clearing existing data...")
        # Clear data in reverse order of dependency
        db.session.query(Rule).delete()
        db.session.query(Repair).delete()
        db.session.execute(issue_symptoms.delete()) # Clear association table
        db.session.query(Issue).delete()
        db.session.query(Symptom).delete()
        db.session.query(Phone).delete() # Add Phone to clearing
        db.session.commit()
        print("Existing data cleared.")
        seed_all_data()