from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

# Import models
from app.models.user import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    # If user is already authenticated, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('applications.dashboard'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        
        # Check password
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return render_template('auth/login.html')
        
        # Log in user and update last login time
        login_user(user, remember=remember)
        user.update_last_login() if hasattr(user, 'update_last_login') else None
        
        # Redirect to the appropriate dashboard based on role
        if hasattr(user, 'role') and user.role == 'arb_member':
            return redirect(url_for('arb.dashboard'))
        else:
            return redirect(url_for('applications.dashboard'))
    
    # GET request - show login form
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'engineer')  # Default to engineer
        
        # Check if username or email already exists
        user_by_username = User.query.filter_by(username=username).first()
        user_by_email = User.query.filter_by(email=email).first()
        
        if user_by_username:
            flash('Username already exists', 'danger')
            return render_template('auth/register.html')
        
        if user_by_email:
            flash('Email already exists', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        
        # Add user to database
        db.session.add(new_user)
        db.session.commit()
        
        # Redirect to login page
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    # GET request - show registration form
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        # Check if email exists
        if email != current_user.email:
            user_by_email = User.query.filter_by(email=email).first()
            if user_by_email:
                flash('Email already exists', 'danger')
                return render_template('auth/edit_profile.html')
            
            current_user.email = email
        
        # Update password if provided
        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
                return render_template('auth/edit_profile.html')
            
            current_user.set_password(new_password)
            flash('Password updated successfully', 'success')
        
        # Commit changes
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    # GET request - show edit profile form
    return render_template('auth/edit_profile.html')