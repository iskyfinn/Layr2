from datetime import datetime
from app import db

class ARBReview(db.Model):
    __tablename__ = 'arb_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vote = db.Column(db.String(20), nullable=True)  # Approve, Reject, Abstain
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ARBReview {self.id} for App {self.application_id}>'


class ARBMeeting(db.Model):
    __tablename__ = 'arb_meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, Completed, Cancelled
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('ARBMeetingAgendaItem', backref='meeting', lazy='dynamic')
    
    def __repr__(self):
        return f'<ARBMeeting {self.scheduled_date}>'


class ARBMeetingAgendaItem(db.Model):
    __tablename__ = 'arb_meeting_agenda_items'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('arb_meetings.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    presentation_order = db.Column(db.Integer, nullable=True)
    time_allocated = db.Column(db.Integer, nullable=True)  # Time in minutes
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected, Deferred
    
    # Make the relationship
    application = db.relationship('Application')
    
    def __repr__(self):
        return f'<AgendaItem for App {self.application_id} in Meeting {self.meeting_id}>'