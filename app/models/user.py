from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


from datetime import datetime

# Import db dynamically when needed
def get_db():


    return db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    def __init__(self, username, email, role='engineer'):  # Added 'role' argument with a default
        self.username = username
        self.email = email
        self.password_hash = None
        self.role = role  # Initialize the role a

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='engineer')
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Set password with hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def is_arb_member(self):
        """Check if user is an ARB member"""
        return self.role == 'arb_member'

    def is_architect(self):
        """Check if user is an architect"""
        return self.role == 'architect'

    @classmethod
    def create(cls, username, email, password, role='engineer'): # Added 'role' argument here as well
        db = get_db()
        user = cls(username, email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))