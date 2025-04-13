from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.application import Application
from app.models.arb_review import ARBReview, ARBMeeting
from app.extensions import db, login_manager

from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/dashboard')
@login_required
def dashboard():
    """Display analytics dashboard"""
    # Only ARB members and architects can view analytics
    if not (current_user.is_arb_member() or current_user.is_architect()):
        flash('You do not have permission to access analytics', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    return render_template('analytics/dashboard.html')

@analytics_bp.route('/api/analytics/application_status')
@login_required
def api_application_status():
    """API endpoint for application status analytics"""
    # Only ARB members and architects can view analytics
    if not (current_user.is_arb_member() or current_user.is_architect()):
        return jsonify({
            'success': False,
            'error': 'Permission denied'
        })
    
    # Count applications by status
    status_counts = db.session.query(
        Application.status, func.count(Application.id)
    ).group_by(Application.status).all()
    
    # Format for chart
    labels = [status for status, _ in status_counts]
    counts = [count for _, count in status_counts]
    
    return jsonify({
        'success': True,
        'labels': labels,
        'counts': counts
    })

@analytics_bp.route('/api/analytics/architecture_scores')
@login_required
def api_architecture_scores():
    """API endpoint for architecture score analytics"""
    # Only ARB members and architects can view analytics
    if not (current_user.is_arb_member() or current_user.is_architect()):
        return jsonify({
            'success': False,
            'error': 'Permission denied'
        })
    
    # Get applications with architecture scores
    applications = db.session.query(
        Application.name, Application.architecture_score
    ).filter(Application.architecture_score != None).all()
    
    # Format for chart
    app_names = [app[0] for app in applications]
    scores = [app[1] for app in applications]
    
    # Calculate score distributions
    score_ranges = {
        'Low (0-0.4)': 0,
        'Medium (0.4-0.7)': 0,
        'High (0.7-1.0)': 0
    }
    
    for score in scores:
        if score < 0.4:
            score_ranges['Low (0-0.4)'] += 1
        elif score < 0.7:
            score_ranges['Medium (0.4-0.7)'] += 1
        else:
            score_ranges['High (0.7-1.0)'] += 1
    
    return jsonify({
        'success': True,
        'app_names': app_names,
        'scores': scores,
        'score_ranges': {
            'labels': list(score_ranges.keys()),
            'counts': list(score_ranges.values())
        }
    })

@analytics_bp.route('/api/analytics/review_trends')
@login_required
def api_review_trends():
    """API endpoint for ARB review trend analytics"""
    # Only ARB members and architects can view analytics
    if not (current_user.is_arb_member() or current_user.is_architect()):
        return jsonify({
            'success': False,
            'error': 'Permission denied'
        })
    
    # Calculate the date 6 months ago
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    # Get monthly counts of applications moving to different statuses
    monthly_data = []
    
    for month_offset in range(6):
        month_start = six_months_ago + timedelta(days=30 * month_offset)
        month_end = month_start + timedelta(days=30)
        month_label = month_start.strftime('%b %Y')
        
        # Count applications submitted for review in this month
        submitted_count = db.session.query(func.count(Application.id)).filter(
            Application.status != 'PTI',
            Application.updated_at >= month_start,
            Application.updated_at < month_end
        ).scalar()
        
        # Count applications approved in this month
        approved_count = db.session.query(func.count(Application.id)).filter(
            Application.status == 'PTO',
            Application.updated_at >= month_start,
            Application.updated_at < month_end
        ).scalar()
        
        # Count applications rejected in this month
        rejected_count = db.session.query(func.count(Application.id)).filter(
            Application.status == 'Rejected',
            Application.updated_at >= month_start,
            Application.updated_at < month_end
        ).scalar()
        
        monthly_data.append({
            'month': month_label,
            'submitted': submitted_count or 0,
            'approved': approved_count or 0,
            'rejected': rejected_count or 0
        })
    
    return jsonify({
        'success': True,
        'monthly_data': monthly_data
    })

@analytics_bp.route('/api/analytics/common_issues')
@login_required
def api_common_issues():
    """API endpoint for common issues identified in ARB reviews"""
    # Only ARB members and architects can view analytics
    if not (current_user.is_arb_member() or current_user.is_architect()):
        return jsonify({
            'success': False,
            'error': 'Permission denied'
        })
    
    # Get rejection comments from ARB reviews
    rejection_reviews = ARBReview.query.filter(
        or_(
            ARBReview.vote == 'Reject',
            ARBReview.vote == 'Final Rejection'
        )
    ).all()
    
    # Extract and analyze comments
    # In a real system, this would use NLP to identify common issues
    # For this prototype, we'll simulate with keyword counting
    
    issue_keywords = {
        'security': ['security', 'vulnerability', 'authentication', 'authorization'],
        'scalability': ['scalability', 'performance', 'throughput', 'capacity'],
        'reliability': ['reliability', 'availability', 'fault tolerance', 'resilience'],
        'documentation': ['documentation', 'unclear', 'missing details', 'incomplete'],
        'compliance': ['compliance', 'regulation', 'standard', 'policy'],
        'architecture': ['architecture', 'design', 'pattern', 'anti-pattern']
    }
    
    issue_counts = {category: 0 for category in issue_keywords}
    
    for review in rejection_reviews:
        if review.comments:
            comments_lower = review.comments.lower()
            for category, keywords in issue_keywords.items():
                for keyword in keywords:
                    if keyword in comments_lower:
                        issue_counts[category] += 1
                        break  # Count each category only once per review
    
    # Format for chart
    categories = list(issue_counts.keys())
    counts = list(issue_counts.values())
    
    return jsonify({
        'success': True,
        'categories': categories,
        'counts': counts
    })

@analytics_bp.route('/api/analytics/meeting_stats')
@login_required
def api_meeting_stats():
    """API endpoint for ARB meeting statistics"""
    # Only ARB members and architects can view analytics
    if not (current_user.is_arb_member() or current_user.is_architect()):
        return jsonify({
            'success': False,
            'error': 'Permission denied'
        })
    
    # Get completed meetings
    completed_meetings = ARBMeeting.query.filter_by(status='Completed').all()
    
    # Count meetings by month
    meeting_counts = {}
    
    for meeting in completed_meetings:
        month_key = meeting.scheduled_date.strftime('%b %Y')
        if month_key not in meeting_counts:
            meeting_counts[month_key] = 0
        meeting_counts[month_key] += 1
    
    # Get average applications per meeting
    avg_apps_per_meeting = 0
    if completed_meetings:
        total_agenda_items = 0
        for meeting in completed_meetings:
            total_agenda_items += meeting.applications.count()
        avg_apps_per_meeting = total_agenda_items / len(completed_meetings)
    
    # Format for charts
    months = list(meeting_counts.keys())
    counts = list(meeting_counts.values())
    
    return jsonify({
        'success': True,
        'meeting_counts': {
            'months': months,
            'counts': counts
        },
        'avg_apps_per_meeting': round(avg_apps_per_meeting, 1)
    })