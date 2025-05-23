# run.py

import os
import sys
print(f"Python path: {sys.path}")
from app import create_app, db



# Add the project root directory to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from app import create_app, db

# Create the Flask application
app = create_app()

print("Registered endpoints:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create database tables
    app.run(debug=True)