from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from .. import db
from ..models import User, Auth, UserRole
from ..forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check email uniqueness
        if Auth.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('auth.register'))

        # Create user and auth records
        default_role = UserRole.query.filter_by(name='user').first()
        user = User(name=form.name.data, role=default_role)
        db.session.add(user)
        db.session.flush()  # assign uid

        auth = Auth(uid=user.uid, email=form.email.data)
        auth.set_password(form.password.data)
        db.session.add(auth)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        auth_record = Auth.query.filter_by(email=form.email.data).first()
        if auth_record and auth_record.check_password(form.password.data):
            login_user(auth_record.user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.index'))
