# Standard library imports
import os
import re
import json
import logging
import traceback
from datetime import datetime
from collections import Counter

# Third-party imports
import docx
import fitz  # PyMuPDF
import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from werkzeug.utils import secure_filename
from app.services.hldd_generator import get_document_generator
from app.services.enhanced_document_generator import get_enhanced_document_generator

# Flask-related imports
from flask import (
    Blueprint, request, flash, redirect, url_for, 
    render_template, jsonify, current_app
)
from flask_login import login_required, current_user

# App-specific imports
from app.config import Config
from app.extensions import db, login_manager
from app.models.application import Application
from app.models.arb_review import ARBReview
from app.services.hldd_analyzer import HLDDAnalyzer
from app.services.pattern_analyzer import get_pattern_analyzer
from app.services.architecture_recommender import get_recommender
from app.services.modernization_strategy import ModernizationStrategy, get_modernization_strategy

# Blueprint
applications_bp = Blueprint('applications', __name__, template_folder='../templates/applications')


# Allowed file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'pptx', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route registration is handled directly on the blueprint now
# This function is retained only if future dynamic registration is needed
def register_hldd_routes(applications_bp):
    pass  # No action needed unless dynamically registering new routes

# -----------------------------
# Modernization Strategy Helper
# -----------------------------
@applications_bp.route('/applications/<int:app_id>/modernization')
@login_required
def modernization_strategy(app_id):
    application = Application.query.get_or_404(app_id)

    # Permissions check
    if application.user_id != current_user.id and not (
        current_user.is_arb_member() or current_user.is_architect()
    ):
        flash('You do not have permission to view modernization strategies', 'danger')
        return redirect(url_for('applications.dashboard'))

    app_info = {
        'description': application.description or '',
        'tech_stack': application.technology_stack or '',
        'age': getattr(application, 'age', 'new'),
        'business_value': getattr(application, 'business_value', '')
    }

    try:
        # Get HLDD analysis if available
        hldd_analysis = {'overall_score': 0.0}
        if application.hldd_path:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            hldd_path = os.path.join(upload_folder, application.hldd_path)
            analyzer = HLDDAnalyzer(hldd_path)
            hldd_analysis = analyzer.analyze_document(hldd_path)
    except Exception as e:
        current_app.logger.error(f"Error analyzing HLDD: {str(e)}")
        flash(f"Error analyzing HLDD: {str(e)}", 'warning')
        hldd_analysis = {'overall_score': 0.0}

    # Get modernization strategy
    strategy_service = ModernizationStrategy()
    strategies = strategy_service.recommend_strategy(app_info, hldd_analysis)

    # Render template with data
    return render_template('modernization_strategies.html', 
                          application=application, 
                          strategies=strategies)


# -----------------------------
# HLDD Upload Route
# -----------------------------
@applications_bp.route('/applications/<int:app_id>/upload_hldd', methods=['GET', 'POST'])
@login_required
def upload_hldd(app_id):
    application = Application.query.get_or_404(app_id)

    if application.user_id != current_user.id:
        flash('You do not have permission to upload an HLDD for this application', 'danger')
        return redirect(url_for('applications.dashboard'))

    if request.method == 'POST':
        if 'hldd_file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['hldd_file']

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        allowed_extensions = {'pdf', 'doc', 'docx', 'txt', 'md'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            flash('Invalid file type. Please upload a PDF, Word document, or text file.', 'danger')
            return redirect(request.url)

        try:
            filename = secure_filename(file.filename)
            unique_filename = f"{app_id}_{filename}"
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)

            application.hldd_path = unique_filename
            db.session.commit()

            flash('HLDD uploaded successfully!', 'success')
            return redirect(url_for('applications.analyze_hldd', app_id=app_id))

        except Exception as e:
            logging.error(f"Error uploading HLDD: {str(e)}")
            flash(f'Error uploading HLDD: {str(e)}', 'danger')
            return redirect(request.url)

    return render_template('applications/upload_hldd.html', application=application)



