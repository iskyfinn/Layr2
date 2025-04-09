from flask import Blueprint, render_template, redirect, url_for

# This line creates the Blueprint that's being imported
main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def index():
    return render_template('index.html')

# Add more routes as needed