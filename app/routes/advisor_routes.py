from flask import Blueprint, render_template, request, jsonify, session, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.repair import RepairRequest
from app.models.phone import Phone
# Import the Issue and Symptom model
from app.models.issue import Issue, Symptom
from app import db
from utils.constants import SYMPTOMS  # Keep for now, might be removed later
import json
from app.utils.helpers import get_advisor  # Import get_advisor

advisor_bp = Blueprint('advisor', __name__)


@advisor_bp.route('/diagnose', methods=['GET', 'POST'])
@login_required
def diagnose():
    """Main diagnosis interface"""
    if request.method == 'POST':
        # Get form data
        phone_brand = request.form.get('phone_brand')
        phone_model = request.form.get('phone_model')

        # Get selected symptoms from Symptom models
        selected_symptom_codes = request.form.getlist('symptom_codes')

        # Retrieve all possible symptoms from the database
        all_symptoms = Symptom.query.all()
        
        # Initialize a dictionary with all symptoms set to False
        processed_symptoms = {symptom.code: False for symptom in all_symptoms}

        # Set selected symptoms to True
        for code in selected_symptom_codes:
            if code in processed_symptoms:
                processed_symptoms[code] = True

        # Create advisor and run diagnosis
        advisor = get_advisor()
        result = advisor.diagnose(processed_symptoms, phone_brand, phone_model)

        # Save to database
        repair_request = RepairRequest(
            user_id=current_user.id,
            phone_brand=phone_brand,
            phone_model=phone_model,
            symptoms_json=json.dumps(processed_symptoms),
            diagnosis_json=json.dumps(result),  # Save diagnosis result
            status='diagnosed'
        )
        db.session.add(repair_request)
        db.session.commit()

        # Store in session for result page
        session['diagnosis_result'] = result
        session['repair_request_id'] = repair_request.id

        # Debug print
        print(f"DEBUG: Diagnosis result being passed to template: {result}")

        return render_template('advisor/result.html',
                               result=result,
                               phone_brand=phone_brand,
                               phone_model=phone_model)

    # Get unique phone brands for the dropdown
    phone_brands = [
        brand for brand,
        in db.session.query(
            Phone.brand).distinct().order_by(
            Phone.brand).all()]
    print(f"Phone Brands fetched: {phone_brands}")
    # Get all symptoms for symptom selection
    all_symptoms = Symptom.query.order_by(Symptom.description).all()

    return render_template('advisor/diagnose.html',
                           symptoms=all_symptoms, phone_brands=phone_brands)


@advisor_bp.route('/add_phone_user', methods=['GET', 'POST'])
@login_required
def add_phone_user():
    """Add new phone model from the user interface"""
    from flask import flash
    from datetime import datetime
    current_year = datetime.now().year

    if request.method == 'POST':
        brand = request.form.get('brand')
        model = request.form.get('model')
        release_year_str = request.form.get('release_year')
        screen_size_str = request.form.get('screen_size')
        battery_capacity_str = request.form.get('battery_capacity')
        waterproof_rating = request.form.get('waterproof_rating')
        has_wireless_charging = bool(request.form.get('has_wireless_charging'))

        errors = []

        if not brand:
            errors.append('Brand is required.')
        if not model:
            errors.append('Model is required.')

        try:
            release_year = int(release_year_str)
            if not (1900 <= release_year <= current_year):
                errors.append(
                    f'Release year must be between 1900 and {current_year}.')
        except (ValueError, TypeError):
            errors.append('Release year must be a valid number.')
            release_year = None  # Ensure it's None if invalid

        try:
            screen_size = float(screen_size_str)
            if not screen_size > 0:
                errors.append('Screen size must be a positive number.')
        except (ValueError, TypeError):
            errors.append('Screen size must be a valid number.')
            screen_size = None  # Ensure it's None if invalid

        try:
            battery_capacity = int(battery_capacity_str)
            if not battery_capacity > 0:
                errors.append('Battery capacity must be a positive number.')
        except (ValueError, TypeError):
            errors.append('Battery capacity must be a valid number.')
            battery_capacity = None  # Ensure it's None if invalid

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'admin/add_phone.html', current_year=current_year, form_data=request.form)

        phone = Phone(
            brand=brand,
            model=model,
            release_year=release_year,
            screen_size=screen_size,
            battery_capacity=battery_capacity,
            waterproof_rating=waterproof_rating,
            has_wireless_charging=has_wireless_charging
        )
        db.session.add(phone)
        db.session.commit()
        flash(
            'Phone added successfully! You can now select it for diagnosis.',
            'success')
        return redirect(url_for('advisor.diagnose'))

    return render_template('admin/add_phone.html', current_year=current_year)


@advisor_bp.route('/api/phone_models/<string:brand>', methods=['GET'])
def get_phone_models_by_brand(brand):
    """API endpoint to get phone models for a given brand"""
    models = Phone.query.filter_by(brand=brand).order_by(Phone.model).all()
    model_list = [{'id': model.id, 'name': model.model} for model in models]
    return jsonify(model_list)


@advisor_bp.route('/api/diagnose', methods=['POST'])
@login_required
def api_diagnose():
    """API endpoint for diagnosis"""
    data = request.get_json()

    symptoms = data.get('symptoms', {})
    phone_brand = data.get('phone_brand')
    phone_model = data.get('phone_model')

    advisor = get_advisor()
    result = advisor.diagnose(symptoms, phone_brand, phone_model)

    # Add cost estimate
    result['cost_estimate'] = advisor.get_cost_estimate(
        result['diagnosis'],
        phone_brand
    )

    # Add prevention tips
    result['prevention_tips'] = advisor.get_prevention_tips(
        result['diagnosis'])

    return jsonify(result)


@advisor_bp.route('/history')
@login_required
def history():
    """View diagnosis history"""
    requests = RepairRequest.query.filter_by(user_id=current_user.id)\
        .order_by(RepairRequest.created_at.desc())\
        .all()

    return render_template('advisor/history.html', requests=requests)


@advisor_bp.route('/request/<int:request_id>')
@login_required
def view_request(request_id):
    """View specific repair request"""
    repair_request = RepairRequest.query.get_or_404(request_id)

    # Check authorization
    if repair_request.user_id != current_user.id and not current_user.has_permission(
            'view_all_requests'):
        return "Unauthorized", 403

    symptoms = json.loads(
        repair_request.symptoms_json) if repair_request.symptoms_json else {}

    return render_template('advisor/view_request.html',
                           request=repair_request,
                           symptoms=symptoms)