# -----------------------------
# HLDD Analyze Route
# -----------------------------
@applications_bp.route('/applications/<int:app_id>/analyze_hldd', methods=['GET'])
@login_required
def analyze_hldd(app_id):
    """
    Analyze the uploaded HLDD and return architecture insights.
    """
    application = Application.query.get_or_404(app_id)

    # Permissions check
    if application.user_id != current_user.id and not current_user.is_arb_member():
        flash('You do not have permission to analyze this HLDD', 'danger')
        return redirect(url_for('applications.dashboard'))

    # Check HLDD existence
    if not application.hldd_path:
        flash('No HLDD found for this application', 'warning')
        return redirect(url_for('applications.application_detail', app_id=app_id))

    try:
        # Construct HLDD path
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        hldd_full_path = os.path.join(upload_folder, application.hldd_path)

        # Analyze document
        analyzer = HLDDAnalyzer(hldd_full_path)
        results = analyzer.analyze_document(hldd_full_path)

        if results.get('error'):
            flash(f"HLDD analysis failed: {results['error']}", 'danger')
            return redirect(url_for('applications.application_detail', app_id=app_id))

        # Save architecture score if needed
        application.architecture_score = results.get('overall_score')
        db.session.commit()

        # Format results for rendering
        formatted_results = {
            'success': True,
            'overall_score': int(results.get('overall_score', 0) * 100),
            'message': "This HLDD has been analyzed successfully." if results.get('acceptable') else
                       "This HLDD needs improvement in several areas.",
            'insights': []
        }

        for criterion, data in results.get('scores', {}).items():
            insight_type = "positive" if data['score'] >= 0.7 else "warning"
            formatted_results['insights'].append({
                'type': insight_type,
                'message': f"{criterion.replace('_', ' ').title()} score: {int(data['score'] * 100)}%"
            })

        if results.get('missing_components'):
            components_str = ", ".join(results['missing_components'])
            formatted_results['insights'].append({
                'type': 'warning',
                'message': f"Missing components: {components_str}"
            })

        for recommendation in results.get('recommendations', []):
            formatted_results['insights'].append({
                'type': 'info',
                'message': recommendation
            })

        return render_template('applications/hldd_analysis.html',
                               application=application,
                               results=formatted_results)

    except Exception as e:
        logging.error(f"Error analyzing HLDD: {str(e)}")
        flash(f'Error analyzing HLDD: {str(e)}', 'danger')
        return redirect(url_for('applications.application_detail', app_id=app_id))


@applications_bp.route('/arb/api/insights/<int:app_id>', methods=['GET'])
@login_required
def arb_insights(app_id):
    """
    Get architecture insights for ARB review
    """
    # Security check - only ARB members can access insights
    if not current_user.is_arb_member():
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    # Get the application
    application = Application.query.get_or_404(app_id)

    # Check if HLDD exists
    if not application.hldd_path:
        return jsonify({
            'success': True,
            'insights': [{
                'type': 'warning',
                'message': 'No HLDD uploaded for this application. Recommend applicant to upload HLDD.'
            }]
        })

    try:
        # Build full path to HLDD
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        full_path = os.path.join(upload_folder, application.hldd_path)

        # Create analyzer and analyze document
        analyzer = HLDDAnalyzer(full_path)  # ✅ FIXED: previously was hldd_full_path
        results = analyzer.analyze_document(full_path)

        # If error occurred during analysis
        if results.get('error'):
            return jsonify({
                'success': True,
                'insights': [{
                    'type': 'warning',
                    'message': f"HLDD analysis failed: {results['error']}"
                }]
            })

        # Format insights
        insights = []

        # Add insight for overall score
        overall_score = results.get('overall_score', 0)
        score_type = "positive" if overall_score >= 0.7 else "warning"
        insights.append({
            'type': score_type,
            'message': f"Overall architecture score: {int(overall_score * 100)}%"
        })

        # Add insights for key criteria
        for criterion in ['security', 'scalability', 'reliability']:
            data = results.get('scores', {}).get(criterion)
            if data:
                insight_type = "positive" if data['score'] >= 0.7 else "warning"
                insights.append({
                    'type': insight_type,
                    'message': f"{criterion.title()} score: {int(data['score'] * 100)}%"
                })

        # Add insights for missing components
        missing = results.get('missing_components', [])
        if missing:
            insights.append({
                'type': 'warning',
                'message': f"Architecture is missing these components: {', '.join(missing)}"
            })

        # Add top recommendation if available
        recommendations = results.get('recommendations', [])
        if recommendations:
            insights.append({
                'type': 'info',
                'message': f"Recommendation: {recommendations[0]}"
            })

        return jsonify({
            'success': True,
            'insights': insights
        })

    except Exception as e:
        logging.exception("Unhandled exception in arb_insights")
        return jsonify({
            'success': False,
            'error': f"Error getting insights: {str(e)}"
        }), 500


