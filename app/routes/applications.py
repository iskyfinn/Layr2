import os
import uuid
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, current_app, jsonify
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models.application import Application, ApplicationTechnology
from app import db

# Services
from app.services.hldd_analyzer import get_analyzer
from app.services.architecture_recommender import get_recommender
from app.services.modernization_strategy import get_modernization_strategy
from app.services.pattern_analyzer import get_pattern_analyzer
from app.services.document_generator import get_document_generator
from app.services.diagram_generator import get_diagram_generator

# Blueprint
applications_bp = Blueprint('applications', __name__, template_folder='../templates/applications')

# Allowed file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'pptx', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dashboard view
@applications_bp.route('/dashboard')
@login_required
def dashboard():
    user_applications = Application.query.filter_by(user_id=current_user.id).all()
    return render_template('applications/dashboard.html', 
                           applications=user_applications, 
                           user=current_user)

# New application view and submission
@applications_bp.route('/applications/new', methods=['GET', 'POST'])
@login_required
def new_application():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        use_case = request.form.get('use_case')
        baseline_systems = request.form.get('baseline_systems')
        requirements = request.form.get('requirements')

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

@applications_bp.route('/applications/<int:app_id>/upload_hldd', methods=['GET', 'POST'])
@login_required
def upload_hldd(app_id):
    """Upload HLDD file for analysis"""
    application = Application.query.get_or_404(app_id)
    
    # Check if user owns this application
    if application.user_id != current_user.id:
        flash('You do not have permission to upload HLDD for this application', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'hldd_file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['hldd_file']
        
        # Check if file is empty
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        # Check if file is allowed
        if file and allowed_file(file.filename):
            # Secure the filename and create a unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Create upload directory if it doesn't exist
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Update application with HLDD path
            application.hldd_path = file_path
            application.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Redirect to HLDD analysis page
            return redirect(url_for('applications.analyze_hldd', app_id=application.id))
        else:
            flash('File type not allowed. Please upload a valid document', 'danger')
            return redirect(request.url)
    
    # GET request - show upload form
    return render_template('applications/upload_hldd.html', 
                          application=application)

@applications_bp.route('/applications/<int:app_id>/analyze_hldd')
@login_required
def analyze_hldd(app_id):
    """Analyze uploaded HLDD"""
    application = Application.query.get_or_404(app_id)
    
    # Check if user owns this application or is an ARB member
    if application.user_id != current_user.id and not current_user.is_arb_member():
        flash('You do not have permission to analyze this application', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    # Check if HLDD exists
    if not application.hldd_path or not os.path.exists(application.hldd_path):
        flash('No HLDD found for this application', 'danger')
        return redirect(url_for('applications.application_detail', app_id=application.id))
    
    # Define analyze_document function directly
    def analyze_document(path):
        # Return a simple result for now
        return {
            'status': 'success',
            'message': 'Document analysis placeholder',
            'overall_score': 85,
            'insights': [
                {'type': 'info', 'message': 'Document appears to be an HLDD'},
                {'type': 'warning', 'message': 'Sample warning message'},
                {'type': 'positive', 'message': 'Sample positive insight'}
            ]
        }
    
    # Use the function directly instead of through analyzer
    results = analyze_document(application.hldd_path)
    
    # Update application with analysis results
    application.architecture_score = results['overall_score']
    db.session.commit()
    
    return render_template('applications/hldd_analysis.html', 
                          application=application,
                          results=results)
    # Create a placeholder implementation
    def analyze_document(path):
        # Return a simple result for now
        return {
            'status': 'success',
            'message': 'Document analysis placeholder',
            'insights': [
                {'type': 'info', 'message': 'Document appears to be an HLDD'},
                {'type': 'warning', 'message': 'Sample warning message'},
                {'type': 'positive', 'message': 'Sample positive insight'}
            ]
        }

    # Then use it
    results = analyze_document(application.hldd_path)

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
    
    # Get architecture recommendations
    recommender = get_recommender()
    recommendations = recommender.recommend_architecture(
        application.use_case,
        application.requirements,
        application.baseline_systems
    )
    
    return render_template('applications/architecture_recommendations.html', 
                          application=application,
                          recommendations=recommendations)

@applications_bp.route('/applications/<int:app_id>/modernization')
@login_required
def modernization_strategies(app_id):
    """Recommend modernization strategies"""
    application = Application.query.get_or_404(app_id)
    
    # Check if user owns this application or is an ARB member or architect
    if application.user_id != current_user.id and not (current_user.is_arb_member() or current_user.is_architect()):
        flash('You do not have permission to view modernization strategies', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    # Application info for modernization analysis
    app_info = {
        'description': application.description or '',
        'tech_stack': application.baseline_systems or '',
        'age': 'legacy' if 'legacy' in (application.description or '').lower() else 'new',
        'business_value': application.use_case or ''
    }
    
    # Create a placeholder implementation for document analysis
    def analyze_document(path):
        # Return a simple result for now
        return {
            'status': 'success',
            'message': 'Document analysis placeholder',
            'overall_score': 85,
            'insights': [
                {'type': 'info', 'message': 'Document appears to be an HLDD'},
                {'type': 'warning', 'message': 'Sample warning message'},
                {'type': 'positive', 'message': 'Sample positive insight'}
            ]
        }
    
    # Get HLDD analysis if available
    hldd_analysis = None
    if application.hldd_path and os.path.exists(application.hldd_path):
        # Use the placeholder function directly instead of the analyzer object
        hldd_analysis = analyze_document(application.hldd_path)
    
    # Implement a simple function instead of using a lambda
    def get_modernization_strategy():
        class ModernizationStrategy:
            def recommend_strategy(self, app_info, hldd_analysis, **kwargs):
                return {
                    'recommended_strategies': [
                        {
                            'name': 'Cloud Migration',
                            'description': 'Migrate the application to a cloud platform for improved scalability and reduced infrastructure costs.',
                            'benefits': ['Cost reduction', 'Improved scalability', 'Reduced maintenance'],
                            'considerations': ['Data migration complexity', 'Initial setup costs', 'Staff training'],
                            'score': 85
                        },
                        {
                            'name': 'Microservices Transformation',
                            'description': 'Split the monolithic application into microservices for better maintainability and deployment flexibility.',
                            'benefits': ['Independent deployments', 'Technology flexibility', 'Better fault isolation'],
                            'considerations': ['Increased complexity', 'API management challenges', 'Service coordination'],
                            'score': 75
                        },
                        {
                            'name': 'Containerization',
                            'description': 'Deploy the application in containers for consistency across environments and improved resource utilization.',
                            'benefits': ['Environment consistency', 'Resource efficiency', 'Deployment simplicity'],
                            'considerations': ['Container orchestration learning curve', 'Stateful services challenges'],
                            'score': 90
                        }
                    ]
                }
        return ModernizationStrategy()
    
    # Get modernization recommendations
    modernization = get_modernization_strategy()
    strategies = modernization.recommend_strategy(app_info, hldd_analysis)
    
    # Store recommendations in the database
    application.modernization_recommendations = str(strategies.get('recommended_strategies', []))
    db.session.commit()
    
    return render_template('applications/modernization_strategies.html', 
                          application=application,
                          strategies=strategies)

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

@applications_bp.route('/applications/<int:app_id>/generate_hldd', methods=['GET', 'POST'])
@login_required
def generate_hldd(app_id):
    """Generate HLDD document"""
    application = Application.query.get_or_404(app_id)
    
    # Check if user owns this application or is an ARB member or architect
    if application.user_id != current_user.id and not (current_user.is_arb_member() or current_user.is_architect()):
        flash('You do not have permission to generate HLDD', 'danger')
        return redirect(url_for('applications.dashboard'))
    
    if request.method == 'POST':
        # Get form data
        application_info = {
            'name': application.name,
            'author': current_user.username,
            'version': '1.0',
            'purpose': request.form.get('purpose'),
            'scope': request.form.get('scope'),
            'overview': request.form.get('overview'),
            'functions': request.form.getlist('functions'),
            'user_roles': [
                {'role': role, 'description': desc} 
                for role, desc in zip(
                    request.form.getlist('role_name'),
                    request.form.getlist('role_description')
                )
            ]
        }
        
        tech_stack_info = {
            'overview': request.form.get('tech_overview'),
            'categories': [
                {
                    'name': category,
                    'technologies': [
                        {
                            'name': tech,
                            'version': ver,
                            'purpose': purpose
                        }
                        for tech, ver, purpose in zip(
                            request.form.getlist(f'{category}_tech_name'),
                            request.form.getlist(f'{category}_tech_version'),
                            request.form.getlist(f'{category}_tech_purpose')
                        )
                    ]
                }
                for category in request.form.getlist('tech_category')
            ]
        }
        
        architecture_info = {
            'overview': request.form.get('arch_overview'),
            'principles': request.form.getlist('principles'),
            'components': [
                {
                    'name': name,
                    'description': desc
                }
                for name, desc in zip(
                    request.form.getlist('component_name'),
                    request.form.getlist('component_description')
                )
            ],
            'data_architecture': {
                'overview': request.form.get('data_overview'),
                'data_stores': [
                    {
                        'name': name,
                        'type': type_,
                        'purpose': purpose
                    }
                    for name, type_, purpose in zip(
                        request.form.getlist('datastore_name'),
                        request.form.getlist('datastore_type'),
                        request.form.getlist('datastore_purpose')
                    )
                ]
            },
            'security': {
                'overview': request.form.get('security_overview'),
                'authentication': request.form.get('authentication'),
                'data_protection': request.form.get('data_protection'),
                'network_security': request.form.get('network_security')
            },
            'deployment': {
                'overview': request.form.get('deployment_overview'),
                'environments': [
                    {
                        'name': name,
                        'description': desc
                    }
                    for name, desc in zip(
                        request.form.getlist('environment_name'),
                        request.form.getlist('environment_description')
                    )
                ]
            }
        }
        
        # Create document generator
        doc_generator = get_document_generator(current_app.config['UPLOAD_FOLDER'])
        
        # Generate HLDD
        result = doc_generator.generate_hldd(application_info, tech_stack_info, architecture_info)
        
        if result['success']:
            # Update application with generated HLDD path
            application.hldd_path = result['file_path']
            application.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('HLDD generated successfully', 'success')
            return redirect(url_for('applications.application_detail', app_id=application.id))
        else:
            flash(f"Failed to generate HLDD: {result.get('error', 'Unknown error')}", 'danger')
            return redirect(request.url)
    
    # GET request - show form
    return render_template('applications/generate_hldd.html', 
                          application=application)

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