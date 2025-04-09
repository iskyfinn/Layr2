from datetime import datetime
from app import db



class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='PTI')  # PTI, In Review, PTO, Rejected
    hldd_path = db.Column(db.String(255), nullable=True)  # Path to uploaded HLDD
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Application details
    use_case = db.Column(db.Text, nullable=True)
    baseline_systems = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    
    # Analysis results
    architecture_score = db.Column(db.Float, nullable=True)  # Score from HLDD analysis
    modernization_recommendations = db.Column(db.Text, nullable=True)
    pattern_analysis = db.Column(db.Text, nullable=True)
    
    # Relationships
    reviews = db.relationship('ARBReview', backref='application', lazy='dynamic')
    
    def __repr__(self):
        return f'<Application {self.name}>'
    
    def is_in_pti_stage(self):
        return self.status == 'PTI'
    
    def is_in_review_stage(self):
        return self.status == 'In Review'
    
    def is_in_pto_stage(self):
        return self.status == 'PTO'
    
    def update_status(self, new_status):
        self.status = new_status
        self.updated_at = datetime.utcnow()
        db.session.commit()


class ApplicationTechnology(db.Model):
    __tablename__ = 'application_technologies'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    technology_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # e.g., Database, Compute, Storage, etc.
    vendor = db.Column(db.String(50))  # AWS, Azure, Google, Oracle
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Technology {self.technology_name} for App {self.application_id}>'