@applications_bp.route('/api/documents/generate', methods=['POST'])
@login_required
def generate_document_api():
    """Generate an enhanced HLDD document via API"""
    try:
        data = request.json
        application_id = data.get('application_id')
        
        if not application_id:
            return jsonify({
                'success': False,
                'error': 'Missing application_id'
            }), 400
            
        # Get application data from database
        application = Application.query.get_or_404(application_id)
        
        # Check permissions
        if application.user_id != current_user.id and not (current_user.is_arb_member() or current_user.is_architect()):
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        # Check if enhanced document generator is available
        if not hasattr(current_app, 'enhanced_document_generator'):
            # Fallback to regular document generator
            doc_generator = get_document_generator(current_app.config.get('UPLOAD_FOLDER', 'uploads'))
            result = doc_generator.generate_hldd(
                application=application,
                user_inputs=data
            )
            current_app.logger.info(f"[HLDD] Generation result: {json.dumps(result, indent=2)}")

        else:
            # Use enhanced document generator
            result = current_app.enhanced_document_generator.generate_hldd(
                application=application,
                user_inputs=data,
                auto_enhance=True
            )
        
        if result.get('success', False):
            # Update application with generated HLDD path
            application.hldd_path = result.get('file_path', '')
            application.updated_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error generating document via API: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@applications_bp.route('/applications/<int:app_id>/generate_hldd', methods=['GET', 'POST'])
@login_required
def generate_hldd(app_id):
    """Generate HLDD document via web interface (supports form & JSON POST)"""
    try:
        application = Application.query.get_or_404(app_id)

        # Permissions check
        if application.user_id != current_user.id and not (
            current_user.is_arb_member() or current_user.is_architect()
        ):
            flash('You do not have permission to generate HLDD', 'danger')
            return redirect(url_for('applications.dashboard'))

        if request.method == 'POST':
            try:
                # Extract user input
                user_inputs = request.get_json() if request.is_json else request.form.to_dict()

                current_app.logger.info(f"[HLDD] Starting generation for app_id={app_id}")
                current_app.logger.debug(f"[HLDD] User inputs: {user_inputs}")

                # Get document generator service
                doc_generator = get_enhanced_document_generator(
                    current_app.config.get('UPLOAD_FOLDER', 'uploads')
                )

                # Generate HLDD
                result = doc_generator.generate_hldd(
                    application=application,
                    user_inputs=user_inputs,
                    auto_enhance=True
                )

                current_app.logger.info(f"[HLDD] Generation result: {json.dumps(result, indent=2)}")

                if result.get('success'):
                    # Store the HLDD path
                    application.hldd_path = result.get('file_path', '')
                    application.updated_at = datetime.utcnow()
                    db.session.commit()

                    if request.is_json:
                        return jsonify({
                            'success': True,
                            'message': 'HLDD generated successfully',
                            'file_path': result.get('file_path'),
                            'file_name': result.get('file_name'),
                            'hldd_data': result.get('hldd_data', {})
                        }), 200
                    else:
                        flash('HLDD generated successfully!', 'success')
                        return redirect(url_for('applications.application_detail', app_id=app_id))

                # If generation failed
                error_msg = result.get('error', 'HLDD generation failed for unknown reason.')
                tb = result.get('traceback', '')

                current_app.logger.warning(f"[HLDD] Failed: {error_msg}")
                if tb:
                    current_app.logger.debug(tb)

                if request.is_json:
                    return jsonify({'success': False, 'error': error_msg, 'traceback': tb}), 500
                else:
                    flash(f'HLDD generation failed: {error_msg}', 'danger')
                    return redirect(url_for('applications.generate_hldd', app_id=app_id))

            except Exception as e:
                current_app.logger.error(f"[HLDD] Exception: {str(e)}")
                current_app.logger.debug(traceback.format_exc())
                if request.is_json:
                    return jsonify({'success': False, 'error': f'Exception: {str(e)}'}), 500
                else:
                    flash(f'Error generating HLDD: {str(e)}', 'danger')
                    return redirect(url_for('applications.generate_hldd', app_id=app_id))

        # GET: Show generation form
        return render_template('applications/generate_hldd.html', application=application)

    except Exception as e:
        current_app.logger.critical(f"[HLDD] Unexpected error: {str(e)}")
        current_app.logger.debug(traceback.format_exc())
        flash('An unexpected error occurred while generating HLDD.', 'danger')
        return redirect(url_for('applications.dashboard'))


    # Document generator factory
    def get_document_generator(upload_folder):
        """
        Factory function to get a document generator instance

        :param upload_folder: Folder to store generated documents
        :return: DocumentGenerator instance
        """
        # Import here to avoid circular imports
        from app.services.hldd_generator import get_document_generator as get_hldd_generator
        return get_hldd_generator(upload_folder)


    # Simple HLDD analyzer wrapper
    def analyze_document(document_path):
        """Run HLDD analysis from file path"""
        try:
            analyzer = HLDDAnalyzer(document_path)
            return analyzer.analyze_document(document_path)
        except Exception as e:
            logging.error(f"Error analyzing document: {str(e)}")
            return {
                'error': str(e),
                'scores': {},
                'missing_components': [],
                'overall_score': 0,
                'acceptable': False,
                'recommendations': ["Error analyzing document. Please check file format and try again."]
            }



         
