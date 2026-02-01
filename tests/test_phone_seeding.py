def test_curated_phones_seeded(app):
    from app import db
    from app.models.phone import Phone
    from app.seeding.seed_data import seed_all_data
    from app.seeding.standardize_data import run_standardize

    # Create tables in the test DB and ensure a clean state for this test run
    db.create_all()
    db.session.query(Phone).delete()
    db.session.commit()

    seed_all_data()
    run_standardize()

    phones = Phone.query.all()
    names = {(p.brand, p.model, p.release_year) for p in phones}

    # Clean up after test
    db.session.remove()
    db.drop_all()

    expected = {
        ('Apple', 'iPhone 14', 2021),
        ('Google', 'Pixel 7', 2020),
        ('Google', 'Pixel 8 Pro', 2022),
        ('Google', 'Pixel Fold', 2022),
        ('Huawei', 'Mate 50 Pro', 2017),
        ('Huawei', 'Nova 11 Pro', 2020),
        ('OnePlus', 'OnePlus Open', 2022),
        ('Sony', 'Xperia 1 V', 2022),
        ('Sony', 'Xperia 1 V', 2023),
        ('Xiaomi', 'Xiaomi 13', 2024),
    }

    for e in expected:
        assert e in names, f"Expected curated phone {e} to be present in seeded phones"