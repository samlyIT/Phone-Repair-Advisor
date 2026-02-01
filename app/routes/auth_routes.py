from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.role import Role
from app import db, login_manager
from app.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('advisor.diagnose'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))

        # Create new user
        user = User(username=form.username.data, email=form.email.data, full_name=form.full_name.data)
        user.set_password(form.password.data)

        # Assign default role
        default_role = Role.query.filter_by(name='user').first()
        if default_role:
            user.role = default_role

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('advisor.diagnose'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account is inactive. Please contact admin.', 'danger')
                return redirect(url_for('auth.login'))

            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            
            flash('Login successful!', 'success')

            if next_page:
                return redirect(next_page)
            if user.has_permission('admin_access'):
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('advisor.diagnose'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('auth/login.html', form=form, title='Sign In')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)