@applications_bp.route('/applications/<int:app_id>')
@login_required
def application_detail(app_id):
    """Display application details"""
    application = Application.query.get_or_404(app_id)
    
    # Check if user owns this application or is an ARB member
    if application.user_id != current_user.id and not current_user.is_arb_member():
        flash('You do not have permission to view this application', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    return render_template('applications/application_detail.html', 
                          application=application)

# Dashboard view
@applications_bp.route('/dashboard')
@login_required
def dashboard():
    user_applications = Application.query.filter_by(user_id=current_user.id).all()
    return render_template('applications/dashboard.html', 
                           applications=user_applications, 
                           user=current_user)
    def _recommend_architecture_style(self, application):
        """
        Recommend architecture style based on application details
        
        :param application: Application model instance
        :return: Recommended architecture style
        """
        try:
            # Use the existing architecture recommender
            recommender = get_recommender()
            recommendations = recommender.recommend_architecture(
                application.use_case or '',
                application.requirements or ''
            )
            
            # Return the top recommended pattern
            return recommendations.get('recommended_patterns', [{}])[0].get('pattern', 'Microservices')
        except Exception as e:
            # Log the error and return a default architecture
            current_app.logger.error(f"Architecture recommendation error: {str(e)}")
            return 'Microservices'
    
def _extract_technology_stack(self, application):
    """
    Extract technology stack from ApplicationTechnology model
    
    :param application: Application model instance
    :return: List of technology stack details
    """
    technologies = ApplicationTechnology.query.filter_by(application_id=application.id).all()
    return [
        {
            'area': tech.category,
            'technology': tech.technology_name,
            'vendor': tech.vendor,
            'rationale': tech.notes
        } for tech in technologies
    ]

@applications_bp.route('/api/architecture/analyze', methods=['POST'])
@login_required
def analyze_architecture():
    """Queue an application for architecture analysis"""
    try:
        data = request.get_json()
        application_id = data.get('application_id')
        use_case = data.get('use_case')
        requirements = data.get('requirements')
        baseline = data.get('baseline_systems')

        if not application_id:
            return jsonify({'error': 'application_id is required'}), 400

        # Fetch the application record
        application = Application.query.get_or_404(application_id)

        # Merge use_case, requirements, baseline (override DB if provided)
        application_data = {
            'name': application.name,
            'description': application.description,
            'technology_stack': application.technology_stack,
            'use_case': use_case or application.use_case,
            'requirements': requirements or application.requirements,
            'baseline_systems': baseline or ""
        }

        # Submit for analysis using architecture agent
        task_id = current_app.architecture_agent.analyze_application(
            application_id=application_id,
            application_data=application_data,
            priority=3  # Medium priority
        )

        return jsonify({'task_id': task_id, 'status': 'queued'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@applications_bp.route('/api/architecture/status/<task_id>', methods=['GET'])
@login_required
def get_analysis_status(task_id):
    """Get status of an architecture analysis task"""
    status = current_app.architecture_agent.get_analysis_status(task_id)
    return jsonify(status)

@applications_bp.route('/api/architecture/insights/<application_id>', methods=['GET'])
@login_required
def get_application_insights(application_id):
    """Get comprehensive architecture insights for an application"""
    insights = current_app.architecture_agent.get_application_insights(application_id)
    return jsonify(insights)

@applications_bp.route('/applications/<int:app_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_application(app_id):
    """Edit application details"""
    application = Application.query.get_or_404(app_id)
    
    # Check if user owns this application
    if application.user_id != current_user.id:
        flash('You do not have permission to edit this application', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    if request.method == 'POST':
        # Get form data
        application.name = request.form.get('name')
        application.description = request.form.get('description')
        application.use_case = request.form.get('use_case')
        application.baseline_systems = request.form.get('baseline_systems')
        application.requirements = request.form.get('requirements')
        
        # Update application
        application.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Application updated successfully', 'success')
        return redirect(url_for('applications.application_detail', app_id=application.id))
    
    # GET request - show form
    return render_template('applications/edit_application.html', 
                          application=application)

# New application view and submission
@applications_bp.route('/applications/new', methods=['GET', 'POST'])
@login_required
def new_application():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        use_case = request.form.get('use_case')
        baseline_systems = request.form.get('baseline_systems')
        requirements = request.json.get("requirements")

        
        if not all([name, description, use_case, baseline_systems, requirements]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('applications/new_application.html')  # Re-render form

        new_app = Application(
            name=name,
            description=description,
            user_id=current_user.id,
            status='PTI',
            use_case=use_case,
            baseline_systems=baseline_systems,
            requirements=requirements
        )

        db.session.add(new_app)
        db.session.commit()

        flash('Application created successfully', 'success')
        return redirect(url_for('applications.application_detail', app_id=new_app.id))

    # GET request: render form
    return render_template('applications/new_application.html')

def schedule_periodic_analysis():
    """Schedule periodic analysis of all applications"""
    applications = Application.query.all()
    
    for application in applications:
        # Skip applications analyzed in the last week
        last_analysis = ARBReview.query.filter_by(
            application_id=application.id
        ).order_by(ARBReview.created_at.desc()).first()
        
        if last_analysis and (datetime.utcnow() - last_analysis.created_at).days < 7:
            continue
        
        # Convert to dictionary for the agent
        application_data = {
            'name': application.name,
            'description': application.description,
            'technology_stack': application.technology_stack,
            'use_case': application.use_case,
            'requirements': application.requirements
        }
        
        # Submit for analysis with low priority
        current_app.architecture_agent.analyze_application(
            str(application.id), 
            application_data,
            priority=1  # Low priority for background tasks
        )


import traceback
import logging
from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.application import Application

@applications_bp.route('/applications/<int:app_id>/recommend_architecture')
@login_required
def recommend_architecture(app_id):
    """Recommend architecture based on application details"""
    application = Application.query.get_or_404(app_id)
    
    # Check if user owns this application or is an ARB member or architect
    if application.user_id != current_user.id and not (current_user.is_arb_member() or current_user.is_architect()):
        flash('You do not have permission to view architecture recommendations', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    # Check if application has required details
    if not application.use_case or not application.requirements:
        flash('Application is missing use case or requirements details', 'warning')
        return redirect(url_for('applications.application_detail', app_id=application.id))
    
    try:
        # Get architecture recommendations
        recommender = get_recommender()
        recommendations = recommender.recommend_architecture(
            application.use_case,
            application.requirements,
            application.baseline_systems
        )
        
        # Ensure the cloud_recommendations structure matches what the template expects
        if 'cloud_recommendations' in recommendations:
            cloud_recs = recommendations['cloud_recommendations']
            
            # Ensure we have scores
            if 'scores' not in cloud_recs:
                cloud_recs['scores'] = {
                    'aws': 0.85,
                    'azure': 0.75,
                    'google': 0.65,
                    'oracle': 0.55
                }
            
            # Ensure we have primary and secondary providers
            if 'primary' not in cloud_recs:
                cloud_recs['primary'] = 'aws'
            
            if 'secondary' not in cloud_recs:
                cloud_recs['secondary'] = 'azure'
            
            # Create overall_ranking if missing
            if 'overall_ranking' not in cloud_recs:
                # Create strength maps for each provider
                strength_maps = {
                    'aws': ['Breadth of services', 'Global reach', 'Mature ecosystem'],
                    'azure': ['Enterprise integration', 'Hybrid cloud', 'Windows ecosystem'],
                    'google': ['Data analytics', 'Kubernetes', 'Machine learning'],
                    'oracle': ['Database performance', 'Integrated stack', 'Enterprise workloads']
                }
                
                # Sort providers by score
                scores = cloud_recs['scores']
                sorted_providers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                
                # Create overall_ranking structure
                cloud_recs['overall_ranking'] = [
                    {
                        'provider': provider,
                        'score': score,
                        'key_strengths': strength_maps.get(provider, ['Versatile services'])
                    } for provider, score in sorted_providers
                ]
            
            # Ensure focus_areas exists
            if 'focus_areas' not in cloud_recs:
                cloud_recs['focus_areas'] = ['compute', 'storage', 'database', 'networking']
        else:
            # If no cloud recommendations at all, create a default structure
            recommendations['cloud_recommendations'] = {
                'primary': 'aws',
                'secondary': 'azure',
                'scores': {
                    'aws': 0.85,
                    'azure': 0.75,
                    'google': 0.65,
                    'oracle': 0.55
                },
                'overall_ranking': [
                    {
                        'provider': 'aws',
                        'score': 0.85,
                        'key_strengths': ['Breadth of services', 'Global reach', 'Mature ecosystem']
                    },
                    {
                        'provider': 'azure',
                        'score': 0.75,
                        'key_strengths': ['Enterprise integration', 'Hybrid cloud', 'Windows ecosystem']
                    },
                    {
                        'provider': 'google',
                        'score': 0.65,
                        'key_strengths': ['Data analytics', 'Kubernetes', 'Machine learning']
                    },
                    {
                        'provider': 'oracle',
                        'score': 0.55,
                        'key_strengths': ['Database performance', 'Integrated stack', 'Enterprise workloads']
                    }
                ],
                'focus_areas': ['compute', 'storage', 'database', 'networking']
            }
        
        # Ensure identified_use_case exists and is formatted
        if 'identified_use_case' not in recommendations or not recommendations['identified_use_case']:
            recommendations['identified_use_case'] = 'general_application'
        
        # Ensure requirement_priorities exists
        if 'requirement_priorities' not in recommendations or not recommendations['requirement_priorities']:
            recommendations['requirement_priorities'] = {
                'security': 0.8,
                'scalability': 0.7,
                'reliability': 0.9,
                'maintainability': 0.6,
                'cost': 0.5
            }
        
        # Ensure recommended_patterns exists
        if 'recommended_patterns' not in recommendations or not recommendations['recommended_patterns']:
            recommendations['recommended_patterns'] = [
                {
                    'pattern': 'microservices',
                    'score': 0.85,
                    'details': {
                        'description': 'Architecture with small, independent services that communicate over a network',
                        'best_for': ['scalability', 'maintainability', 'agility'],
                        'caution_for': ['operational complexity', 'distributed systems challenges', 'network overhead'],
                        'components': [
                            'API Gateway', 'Service Registry', 'Authentication Service', 
                            'Business Services', 'Data Services', 'Monitoring'
                        ]
                    },
                    'reasoning': [
                        'Well suited for applications needing independent scaling',
                        'Supports team autonomy and parallel development',
                        'Good fit for cloud-native deployment'
                    ]
                }
            ]
        
        return render_template('applications/architecture_recommendations.html', 
                              application=application,
                              recommendations=recommendations)
    
    except Exception as e:
        current_app.logger.error(f"Error generating architecture recommendations: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        flash(f'Error generating architecture recommendations: {str(e)}', 'danger')
        return redirect(url_for('applications.application_detail', app_id=application.id))

@applications_bp.route('/applications/<int:app_id>/patterns')
@login_required
def patterns_analysis(app_id):
    """Analyze patterns and anti-patterns"""
    application = Application.query.get_or_404(app_id)
    
    # Check if user owns this application or is an ARB member or architect
    if application.user_id != current_user.id and not (current_user.is_arb_member() or current_user.is_architect()):
        flash('You do not have permission to view pattern analysis', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    # Get tech stack and use case
    tech_stack = application.baseline_systems or ''
    use_case = application.use_case or ''
    
    # Analyze patterns
    pattern_analyzer = get_pattern_analyzer(cpu_optimized=True)
    analysis = pattern_analyzer.analyze_tech_stack(tech_stack, use_case)
    
    # Store pattern analysis in the database
    application.pattern_analysis = str(analysis)
    db.session.commit()
    
    return render_template('applications/patterns_analysis.html', 
                          application=application,
                          analysis=analysis)

@applications_bp.route('/applications/<int:app_id>/generate_diagram', methods=['GET', 'POST'])
@login_required
def generate_diagram(app_id):
    """Generate architecture diagram"""
    application = Application.query.get_or_404(app_id)
    
    # Check if user owns this application or is an ARB member or architect
    if application.user_id != current_user.id and not (current_user.is_arb_member() or current_user.is_architect()):
        flash('You do not have permission to generate diagrams', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    if request.method == 'POST':
        diagram_type = request.form.get('diagram_type')
        
        # Create diagram generator
        diagram_generator = get_diagram_generator(current_app.config['UPLOAD_FOLDER'], cpu_optimized=True)
        
        if diagram_type == 'system_architecture':
            # Get components and connections from form
            components = [
                {
                    'name': name,
                    'type': type_,
                    'description': desc
                }
                for name, type_, desc in zip(
                    request.form.getlist('component_name'),
                    request.form.getlist('component_type'),
                    request.form.getlist('component_description')
                )
            ]
            
            connections = [
                {
                    'from': from_comp,
                    'to': to_comp,
                    'type': conn_type,
                    'description': desc
                }
                for from_comp, to_comp, conn_type, desc in zip(
                    request.form.getlist('connection_from'),
                    request.form.getlist('connection_to'),
                    request.form.getlist('connection_type'),
                    request.form.getlist('connection_description')
                )
            ]
            
            title = f"{application.name} - System Architecture"
            result = diagram_generator.generate_system_architecture_diagram(components, connections, title)
        
        elif diagram_type == 'deployment':
            # Get environments and components from form
            environments = [
                {
                    'name': name,
                    'description': desc
                }
                for name, desc in zip(
                    request.form.getlist('environment_name'),
                    request.form.getlist('environment_description')
                )
            ]
            
            components = [
                {
                    'name': name,
                    'type': type_,
                    'env': env,
                    'host': host
                }
                for name, type_, env, host in zip(
                    request.form.getlist('component_name'),
                    request.form.getlist('component_type'),
                    request.form.getlist('component_env'),
                    request.form.getlist('component_host')
                )
            ]
            
            title = f"{application.name} - Deployment Architecture"
            result = diagram_generator.generate_deployment_diagram(environments, components, title)
        
        elif diagram_type == 'data_model':
            # Get entities and relationships from form
            entities = [
                {
                    'name': name,
                    'attributes': [
                        {
                            'name': attr_name,
                            'type': attr_type,
                            'key': 'primary_key' in attr_flags
                        }
                        for attr_name, attr_type, attr_flags in zip(
                            request.form.getlist(f'entity_{name}_attr_name'),
                            request.form.getlist(f'entity_{name}_attr_type'),
                            request.form.getlist(f'entity_{name}_attr_flags')
                        )
                    ]
                }
                for name in request.form.getlist('entity_name')
            ]
            
            relationships = [
                {
                    'from': from_entity,
                    'to': to_entity,
                    'type': rel_type
                }
                for from_entity, to_entity, rel_type in zip(
                    request.form.getlist('relationship_from'),
                    request.form.getlist('relationship_to'),
                    request.form.getlist('relationship_type')
                )
            ]
            
            title = f"{application.name} - Data Model"
            result = diagram_generator.generate_data_model_diagram(entities, relationships, title)
        
        elif diagram_type == 'sequence':
            # Get sequence steps from form
            sequence = [
                {
                    'from': from_actor,
                    'to': to_actor,
                    'action': action,
                    'notes': notes
                }
                for from_actor, to_actor, action, notes in zip(
                    request.form.getlist('sequence_from'),
                    request.form.getlist('sequence_to'),
                    request.form.getlist('sequence_action'),
                    request.form.getlist('sequence_notes')
                )
            ]
            
            title = f"{application.name} - Sequence Diagram"
            result = diagram_generator.generate_sequence_diagram(sequence, title)
        
        elif diagram_type == 'mermaid':
            # Get Mermaid syntax from form
            mermaid_code = request.form.get('mermaid_code', '')
            title = f"{application.name} - {request.form.get('mermaid_title', 'Diagram')}"
            result = diagram_generator.generate_mermaid_diagram(mermaid_code, title)
        
        else:
            flash('Invalid diagram type', 'danger')
            return redirect(request.url)
        
        if result['success']:
            flash('Diagram generated successfully', 'success')
            
            # Return diagram info
            return jsonify({
                'success': True,
                'file_path': result['file_path'],
                'file_name': result['file_name']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            })
    
    # GET request - show form
    return render_template('applications/generate_diagram.html', 
                          application=application)

@applications_bp.route('/applications/<int:app_id>/submit_for_review', methods=['POST'])
@login_required
def submit_for_review(app_id):
    """Submit application for ARB review"""
    application = Application.query.get_or_404(app_id)
    
    # Check if user owns this application
    if application.user_id != current_user.id:
        flash('You do not have permission to submit this application for review', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    # Check if application is in PTI stage
    if not application.is_in_pti_stage():
        flash('This application is already in review or has been approved', 'warning')
        return redirect(url_for('applications.application_detail', app_id=application.id))
    
    # Update application status
    application.update_status('In Review')
    
    flash('Application submitted for ARB review', 'success')
    return redirect(url_for('applications.application_detail', app_id=application.id))

@applications_bp.route('/api/ask_question', methods=['POST'])
@login_required
def ask_question():
    """API endpoint for asking architecture questions"""
    data = request.get_json()
    
    if not data or 'question' not in data:
        return jsonify({
            'success': False,
            'error': 'No question provided'
        })
    
    question = data['question']
    app_id = data.get('app_id')
    
    # For a real implementation, this would connect to an LLM or knowledge base
    # Here we're providing a simple response based on keywords
    
    response = "I'm sorry, I don't have enough information to answer that question."
    
    # Simple keyword-based responses
    if 'microservices' in question.lower():
        response = """
        Microservices architecture involves building applications as a collection of small, independent services.
        
        Pros:
        - Independent scaling of services
        - Technology diversity
        - Resilience through isolation
        - Easier continuous deployment
        
        Cons:
        - Increased operational complexity
        - Distributed system debugging challenges
        - Network latency
        - Data consistency issues
        
        Best use cases:
        - Large, complex applications
        - Applications requiring independent scaling of components
        - Teams with clear domain boundaries
        """
    elif 'serverless' in question.lower():
        response = """
        Serverless architecture allows you to build applications without managing servers.
        
        Pros:
        - No server management
        - Pay-per-use pricing
        - Automatic scaling
        - Focus on code not infrastructure
        
        Cons:
        - Cold start latency
        - Limited execution duration
        - Vendor lock-in
        - Limited local testing
        
        Best use cases:
        - Event-driven workloads
        - Microservices
        - APIs with variable traffic
        - Applications with unpredictable usage patterns
        """
    elif 'cloud provider' in question.lower() or 'aws vs azure' in question.lower():
        response = """
        Major cloud providers comparison:
        
        AWS:
        - Largest market share
        - Widest range of services
        - Global presence
        - Most mature ecosystem
        
        Azure:
        - Strong enterprise integration
        - Hybrid cloud capabilities
        - Microsoft ecosystem integration
        - Strong compliance offerings
        
        Google Cloud:
        - Strong in data analytics and ML
        - Kubernetes excellence
        - Global network performance
        - Cost optimization features
        
        Oracle Cloud:
        - Oracle database performance
        - Integrated stack for Oracle workloads
        - Enterprise-focused
        - Aggressive pricing models
        """
    
    return jsonify({
        'success': True,
        'response': response
    })