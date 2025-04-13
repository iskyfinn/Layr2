from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.application import Application
from app.models.arb_review import ARBReview, ARBMeeting, ARBMeetingAgendaItem
from app.extensions import db, login_manager


arb_bp = Blueprint('arb', __name__)

@arb_bp.route('/arb/dashboard')
@login_required
def dashboard():
    """Display ARB dashboard"""
    # Check if user is an ARB member
    if not current_user.is_arb_member():
        flash('You do not have permission to access the ARB dashboard', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    # Get applications in review
    applications_in_review = Application.query.filter_by(status='In Review').all()
    
    # Get upcoming meetings
    upcoming_meetings = ARBMeeting.query.filter_by(status='Scheduled').order_by(ARBMeeting.scheduled_date).all()
    
    # Get applications that have recently been approved/rejected
    recent_decisions = Application.query.filter(Application.status.in_(['PTO', 'Rejected'])).order_by(Application.updated_at.desc()).limit(5).all()
    
    return render_template('arb/dashboard.html', 
                          applications_in_review=applications_in_review,
                          upcoming_meetings=upcoming_meetings,
                          recent_decisions=recent_decisions)

@arb_bp.route('/arb/applications')
@login_required
def applications_list():
    """Display list of applications for ARB review"""
    # Check if user is an ARB member
    if not current_user.is_arb_member():
        flash('You do not have permission to access ARB applications', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    # Get applications by status
    in_review = Application.query.filter_by(status='In Review').all()
    approved = Application.query.filter_by(status='PTO').all()
    rejected = Application.query.filter_by(status='Rejected').all()
    
    return render_template('arb/applications_list.html', 
                          in_review=in_review,
                          approved=approved,
                          rejected=rejected)

@arb_bp.route('/arb/applications/<int:app_id>/review', methods=['GET', 'POST'])
@login_required
def review_application(app_id):
    """Review an application and submit vote"""
    # Check if user is an ARB member
    if not current_user.is_arb_member():
        flash('You do not have permission to review applications', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    application = Application.query.get_or_404(app_id)
    
    # Check if application is in review status
    if not application.is_in_review_stage():
        flash('This application is not currently in review', 'warning')
        return redirect(url_for('arb.applications_list'))
    
    # Check if this ARB member has already reviewed
    existing_review = ARBReview.query.filter_by(
        application_id=app_id, reviewer_id=current_user.id
    ).first()
    
    if request.method == 'POST':
        vote = request.form.get('vote')
        comments = request.form.get('comments')
        
        if not vote or vote not in ['Approve', 'Reject', 'Abstain']:
            flash('Invalid vote option', 'danger')
            return redirect(request.url)
        
        if existing_review:
            # Update existing review
            existing_review.vote = vote
            existing_review.comments = comments
            existing_review.updated_at = datetime.utcnow()
        else:
            # Create new review
            new_review = ARBReview(
                application_id=app_id,
                reviewer_id=current_user.id,
                vote=vote,
                comments=comments
            )
            db.session.add(new_review)
        
        db.session.commit()
        
        flash('Review submitted successfully', 'success')
        return redirect(url_for('arb.applications_list'))
    
    # GET request - show review form
    return render_template('arb/review_application.html', 
                          application=application,
                          existing_review=existing_review)

@arb_bp.route('/arb/applications/<int:app_id>/decision', methods=['POST'])
@login_required
def application_decision(app_id):
    """Make final ARB decision on an application"""
    # Check if user is an ARB member
    if not current_user.is_arb_member():
        flash('You do not have permission to make ARB decisions', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    application = Application.query.get_or_404(app_id)
    
    # Check if application is in review status
    if not application.is_in_review_stage():
        flash('This application is not currently in review', 'warning')
        return redirect(url_for('arb.applications_list'))
    
    decision = request.form.get('decision')
    notes = request.form.get('decision_notes')
    
    if not decision or decision not in ['PTO', 'Rejected']:
        flash('Invalid decision', 'danger')
        return redirect(url_for('arb.review_application', app_id=app_id))
    
    # Update application status
    application.update_status(decision)
    
    # Create a final review entry to store decision notes
    final_decision = ARBReview(
        application_id=app_id,
        reviewer_id=current_user.id,
        vote='Final ' + ('Approval' if decision == 'PTO' else 'Rejection'),
        comments=notes
    )
    db.session.add(final_decision)
    db.session.commit()
    
    flash(f'Application has been {decision}', 'success')
    return redirect(url_for('arb.applications_list'))

@arb_bp.route('/arb/meetings')
@login_required
def meetings():
    """Display ARB meetings list"""
    # Check if user is an ARB member
    if not current_user.is_arb_member():
        flash('You do not have permission to access ARB meetings', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    # Get meetings by status
    scheduled_meetings = ARBMeeting.query.filter_by(status='Scheduled').order_by(ARBMeeting.scheduled_date).all()
    completed_meetings = ARBMeeting.query.filter_by(status='Completed').order_by(ARBMeeting.scheduled_date.desc()).all()
    
    return render_template('arb/meetings.html', 
                          scheduled_meetings=scheduled_meetings,
                          completed_meetings=completed_meetings)

@arb_bp.route('/arb/meetings/new', methods=['GET', 'POST'])
@login_required
def new_meeting():
    """Schedule a new ARB meeting"""
    # Check if user is an ARB member
    if not current_user.is_arb_member():
        flash('You do not have permission to schedule ARB meetings', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    if request.method == 'POST':
        scheduled_date = request.form.get('scheduled_date')
        notes = request.form.get('notes')
        
        if not scheduled_date:
            flash('Meeting date is required', 'danger')
            return redirect(request.url)
        
        # Create new meeting
        new_meeting = ARBMeeting(
            scheduled_date=datetime.strptime(scheduled_date, '%Y-%m-%dT%H:%M'),
            status='Scheduled',
            notes=notes
        )
        
        db.session.add(new_meeting)
        db.session.commit()
        
        flash('Meeting scheduled successfully', 'success')
        return redirect(url_for('arb.meetings'))
    
    # GET request - show form
    return render_template('arb/new_meeting.html')

@arb_bp.route('/arb/meetings/<int:meeting_id>')
@login_required
def meeting_detail(meeting_id):
    """Display ARB meeting details"""
    # Check if user is an ARB member
    if not current_user.is_arb_member():
        flash('You do not have permission to access ARB meeting details', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    meeting = ARBMeeting.query.get_or_404(meeting_id)
    
    # Get agenda items
    agenda_items = ARBMeetingAgendaItem.query.filter_by(meeting_id=meeting_id).order_by(ARBMeetingAgendaItem.presentation_order).all()
    
    # Get applications that could be added to the agenda
    available_applications = Application.query.filter_by(status='In Review').all()
    
    # Filter out applications already in the agenda
    agenda_app_ids = [item.application_id for item in agenda_items]
    available_applications = [app for app in available_applications if app.id not in agenda_app_ids]
    
    return render_template('arb/meeting_detail.html', 
                          meeting=meeting,
                          agenda_items=agenda_items,
                          available_applications=available_applications)

@arb_bp.route('/arb/meetings/<int:meeting_id>/add_agenda_item', methods=['POST'])
@login_required
def add_agenda_item(meeting_id):
    """Add an application to the meeting agenda"""
    # Check if user is an ARB member
    if not current_user.is_arb_member():
        flash('You do not have permission to modify ARB meeting agendas', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    meeting = ARBMeeting.query.get_or_404(meeting_id)
    
    # Check if meeting is still scheduled
    if meeting.status != 'Scheduled':
        flash('Cannot modify agenda for meetings that are not in Scheduled status', 'warning')
        return redirect(url_for('arb.meeting_detail', meeting_id=meeting_id))
    
    application_id = request.form.get('application_id')
    time_allocated = request.form.get('time_allocated')
    
    if not application_id:
        flash('Application is required', 'danger')
        return redirect(url_for('arb.meeting_detail', meeting_id=meeting_id))
    
    # Verify the application exists and is in review
    application = Application.query.get_or_404(application_id)
    if application.status != 'In Review':
        flash('Only applications in review can be added to the agenda', 'warning')
        return redirect(url_for('arb.meeting_detail', meeting_id=meeting_id))
    
    # Get the next presentation order
    next_order = 1
    max_order = db.session.query(db.func.max(ARBMeetingAgendaItem.presentation_order)).filter_by(meeting_id=meeting_id).scalar()
    if max_order:
        next_order = max_order + 1
    
    # Create new agenda item
    new_item = ARBMeetingAgendaItem(
        meeting_id=meeting_id,
        application_id=application_id,
        presentation_order=next_order,
        time_allocated=time_allocated,
        status='Pending'
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    flash('Application added to meeting agenda', 'success')
    return redirect(url_for('arb.meeting_detail', meeting_id=meeting_id))

@arb_bp.route('/arb/meetings/<int:meeting_id>/update_status', methods=['POST'])
@login_required
def update_meeting_status(meeting_id):
    """Update ARB meeting status"""
    # Check if user is an ARB member
    if not current_user.is_arb_member():
        flash('You do not have permission to update ARB meeting status', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    meeting = ARBMeeting.query.get_or_404(meeting_id)
    new_status = request.form.get('status')
    
    if not new_status or new_status not in ['Scheduled', 'Completed', 'Cancelled']:
        flash('Invalid meeting status', 'danger')
        return redirect(url_for('arb.meeting_detail', meeting_id=meeting_id))
    
    # Update meeting status
    meeting.status = new_status
    db.session.commit()
    
    flash('Meeting status updated successfully', 'success')
    return redirect(url_for('arb.meeting_detail', meeting_id=meeting_id))

@arb_bp.route('/api/arb/insights/<int:app_id>')
@login_required
def arb_insights(app_id):
    """API endpoint to provide ARB insights for an application"""
    # Check if user is an ARB member
    if not current_user.is_arb_member():
        return jsonify({
            'success': False,
            'error': 'Permission denied'
        })
    
    application = Application.query.get_or_404(app_id)
    
    # Get reviews for this application
    reviews = ARBReview.query.filter_by(application_id=app_id).all()
    
    # Calculate review stats
    approve_count = sum(1 for review in reviews if review.vote == 'Approve')
    reject_count = sum(1 for review in reviews if review.vote == 'Reject')
    abstain_count = sum(1 for review in reviews if review.vote == 'Abstain')
    total_votes = approve_count + reject_count + abstain_count
    
    # Generate insights based on application data and reviews
    insights = []
    
    # Add insight based on HLDD analysis if available
    if application.architecture_score is not None:
        if application.architecture_score < 0.5:
            insights.append({
                'type': 'warning',
                'message': 'Low architecture score in HLDD analysis. Consider requesting revisions before approval.'
            })
        elif application.architecture_score >= 0.8:
            insights.append({
                'type': 'positive',
                'message': 'High architecture score in HLDD analysis. Application shows good architectural practices.'
            })
    
    # Add insight based on review consensus
    if total_votes > 0:
        approve_percentage = (approve_count / total_votes) * 100
        if approve_percentage >= 75:
            insights.append({
                'type': 'positive',
                'message': f'Strong consensus for approval ({approve_percentage:.0f}% of votes).'
            })
        elif approve_percentage <= 25:
            insights.append({
                'type': 'warning',
                'message': f'Strong consensus against approval (only {approve_percentage:.0f}% of votes in favor).'
            })
        elif 40 <= approve_percentage <= 60:
            insights.append({
                'type': 'neutral',
                'message': f'Mixed opinions on this application ({approve_percentage:.0f}% approval rate).'
            })
    
    # Add insights based on patterns if available
    if application.pattern_analysis:
        if 'anti-pattern' in application.pattern_analysis.lower():
            insights.append({
                'type': 'warning',
                'message': 'Pattern analysis detected potential anti-patterns. Review architecture carefully.'
            })
    
    # Add insights based on modernization recommendations if available
    if application.modernization_recommendations:
        insights.append({
            'type': 'neutral',
            'message': 'Review modernization recommendations to ensure the application is future-proof.'
        })
    
    # Check if key architecture areas are addressed
    key_areas = ['security', 'scalability', 'reliability', 'compliance']
    missing_areas = []
    
    if application.description:
        for area in key_areas:
            if area not in application.description.lower():
                missing_areas.append(area)
    
    if missing_areas:
        insights.append({
            'type': 'warning',
            'message': f'Application may not adequately address: {", ".join(missing_areas)}.'
        })
    
    return jsonify({
        'success': True,
        'application': {
            'id': application.id,
            'name': application.name,
            'status': application.status,
            'architecture_score': application.architecture_score
        },
        'review_stats': {
            'approve_count': approve_count,
            'reject_count': reject_count,
            'abstain_count': abstain_count,
            'total_votes': total_votes
        },
        'insights': insights
    })