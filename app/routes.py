from flask import Blueprint, render_template

# Authentication Blueprint
auth_bp = Blueprint('auth', __name__)

# Applications Blueprint
applications_bp = Blueprint('applications', __name__)

# ARB (Architecture Review Board) Blueprint
arb_bp = Blueprint('arb', __name__)

# Analytics Blueprint
analytics_bp = Blueprint('analytics', __name__)

# Main/Home Blueprint
main_bp = Blueprint('main', __name__)

# Routes for each blueprint
@main_bp.route('/')
def index():
    return render_template('base.html')

@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')

@applications_bp.route('/dashboard')
def applications_dashboard():
    return render_template('applications/dashboard.html')

@arb_bp.route('/dashboard')
def arb_dashboard():
    return render_template('arb/dashboard.html')

@analytics_bp.route('/dashboard')
def analytics_dashboard():
    return render_template('analytics/dashboard.html')