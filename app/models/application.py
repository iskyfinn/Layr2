from app.extensions import db, login_manager

from datetime import datetime
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy  # For type hinting
import traceback

class Diagram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    # Add other diagram-related fields here

class ApplicationTechnology(db.Model):
    """
    Association table for Application and Technology
    Allows tracking which technologies are used in each application
    """
    __tablename__ = 'application_technologies'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    technology_id = db.Column(db.Integer, db.ForeignKey('technologies.id'), nullable=False)
    usage_type = db.Column(db.String(50))  # e.g., Frontend, Backend, Database, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    technology = db.relationship('Technology', backref='application_technologies')
    
    def __repr__(self):
        return f'<ApplicationTechnology {self.application_id}:{self.technology_id}>'

class Application(db.Model):
    """Application model for architecture review"""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='PTI')  # PTI, In Review, PTO, Rejected
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    technologies = db.relationship('ApplicationTechnology', backref='application', lazy='dynamic')

    # Additional fields
    use_case = db.Column(db.Text)
    requirements = db.Column(db.Text)
    baseline_systems = db.Column(db.Text)
    business_unit = db.Column(db.String(100))
    technology_stack = db.Column(db.String(255))
    criticality = db.Column(db.String(20))
    security_classification = db.Column(db.String(20))
    deployment_model = db.Column(db.String(20))
    user_base = db.Column(db.String(100))
    additional_context = db.Column(db.Text)
    
    # HLDD path
    hldd_path = db.Column(db.String(255))
    
    # Architecture score (0-1)
    architecture_score = db.Column(db.Float)
    
    # Relationships
    owner = db.relationship('User', backref='applications')
    diagrams = db.relationship('Diagram', backref='application', lazy='dynamic')
    reviews = db.relationship('ARBReview', backref='application', lazy='dynamic')
    
    def is_in_pti_stage(self):
        """Check if application is in PTI stage"""
        return self.status == 'PTI'
    
    def is_in_review_stage(self):
        """Check if application is in review stage"""
        return self.status == 'In Review'
    
    def is_in_pto_stage(self):
        """Check if application is in PTO stage"""
        return self.status == 'PTO'
    
    def is_rejected(self):
        """Check if application is rejected"""
        return self.status == 'Rejected'
    
    def submit_for_review(self):
        """
        Submit application for review
        Performs validation checks before changing status
        """
        # Check if application is in PTI stage
        if not self.is_in_pti_stage():
            return False, "Application is not in PTI stage"
        
        # Validate required fields
        required_fields = ['name', 'description', 'use_case', 'requirements']
        for field in required_fields:
            if not getattr(self, field):
                return False, f"Missing required field: {field}"
        
        # Check if HLDD is uploaded (not strictly required but recommended)
        if not self.hldd_path:
            # Allow submission without HLDD, but return warning
            self.status = 'In Review'
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True, "Application submitted for review, but HLDD is missing"
        
        # Everything looks good
        self.status = 'In Review'
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return True, "Application successfully submitted for review"
    
    def make_final_decision(self, decision, notes=None):
        """
        Make final decision on application (PTO or Rejected)
        
        Args:
            decision: 'PTO' or 'Rejected'
            notes: Optional notes about the decision
        
        Returns:
            tuple: (success, message)
        """
        # Check if application is in review stage
        if not self.is_in_review_stage():
            return False, "Application is not in review stage"
        
        # Check if decision is valid
        if decision not in ['PTO', 'Rejected']:
            return False, "Invalid decision"
        
        # Check if user is ARB member
        if not current_user.is_arb_member():
            return False, "Only ARB members can make final decisions"
        
        # Make decision
        self.status = decision
        self.updated_at = datetime.utcnow()
        
        # Create decision record (assuming there's a Decision model)
        from .arb_review import ARBDecision  # Local import to avoid circular dependency
        decision_record = ARBDecision(
            application_id=self.id,
            decision=decision,
            notes=notes,
            reviewer_id=current_user.id
        )
        db.session.add(decision_record)
        
        # Commit changes
        db.session.commit()
        
        return True, f"Application marked as {decision}"
    
    def get_review_status(self):
        """
        Get review status statistics
        
        Returns:
            dict: Review statistics
        """
        # Get all reviews
        all_reviews = self.reviews.all()
        
        # Count votes
        approve_count = sum(1 for review in all_reviews if review.vote == 'Approve')
        reject_count = sum(1 for review in all_reviews if review.vote == 'Reject')
        abstain_count = sum(1 for review in all_reviews if review.vote == 'Abstain')
        
        # Calculate percentages
        total_count = len(all_reviews)
        approve_percentage = (approve_count / total_count * 100) if total_count > 0 else 0
        reject_percentage = (reject_count / total_count * 100) if total_count > 0 else 0
        abstain_percentage = (abstain_count / total_count * 100) if total_count > 0 else 0
        
        return {
            'total_count': total_count,
            'approve_count': approve_count,
            'reject_count': reject_count,
            'abstain_count': abstain_count,
            'approve_percentage': approve_percentage,
            'reject_percentage': reject_percentage,
            'abstain_percentage': abstain_percentage
        }
    
    def __repr__(self):
        return f'<Application {self.name}>'

class ARBDecision(db.Model):
    """ARB Decision model"""
    __tablename__ = 'arb_decisions'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    decision = db.Column(db.String(20), nullable=False)  # PTO, Rejected
    notes = db.Column(db.Text)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    application = db.relationship('Application', backref='decisions')
    reviewer = db.relationship('User', backref='decisions')
    
    def __repr__(self):
        return f'<ARBDecision {self.decision} for Application {self.application_id}>'