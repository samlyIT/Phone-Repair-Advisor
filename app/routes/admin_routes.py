from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
import json
from app.models.phone import Phone
from app.models.issue import Issue, Symptom
from app.models.repair import Repair
from app.models.user import User
from app.models.role import Role
from app.models.rule import Rule
from app import db
from app.utils.helpers import get_advisor

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin permission"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_permission(
                'admin_access'):
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('advisor.diagnose'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    stats = {
        'total_users': User.query.count(),
        'total_phones': Phone.query.count(),
        'total_issues': Issue.query.count(),
        'total_repairs': Repair.query.count(),
        'total_rules': Rule.query.count(),
        'total_symptoms': Symptom.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role_id = request.form.get('role_id')

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('admin.add_user'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('admin.add_user'))

        # Create new user
        user = User(username=username, email=email, full_name=full_name, role_id=role_id)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('User added successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    roles = Role.query.all()
    return render_template('admin/add_user.html', roles=roles)


@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit existing user"""
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.full_name = request.form.get('full_name')
        user.role_id = request.form.get('role_id')
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/edit_user.html', user=user, roles=roles)


@admin_bp.route('/users/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def change_password(user_id):
    """Change user password"""
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('admin.change_password', user_id=user.id))

        user.set_password(password)
        db.session.commit()
        flash('Password updated successfully!', 'success')
        return redirect(url_for('admin.edit_user', user_id=user.id))

    return render_template('admin/change_password.html', user=user)


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/phones')
@login_required
@admin_required
def manage_phones():
    """Manage phone models"""
    phones = Phone.query.order_by(Phone.brand, Phone.model).all()
    return render_template('admin/phones.html', phones=phones)


@admin_bp.route('/phones/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_phone():
    """Add new phone model"""
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
        flash('Phone added successfully!', 'success')
        return redirect(url_for('admin.manage_phones'))

    return render_template('admin/add_phone.html', current_year=current_year)


@admin_bp.route('/phones/edit/<int:phone_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_phone(phone_id):
    """Edit existing phone model"""
    phone = Phone.query.get_or_404(phone_id)
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
                'admin/edit_phone.html', current_year=current_year, phone=phone)

        phone.brand = brand
        phone.model = model
        phone.release_year = release_year
        phone.screen_size = screen_size
        phone.battery_capacity = battery_capacity
        phone.waterproof_rating = waterproof_rating
        phone.has_wireless_charging = has_wireless_charging

        db.session.commit()
        flash('Phone updated successfully!', 'success')
        return redirect(url_for('admin.manage_phones'))

    return render_template('admin/edit_phone.html',
                           current_year=current_year, phone=phone)


@admin_bp.route('/phones/delete/<int:phone_id>', methods=['POST'])
@login_required
@admin_required
def delete_phone(phone_id):
    """Delete a phone model"""
    phone = Phone.query.get_or_404(phone_id)
    db.session.delete(phone)
    db.session.commit()
    flash('Phone deleted successfully!', 'success')
    return redirect(url_for('admin.manage_phones'))


@admin_bp.route('/issues')
@login_required
@admin_required
def manage_issues():
    """Manage phone issues"""
    issues = Issue.query.order_by(Issue.category, Issue.name).all()
    return render_template('admin/issues.html', issues=issues)


@admin_bp.route('/issues/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_issue():
    """Add new issue"""
    phones = Phone.query.order_by(Phone.brand, Phone.model).all()
    symptoms_list = Symptom.query.order_by(Symptom.code).all()

    if request.method == 'POST':
        phone_id = request.form.get('phone_id', type=int)
        selected_symptom_ids = request.form.getlist('symptom_ids')

        errors = []
        if not request.form.get('category'):
            errors.append('Category is required.')
        if not request.form.get('name'):
            errors.append('Name is required.')
        if not selected_symptom_ids:
            errors.append('At least one symptom must be selected for the issue.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'admin/add_issue.html', phones=phones, symptoms=symptoms_list, form_data=request.form)

        issue = Issue(
            phone_id=phone_id,
            category=request.form.get('category'),
            name=request.form.get('name'),
            description=request.form.get('description'),
            severity=request.form.get('severity')
        )

        # Associate selected symptoms
        if selected_symptom_ids:
            selected_symptoms = Symptom.query.filter(Symptom.id.in_(selected_symptom_ids)).all()
            issue.symptoms = selected_symptoms

        db.session.add(issue)
        db.session.commit()
        flash('Issue added successfully!', 'success')
        return redirect(url_for('admin.manage_issues'))

    return render_template('admin/add_issue.html', phones=phones, symptoms=symptoms_list)


@admin_bp.route('/issues/edit/<int:issue_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_issue(issue_id):
    """Edit existing issue"""
    issue = Issue.query.get_or_404(issue_id)
    phones = Phone.query.order_by(Phone.brand, Phone.model).all()
    symptoms_list = Symptom.query.order_by(Symptom.code).all()

    if request.method == 'POST':
        issue.phone_id = request.form.get('phone_id', type=int)
        issue.category = request.form.get('category')
        issue.name = request.form.get('name')
        issue.description = request.form.get('description')
        issue.severity = request.form.get('severity')

        selected_symptom_ids = request.form.getlist('symptom_ids')
        if selected_symptom_ids:
            issue.symptoms = Symptom.query.filter(Symptom.id.in_(selected_symptom_ids)).all()
        else:
            issue.symptoms = []

        db.session.commit()
        flash('Issue updated successfully!', 'success')
        return redirect(url_for('admin.manage_issues'))

    return render_template('admin/edit_issue.html', issue=issue, phones=phones, symptoms=symptoms_list)


@admin_bp.route('/issues/delete/<int:issue_id>', methods=['POST'])
@login_required
@admin_required
def delete_issue(issue_id):
    """Delete an issue"""
    issue = Issue.query.get_or_404(issue_id)
    db.session.delete(issue)
    db.session.commit()
    flash('Issue deleted successfully!', 'success')
    return redirect(url_for('admin.manage_issues'))


@admin_bp.route('/repairs')
@login_required
@admin_required
def manage_repairs():
    """Manage repair solutions"""
    repairs = Repair.query.order_by(
        Repair.issue_id, Repair.priority.desc()).all()
    return render_template('admin/repairs.html', repairs=repairs)


@admin_bp.route('/repairs/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_repair():
    """Add new repair solution"""
    if request.method == 'POST':
        repair = Repair(
            issue_id=request.form.get('issue_id', type=int),
            solution=request.form.get('solution'),
            estimated_cost_min=request.form.get(
                'estimated_cost_min', type=float),
            estimated_cost_max=request.form.get(
                'estimated_cost_max', type=float),
            estimated_time_hours=request.form.get(
                'estimated_time_hours', type=float),
            difficulty=request.form.get('difficulty'),
            parts_needed=request.form.get('parts_needed'),
            tools_needed=request.form.get('tools_needed'),
            warranty_affected=bool(request.form.get('warranty_affected')),
            priority=request.form.get('priority', type=int, default=1)
        )
        db.session.add(repair)
        db.session.commit()
        flash('Repair solution added successfully!', 'success')
        return redirect(url_for('admin.manage_repairs'))

    issues = Issue.query.all()
    return render_template('admin/add_repair.html', issues=issues)


@admin_bp.route('/repairs/edit/<int:repair_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_repair(repair_id):
    """Edit existing repair solution"""
    repair = Repair.query.get_or_404(repair_id)
    issues = Issue.query.all()
    if request.method == 'POST':
        repair.issue_id = request.form.get('issue_id', type=int)
        repair.solution = request.form.get('solution')
        repair.estimated_cost_min = request.form.get(
            'estimated_cost_min', type=float)
        repair.estimated_cost_max = request.form.get(
            'estimated_cost_max', type=float)
        repair.estimated_time_hours = request.form.get(
            'estimated_time_hours', type=float)
        repair.difficulty = request.form.get('difficulty')
        repair.parts_needed = request.form.get('parts_needed')
        repair.tools_needed = request.form.get('tools_needed')
        repair.warranty_affected = bool(request.form.get('warranty_affected'))
        repair.priority = request.form.get('priority', type=int, default=1)
        db.session.commit()
        flash('Repair solution updated successfully!', 'success')
        return redirect(url_for('admin.manage_repairs'))

    return render_template('admin/edit_repair.html',
                           repair=repair, issues=issues)


@admin_bp.route('/repairs/delete/<int:repair_id>', methods=['POST'])
@login_required
@admin_required
def delete_repair(repair_id):
    """Delete a repair solution"""
    repair = Repair.query.get_or_404(repair_id)
    db.session.delete(repair)
    db.session.commit()
    flash('Repair solution deleted successfully!', 'success')
    return redirect(url_for('admin.manage_repairs'))


@admin_bp.route('/manage_rules')
@login_required
@admin_required
def manage_rules():
    """View and manage expert system rules"""
    rules = Rule.query.order_by(Rule.priority.desc()).all()
    return render_template('admin/manage_rules.html', rules=rules)


@admin_bp.route('/rules/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_rule():
    """Add new expert system rule"""
    repairs = Repair.query.order_by(Repair.priority.desc()).all()

    if request.method == 'POST':
        name = request.form.get('name')
        conditions = request.form.get('conditions')
        actions = request.form.get('actions')
        priority = request.form.get('priority', type=int, default=1)
        confidence = request.form.get('confidence', type=float, default=1.0)
        description = request.form.get('description')
        repair_id = request.form.get('repair_id', type=int)

        # Basic validation for JSON and store as JSON objects
        try:
            conditions_obj = json.loads(conditions)
            actions_obj = json.loads(actions)
        except json.JSONDecodeError:
            flash('Conditions and Actions must be valid JSON.', 'danger')
            return render_template('admin/edit_rule.html', rule=request.form, repairs=repairs)

        new_rule = Rule(
            name=name,
            conditions=conditions_obj,
            actions=actions_obj,
            priority=priority,
            confidence=confidence,
            description=description,
            repair_id=repair_id
        )
        db.session.add(new_rule)
        db.session.commit()

        # Reload rules in the running application
        get_advisor().rule_engine.load_rules()

        flash(
            'Rule added successfully! The Rule Engine has been updated.',
            'success')
        return redirect(url_for('admin.manage_rules'))

    return render_template('admin/edit_rule.html', rule=None, repairs=repairs)


@admin_bp.route('/rules/edit/<int:rule_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_rule(rule_id):
    """Edit an existing expert system rule"""
    rule = Rule.query.get_or_404(rule_id)
    repairs = Repair.query.order_by(Repair.priority.desc()).all()

    if request.method == 'POST':
        rule.name = request.form.get('name')
        conditions = request.form.get('conditions')
        actions = request.form.get('actions')
        rule.priority = request.form.get(
            'priority', type=int, default=rule.priority)
        rule.confidence = request.form.get(
            'confidence', type=float, default=rule.confidence)
        rule.description = request.form.get('description')
        rule.repair_id = request.form.get('repair_id', type=int)

        # Basic validation for JSON and store as JSON objects
        try:
            rule.conditions = json.loads(conditions)
            rule.actions = json.loads(actions)
        except json.JSONDecodeError:
            flash('Conditions and Actions must be valid JSON.', 'danger')
            return render_template('admin/edit_rule.html', rule=rule, repairs=repairs)

        db.session.commit()

        # Reload rules in the running application
        get_advisor().rule_engine.load_rules()

        flash(
            'Rule updated successfully! The Rule Engine has been updated.',
            'success')
        return redirect(url_for('admin.manage_rules'))

    # Pre-populate form with existing rule data, formatted nicely
    try:
        rule.conditions = json.dumps(rule.conditions, indent=2) if rule.conditions else '[]'
        rule.actions = json.dumps(rule.actions, indent=2) if rule.actions else '[]'
    except (json.JSONDecodeError, TypeError):
        flash(
            'Warning: The conditions or actions for this rule are not valid JSON.',
            'warning')

    return render_template('admin/edit_rule.html', rule=rule, repairs=repairs)


@admin_bp.route('/rules/delete/<int:rule_id>', methods=['POST'])
@login_required
@admin_required
def delete_rule(rule_id):
    """Delete an expert system rule"""
    rule = Rule.query.get_or_404(rule_id)
    db.session.delete(rule)
    db.session.commit()

    # Reload rules in the running application
    get_advisor().rule_engine.load_rules()

    flash('Rule deleted successfully! The Rule Engine has been updated.', 'success')
    return redirect(url_for('admin.manage_rules'))


@admin_bp.route('/symptoms')
@login_required
@admin_required
def manage_symptoms():
    """Manage symptoms"""
    symptoms = Symptom.query.all()
    return render_template('admin/symptoms.html', symptoms=symptoms)


@admin_bp.route('/symptoms/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_symptom():
    """Add new symptom"""
    if request.method == 'POST':
        code = request.form.get('code')
        description = request.form.get('description')
        question = request.form.get('question')

        # Check if symptom exists
        if Symptom.query.filter_by(code=code).first():
            flash('Symptom code already exists', 'danger')
            return redirect(url_for('admin.add_symptom'))

        new_symptom = Symptom(
            code=code,
            description=description,
            question=question
        )
        db.session.add(new_symptom)
        db.session.commit()

        flash('Symptom added successfully!', 'success')
        return redirect(url_for('admin.manage_symptoms'))

    return render_template('admin/edit_symptom.html', symptom=None)


@admin_bp.route('/symptoms/edit/<int:symptom_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_symptom(symptom_id):
    """Edit an existing symptom"""
    symptom = Symptom.query.get_or_404(symptom_id)

    if request.method == 'POST':
        symptom.code = request.form.get('code')
        symptom.description = request.form.get('description')
        symptom.question = request.form.get('question')
        db.session.commit()
        flash('Symptom updated successfully!', 'success')
        return redirect(url_for('admin.manage_symptoms'))

    return render_template('admin/edit_symptom.html', symptom=symptom)


@admin_bp.route('/symptoms/delete/<int:symptom_id>', methods=['POST'])
@login_required
@admin_required
def delete_symptom(symptom_id):
    """Delete a symptom"""
    symptom = Symptom.query.get_or_404(symptom_id)
    db.session.delete(symptom)
    db.session.commit()
    flash('Symptom deleted successfully!', 'success')
    return redirect(url_for('admin.manage_symptoms'))