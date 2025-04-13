# app/services/architecture_agent.py

import os
import logging
import json
import datetime
from typing import Dict, Any, List, Optional, Tuple
import threading
import time
import uuid
from flask import current_app

# Import your existing services
from app.services.hldd_generator import get_document_generator
from app.services.modernization_strategy import modernization_strategy
from app.services.pattern_analyzer import get_pattern_analyzer
from app.services.architecture_recommender import get_recommender
from app.services.diagram_generator import get_diagram_generator
from app.services.modernization_strategy import get_modernization_strategy

class ArchitectureAgent:
    """
    An autonomous agent for intelligent architecture analysis and recommendation.
    
    This service integrates various architecture services to provide a more proactive
    and intelligent experience, helping users with architecture decisions, documentation
    generation, and ongoing guidance.
    """
    
    def __init__(self, 
                 upload_folder: str, 
                 enable_background_tasks: bool = True,
                 analysis_interval: int = 3600):  # Default to hourly analysis
        """
        Initialize the Architecture Agent
        
        Args:
            upload_folder: Folder to store generated documents and artifacts
            enable_background_tasks: Whether to enable background processing
            analysis_interval: Interval for periodic analysis (in seconds)
        """
        self.upload_folder = upload_folder
        self.enable_background_tasks = enable_background_tasks
        self.analysis_interval = analysis_interval
        
        # Create output folders
        self.documents_folder = os.path.join(upload_folder, 'documents')
        self.diagrams_folder = os.path.join(upload_folder, 'diagrams')
        os.makedirs(self.documents_folder, exist_ok=True)
        os.makedirs(self.diagrams_folder, exist_ok=True)
        
        # Initialize component services
        self.hldd_analyzer = None  # Initialize on demand
        self.document_generator = get_document_generator(self.documents_folder)
        # self.modernization_strategy = modernization_strategy()
        self.pattern_analyzer = get_pattern_analyzer()
        # self.architecture_recommender = get_recommender()
        self.diagram_generator = get_diagram_generator(self.diagrams_folder)
        
        # Store analysis results and insights for applications
        self.application_insights = {}
        self.pending_tasks = {}
        self.analysis_queue = []
        
        # Start background processing if enabled
        if enable_background_tasks:
            self.start_background_processing()
    
    def analyze_application(self, 
                           application_id: str, 
                           application_data: Dict[str, Any],
                           hldd_path: Optional[str] = None,
                           user_notes: Optional[str] = None,
                           priority: int = 1) -> str:
        """
        Queue an application for comprehensive analysis
        
        Args:
            application_id: Unique identifier for the application
            application_data: Application details
            hldd_path: Optional path to HLDD document for analysis
            user_notes: Optional notes from user
            priority: Task priority (1-5, 5 being highest)
            
        Returns:
            task_id: Identifier for the queued analysis task
        """
        task_id = str(uuid.uuid4())
        
        # Create task for processing
        task = {
            'task_id': task_id,
            'application_id': application_id,
            'application_data': application_data,
            'hldd_path': hldd_path,
            'user_notes': user_notes,
            'priority': priority,
            'status': 'queued',
            'created_at': datetime.datetime.utcnow().isoformat(),
            'results': None
        }
        
        # Add to pending tasks
        self.pending_tasks[task_id] = task
        
        # Add to queue with priority
        self.analysis_queue.append((priority, task_id))
        self.analysis_queue.sort(reverse=True)  # Sort by priority (highest first)
        
        # If immediate processing is needed for high priority
        if priority >= 4 and not self.enable_background_tasks:
            self._process_analysis_task(task_id)
        
        return task_id
    
    def get_analysis_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of an analysis task
        
        Args:
            task_id: Task identifier
            
        Returns:
            dict: Task status and results if completed
        """
        if task_id not in self.pending_tasks:
            return {'status': 'not_found'}
        
        task = self.pending_tasks[task_id]
        response = {
            'task_id': task_id,
            'status': task['status'],
            'application_id': task['application_id'],
            'created_at': task['created_at']
        }
        
        # Include results if available
        if task['status'] == 'completed' and task['results']:
            response['results'] = task['results']
        
        return response
    
    def get_application_insights(self, application_id: str) -> Dict[str, Any]:
        """
        Get comprehensive insights for an application
        
        Args:
            application_id: Application identifier
            
        Returns:
            dict: Insights, recommendations, and analysis for the application
        """
        if application_id not in self.application_insights:
            return {'status': 'no_insights'}
        
        return self.application_insights[application_id]
    
    def generate_hldd(self, 
                     application_data: Dict[str, Any],
                     user_inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate HLDD document with intelligent recommendations
        
        Args:
            application_data: Application details
            user_inputs: Additional user inputs for document generation
            
        Returns:
            dict: Generated document information
        """
        try:
            # Get arch recommendations based on description
            description = application_data.get('description', '')
            use_case = application_data.get('use_case', '')
            requirements = application_data.get('requirements', '')
            
            # Get architecture recommendations
            arch_recommendations = self.architecture_recommender.recommend_architecture(
                use_case or description,
                requirements or description
            )
            
            # Get pattern recommendations
            tech_stack = application_data.get('technology_stack', '')
            pattern_analysis = self.pattern_analyzer.analyze_tech_stack(
                tech_stack or description,
                use_case or description
            )
            
            # Prepare HLDD data
            hldd_data = {
                'basicInfo': {
                    'name': application_data.get('name', 'New Application'),
                    'description': description,
                    'version': application_data.get('version', '1.0'),
                    'author': application_data.get('owner', 'Architecture Team')
                },
                'technologyStack': {
                    'overview': 'Recommended technology stack based on application requirements',
                    'categories': self._format_technology_stack(
                        tech_stack,
                        arch_recommendations
                    )
                },
                'architectureInfo': {
                    'overview': 'Recommended architecture based on requirements analysis',
                    'architectural_style': self._get_primary_architecture_style(arch_recommendations),
                    'components': self._extract_components_from_patterns(pattern_analysis),
                    'principles': self._extract_architecture_principles(arch_recommendations, pattern_analysis),
                    'security': self._determine_security_requirements(requirements or description)
                }
            }
            
            # Merge with user inputs if provided
            if user_inputs:
                hldd_data = self._merge_dict(hldd_data, user_inputs)
            
            # Generate document
            result = self.document_generator.generate_hldd(
                None,  # No application model here
                user_inputs,
                hldd_data
            )
            
            # Add recommendations to the result
            result['recommendations'] = {
                'architecture': arch_recommendations,
                'patterns': pattern_analysis
            }
            
            return result
        
        except Exception as e:
            logging.error(f"Error generating HLDD: {str(e)}")
            return {
                'error': str(e),
                'success': False
            }
    
    def recommend_modernization(self, 
                              application_data: Dict[str, Any],
                              hldd_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Provide modernization recommendations for an application
        
        Args:
            application_data: Application details
            hldd_analysis: Optional HLDD analysis results
            
        Returns:
            dict: Modernization recommendations
        """
        try:
            return self.modernization_strategy.recommend_strategy(
                application_data,
                hldd_analysis
            )
        except Exception as e:
            logging.error(f"Error generating modernization recommendations: {str(e)}")
            return {
                'error': str(e),
                'recommended_strategies': []
            }
    
    def generate_diagrams(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate architecture diagrams from application description
        
        Args:
            application_data: Application details
            
        Returns:
            dict: Generated diagram information
        """
        try:
            # Extract architecture components from description
            components = self._extract_components_from_description(
                application_data.get('description', ''),
                application_data.get('technology_stack', '')
            )
            
            # Generate system architecture diagram
            connections = self._identify_component_connections(components)
            system_diagram = self.diagram_generator.generate_system_architecture_diagram(
                components,
                connections,
                f"{application_data.get('name', 'Application')} System Architecture"
            )
            
            # Generate data model if applicable
            data_entities = self._extract_data_entities(
                application_data.get('description', ''),
                application_data.get('data_model', '')
            )
            
            data_relationships = []
            if data_entities:
                data_relationships = self._identify_entity_relationships(data_entities)
                
            data_model_diagram = None
            if data_entities and data_relationships:
                data_model_diagram = self.diagram_generator.generate_data_model_diagram(
                    data_entities,
                    data_relationships,
                    f"{application_data.get('name', 'Application')} Data Model"
                )
            
            # Generate mermaid diagram for more complex relationships
            mermaid_diagram = self._generate_mermaid_architecture_diagram(
                components, 
                connections,
                application_data.get('name', 'Application')
            )
            
            return {
                'system_diagram': system_diagram,
                'data_model_diagram': data_model_diagram,
                'mermaid_diagram': mermaid_diagram,
                'success': True
            }
            
        except Exception as e:
            logging.error(f"Error generating diagrams: {str(e)}")
            return {
                'error': str(e),
                'success': False
            }
    
    def analyze_hldd(self, hldd_path: str) -> Dict[str, Any]:
        from app.services.hldd_analyzer import HLDDAnalyzer


        """
        Analyze HLDD document for architecture assessment
        
        Args:
            hldd_path: Path to HLDD document
            
        Returns:
            dict: Analysis results with quality scores and recommendations
        """
        try:
            # Initialize HLDD analyzer if not already done
            if not self.hldd_analyzer:
                self.hldd_analyzer = HLDDAnalyzer(hldd_path)
                analyzer = get_hldd_analyzer()

            # Perform analysis
            results = self.hldd_analyzer.analyze_document(hldd_path)
            
            # Add agent-specific insights
            results['agent_insights'] = self._generate_architecture_insights(results)
            
            return results
            
        except Exception as e:
            logging.error(f"Error analyzing HLDD: {str(e)}")
            return {
                'error': str(e),
                'scores': {},
                'missing_components': [],
                'overall_score': 0,
                'acceptable': False,
                'recommendations': ["Error analyzing document. Please try again."]
            }
    
    def get_next_actions(self, application_id: str) -> List[Dict[str, Any]]:
        """
        Determine next recommended actions for an application
        
        Args:
            application_id: Application identifier
            
        Returns:
            list: Recommended next actions for the application
        """
        if application_id not in self.application_insights:
            return [{"action": "analyze", "description": "Perform initial analysis"}]
        
        insights = self.application_insights[application_id]
        next_actions = []
        
        # Check for missing HLDD
        if not insights.get('has_hldd', False):
            next_actions.append({
                "action": "generate_hldd",
                "description": "Generate High Level Design Document",
                "priority": "high"
            })
        
        # Check for architecture issues
        if insights.get('architecture_score', 0) < 0.7:
            next_actions.append({
                "action": "review_architecture",
                "description": "Review and update architecture design",
                "priority": "high",
                "specific_issues": insights.get('architecture_issues', [])
            })
        
        # Check for security issues
        if insights.get('security_score', 0) < 0.6:
            next_actions.append({
                "action": "address_security",
                "description": "Address security concerns in the design",
                "priority": "high",
                "specific_issues": insights.get('security_issues', [])
            })
        
        # Check for missing diagrams
        if not insights.get('has_diagrams', False):
            next_actions.append({
                "action": "generate_diagrams",
                "description": "Generate architecture diagrams",
                "priority": "medium"
            })
        
        # Check for modernization opportunities
        if insights.get('modernization_opportunities', []):
            next_actions.append({
                "action": "evaluate_modernization",
                "description": "Evaluate modernization opportunities",
                "priority": "medium",
                "opportunities": insights.get('modernization_opportunities', [])
            })
        
        # If all is well, suggest review or enhancement
        if not next_actions:
            next_actions.append({
                "action": "enhance_design",
                "description": "Consider enhancements to the current design",
                "priority": "low",
                "suggestions": ["Add more detailed component interactions", 
                              "Document non-functional requirements",
                              "Add operational procedures"]
            })
        
        return next_actions
    
    def start_background_processing(self):
        """Start background thread for processing analysis tasks"""
        self.is_running = True
        self.background_thread = threading.Thread(target=self._background_processor)
        self.background_thread.daemon = True
        self.background_thread.start()
        
        # Start periodic analysis thread
        self.periodic_thread = threading.Thread(target=self._periodic_analyzer)
        self.periodic_thread.daemon = True
        self.periodic_thread.start()
    
    def stop_background_processing(self):
        """Stop background processing threads"""
        self.is_running = False
    
    # Internal methods
    
    def _background_processor(self):
        """Background thread to process analysis queue"""
        while self.is_running:
            try:
                # Check if there are tasks in the queue
                if self.analysis_queue:
                    # Get highest priority task
                    _, task_id = self.analysis_queue.pop(0)
                    
                    # Process the task
                    self._process_analysis_task(task_id)
                
                # Sleep briefly before checking again
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error in background processor: {str(e)}")
                time.sleep(5)  # Sleep longer on error
    
    def _periodic_analyzer(self):
        """Periodically analyze applications for new insights"""
        while self.is_running:
            try:
                # Get applications to analyze
                app_ids = list(self.application_insights.keys())
                
                for app_id in app_ids:
                    try:
                        # Check last analysis time
                        insights = self.application_insights[app_id]
                        last_analysis = insights.get('last_analysis_time', None)
                        
                        if not last_analysis:
                            continue
                            
                        # Parse last analysis time
                        last_time = datetime.datetime.fromisoformat(last_analysis)
                        now = datetime.datetime.utcnow()
                        
                        # If enough time has passed, re-analyze
                        if (now - last_time).total_seconds() >= self.analysis_interval:
                            # Queue for re-analysis with low priority
                            if 'application_data' in insights:
                                self.analyze_application(
                                    app_id,
                                    insights['application_data'],
                                    priority=1  # Low priority for periodic analysis
                                )
                    
                    except Exception as e:
                        logging.error(f"Error during periodic analysis of app {app_id}: {str(e)}")
                
                # Sleep until next analysis interval
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                logging.error(f"Error in periodic analyzer: {str(e)}")
                time.sleep(60)  # Sleep for a minute on error
    
    def _process_analysis_task(self, task_id: str):
        """Process a queued analysis task"""
        if task_id not in self.pending_tasks:
            return
        
        task = self.pending_tasks[task_id]
        
        try:
            # Update status
            task['status'] = 'processing'
            
            application_id = task['application_id']
            application_data = task['application_data']
            hldd_path = task['hldd_path']
            
            # Initialize insights for this application if not exists
            if application_id not in self.application_insights:
                self.application_insights[application_id] = {
                    'application_id': application_id,
                    'application_data': application_data,
                    'creation_time': datetime.datetime.utcnow().isoformat()
                }
            
            insights = self.application_insights[application_id]
            
            # Step 1: Analyze HLDD if available
            hldd_analysis = None
            if hldd_path:
                hldd_analysis = self.analyze_hldd(hldd_path)
                insights['hldd_analysis'] = hldd_analysis
                insights['has_hldd'] = True
                insights['hldd_path'] = hldd_path
                
                # Extract architecture and security scores
                if 'scores' in hldd_analysis:
                    arch_score = 0
                    security_score = 0
                    
                    if 'scalability' in hldd_analysis['scores']:
                        arch_score += hldd_analysis['scores']['scalability']['score']
                    
                    if 'reliability' in hldd_analysis['scores']:
                        arch_score += hldd_analysis['scores']['reliability']['score']
                    
                    if 'maintainability' in hldd_analysis['scores']:
                        arch_score += hldd_analysis['scores']['maintainability']['score']
                    
                    if 'security' in hldd_analysis['scores']:
                        security_score = hldd_analysis['scores']['security']['score']
                    
                    # Average architecture score from components
                    if arch_score > 0:
                        arch_score = arch_score / 3.0
                    
                    insights['architecture_score'] = arch_score
                    insights['security_score'] = security_score
                    
                    # Identify issues
                    architecture_issues = []
                    security_issues = []
                    
                    for criterion, data in hldd_analysis['scores'].items():
                        if data['score'] < 0.5:
                            if criterion == 'security':
                                security_issues.append(f"Low score in {criterion}: {data['score']}")
                            else:
                                architecture_issues.append(f"Low score in {criterion}: {data['score']}")
                    
                    insights['architecture_issues'] = architecture_issues
                    insights['security_issues'] = security_issues
            
            # Step 2: Get architecture recommendations
            description = application_data.get('description', '')
            use_case = application_data.get('use_case', '')
            requirements = application_data.get('requirements', '')
            
            arch_recommendations = self.architecture_recommender.recommend_architecture(
                use_case or description,
                requirements or description
            )
            
            insights['architecture_recommendations'] = arch_recommendations
            
            # Step 3: Analyze patterns
            tech_stack = application_data.get('technology_stack', '')
            pattern_analysis = self.pattern_analyzer.analyze_tech_stack(
                tech_stack or description,
                use_case or description
            )
            
            insights['pattern_analysis'] = pattern_analysis
            
            # Check for anti-patterns
            if 'potential_anti_patterns' in pattern_analysis and pattern_analysis['potential_anti_patterns']:
                anti_patterns = pattern_analysis['potential_anti_patterns']
                insights['has_anti_patterns'] = True
                insights['anti_patterns'] = anti_patterns
                
                # Add to architecture issues
                if 'architecture_issues' not in insights:
                    insights['architecture_issues'] = []
                
                for anti in anti_patterns:
                    insights['architecture_issues'].append(
                        f"Anti-pattern detected: {anti['anti_pattern']}"
                    )
            
            # Step 4: Get modernization recommendations
            modernization = self.modernization_strategy.recommend_strategy(
                application_data,
                hldd_analysis
            )
            
            insights['modernization_recommendations'] = modernization
            
            # Extract top modernization opportunities
            if 'recommended_strategies' in modernization:
                insights['modernization_opportunities'] = [
                    {
                        'strategy': strategy['strategy']['name'],
                        'description': strategy['strategy']['description']
                    } for strategy in modernization['recommended_strategies'][:2]
                ]
            
            # Step 5: Generate diagrams if not already done
            if 'has_diagrams' not in insights or not insights['has_diagrams']:
                diagrams = self.generate_diagrams(application_data)
                if diagrams.get('success', False):
                    insights['has_diagrams'] = True
                    insights['diagrams'] = diagrams
            
            # Step 6: Generate next actions
            insights['next_actions'] = self.get_next_actions(application_id)
            
            # Update analysis time
            insights['last_analysis_time'] = datetime.datetime.utcnow().isoformat()
            
            # Mark task as completed
            task['status'] = 'completed'
            task['results'] = {
                'insights_available': True,
                'next_actions': insights['next_actions']
            }
            
        except Exception as e:
            logging.error(f"Error processing analysis task {task_id}: {str(e)}")
            task['status'] = 'error'
            task['error'] = str(e)
    
    def _format_technology_stack(self, tech_stack_text, arch_recommendations):
        """Format technology stack for HLDD from recommendations"""
        categories = []
        
        # Extract recommendations from architecture analysis
        if 'recommended_patterns' in arch_recommendations:
            pattern = arch_recommendations['recommended_patterns'][0]['pattern']
            pattern_details = arch_recommendations['recommended_patterns'][0]['details']
            
            # Extract recommended components
            if 'components' in pattern_details:
                components = pattern_details['components']
                
                # Group components by category
                component_categories = {}
                
                for component in components:
                    # Simple categorization based on component name
                    if 'API' in component or 'Gateway' in component:
                        category = 'API Layer'
                    elif 'Service' in component or 'Backend' in component:
                        category = 'Services Layer'
                    elif 'Database' in component or 'Data' in component:
                        category = 'Data Layer'
                    elif 'Frontend' in component or 'UI' in component:
                        category = 'Frontend'
                    elif 'Monitor' in component or 'Log' in component:
                        category = 'Operations'
                    else:
                        category = 'Infrastructure'
                    
                    if category not in component_categories:
                        component_categories[category] = []
                    
                    component_categories[category].append(component)
                
                # Format into categories
                for category, components in component_categories.items():
                    tech_category = {
                        'name': category,
                        'technologies': []
                    }
                    
                    for component in components:
                        tech_category['technologies'].append({
                            'name': component,
                            'version': 'Latest',
                            'purpose': f"Supports {pattern} architecture"
                        })
                    
                    categories.append(tech_category)
        
        # If we have text about technologies, try to extract more specific info
        if tech_stack_text:
            # This would be enhanced with NLP in a real implementation
            tech_mentions = self._extract_technologies_from_text(tech_stack_text)
            
            if tech_mentions:
                tech_category = {
                    'name': 'Mentioned Technologies',
                    'technologies': []
                }
                
                for tech in tech_mentions:
                    tech_category['technologies'].append({
                        'name': tech,
                        'version': 'Specified by user',
                        'purpose': 'User-specified technology'
                    })
                
                categories.append(tech_category)
        
        # Ensure we have at least some categories
        if not categories:
            categories = [
                {
                    'name': 'Frontend',
                    'technologies': [
                        {
                            'name': 'React',
                            'version': 'Latest',
                            'purpose': 'User interface framework'
                        }
                    ]
                },
                {
                    'name': 'Backend',
                    'technologies': [
                        {
                            'name': 'Python (Flask)',
                            'version': 'Latest',
                            'purpose': 'Server-side logic and API'
                        }
                    ]
                }
            ]
        
        return categories
    
    def _get_primary_architecture_style(self, arch_recommendations):
        """Extract primary architecture style from recommendations"""
        if 'recommended_patterns' in arch_recommendations and arch_recommendations['recommended_patterns']:
            return arch_recommendations['recommended_patterns'][0]['pattern']
        
        return 'Layered'  # Default if no recommendation
    
    def _extract_components_from_patterns(self, pattern_analysis):
        """Extract component recommendations from pattern analysis"""
        components = []
        
        if 'relevant_patterns' in pattern_analysis:
            for pattern in pattern_analysis['relevant_patterns']:
                pattern_name = pattern['pattern']
                
                # Create a component based on the pattern
                components.append({
                    'name': pattern_name.replace('_', ' ').title(),
                    'description': pattern['description']
                })
                
                # Add related components based on implementations
                if 'implementations' in pattern:
                    for cloud, techs in pattern['implementations'].items():
                        for tech in techs[:2]:  # Take top 2 technologies
                            components.append({
                                'name': tech,
                                'description': f"Implementation of {pattern_name} pattern"
                            })
        
        return components
    
    def _extract_architecture_principles(self, arch_recommendations, pattern_analysis):
        """Extract architecture principles from recommendations"""
        principles = []
        
        # Add principles from recommended patterns
        if 'recommended_patterns' in arch_recommendations:
            for pattern in arch_recommendations['recommended_patterns']:
                if 'details' in pattern and 'best_for' in pattern['details']:
                    for strength in pattern['details']['best_for']:
                        principles.append(
                            f"{strength.capitalize()}: Design for {strength} following {pattern['pattern']} patterns"
                        )
        
        # Add principles from pattern benefits
        if 'relevant_patterns' in pattern_analysis:
            for pattern in pattern_analysis['relevant_patterns']:
                if 'benefits' in pattern:
                    for benefit in pattern['benefits'][:2]:  # Take top 2 benefits
                        principles.append(f"{benefit}")
        
        # Ensure we have some principles
        if not principles:
            principles = [
                'Scalability: The system should scale horizontally to handle increasing load',
                'Reliability: The system should be resilient to failures and maintain high availability',
                'Security: The system should implement defense in depth and follow security best practices',
                'Maintainability: The system should be easy to maintain and update'
            ]
        
        return principles
    
    def _determine_security_requirements(self, description):
        """Determine security requirements based on description"""
        description_lower = description.lower()
        
        # Look for security-related terms
        security_terms = [
            'security', 'confidential', 'sensitive', 'privacy', 'compliance',
            'GDPR', 'HIPAA', 'PCI', 'regulation', 'secure', 'encryption',
            'authentication', 'authorization', 'data protection'
        ]
        
        security_level = 'low_sensitivity'
        
        # Count security terms
        term_count = sum(1 for term in security_terms if term.lower() in description_lower)
        
        if term_count >= 3:
            security_level = 'high_sensitivity'
        elif term_count >= 1:
            security_level = 'medium_sensitivity'
        
        # Define security templates based on level
        security_templates = {
            'low_sensitivity': {
                'overview': 'Basic security measures for low-risk applications',
                'authentication': 'Basic username/password',
                'data_protection': 'Standard encryption for sensitive data',
                'network_security': 'Firewall and basic intrusion detection'
            },
            'medium_sensitivity': {
                'overview': 'Enhanced security for moderately sensitive applications',
                'authentication': 'Multi-factor authentication',
                'data_protection': 'Advanced encryption (AES-256)',
                'network_security': 'Network segmentation, advanced firewall rules'
            },
            'high_sensitivity': {
                'overview': 'Comprehensive security for highly sensitive applications',
                'authentication': 'Biometric + multi-factor authentication',
                'data_protection': 'End-to-end encryption, data masking',
                'network_security': 'Zero trust architecture, continuous monitoring'
            }
        }
        
        return security_templates[security_level]
    
def _extract_components_from_description(self, description, tech_stack):
    """Extract architecture components from description text"""
    components = []

    component_patterns = [
        {'pattern': r'\b(web|ui|frontend|interface|client)\b', 'type': 'user'},
        {'pattern': r'\b(api gateway|gateway|api management)\b', 'type': 'service'},
        {'pattern': r'\b(service|microservice|backend|server)\b', 'type': 'service'},
        {'pattern': r'\b(database|db|data store|repository|sql|nosql)\b', 'type': 'database'},
        {'pattern': r'\b(external|third.party|integration|external system)\b', 'type': 'external'},
        {'pattern': r'\b(auth|security|authentication|authorization)\b', 'type': 'service'},
        {'pattern': r'\b(monitor|logging|observability|telemetry)\b', 'type': 'service'}
    ]

    combined_text = f"{description} {tech_stack}".lower()

    for pattern_info in component_patterns:
        pattern = pattern_info['pattern']
        matches = re.findall(pattern, combined_text, re.IGNORECASE)
        if matches:
            component_type = pattern_info['type']
            component_name = self._format_component_name(matches[0])
            if not any(c['name'].lower() == component_name.lower() for c in components):
                components.append({
                    'name': component_name,
                    'type': component_type,
                    'description': self._generate_component_description(component_name, component_type)
                })

    if not any(c['type'] == 'user' for c in components):
        components.append({
            'name': 'User Interface',
            'type': 'user',
            'description': 'The frontend component responsible for user interactions'
        })

    if not any(c['type'] == 'service' for c in components):
        components.append({
            'name': 'Application Service',
            'type': 'service',
            'description': 'Core business logic and processing service'
        })

    if not any(c['type'] == 'database' for c in components):
        components.append({
            'name': 'Database',
            'type': 'database',
            'description': 'Persistent data storage'
        })

    return components


def _format_component_name(self, component_keyword):
    """Format a component name from a keyword"""
    if component_keyword.lower() in ['ui', 'db']:
        return component_keyword.upper() + " Component"
    elif component_keyword.lower() in ['api']:
        return component_keyword.upper() + " Gateway"
    else:
        words = component_keyword.split()
        capitalized = ' '.join(word.capitalize() for word in words)
        if component_keyword.lower() in ['database', 'data store', 'repository']:
            return capitalized
        elif component_keyword.lower() in ['web', 'frontend', 'client', 'interface']:
            return f"{capitalized} Interface"
        elif component_keyword.lower() in ['service', 'microservice', 'backend', 'server']:
            return f"{capitalized} Service"
        else:
            return f"{capitalized} Component"


def _generate_component_description(self, name, component_type):
    """Generate a description for a component based on its name and type"""
    if component_type == 'user':
        return f"The {name} provides the user-facing interface for the application, handling user interactions and presentation logic."
    elif component_type == 'service':
        if 'api' in name.lower() or 'gateway' in name.lower():
            return f"The {name} routes and manages API requests, providing a unified entry point for client applications."
        elif 'auth' in name.lower() or 'security' in name.lower():
            return f"The {name} handles authentication, authorization, and security-related functionality."
        else:
            return f"The {name} implements core business logic and processing functionality."
    elif component_type == 'database':
        return f"The {name} provides persistent data storage and retrieval capabilities."
    elif component_type == 'external':
        return f"The {name} represents an external system or third-party service that the application integrates with."
    else:
        return f"The {name} is a key component in the system architecture."

    
    def _identify_component_connections(self, components):
        """Identify logical connections between components"""
        connections = []
        
        # Sort components in a logical processing order
        # User components, then services, then databases, then external
        type_order = {'user': 1, 'service': 2, 'database': 3, 'external': 4}
        sorted_components = sorted(components, key=lambda c: type_order.get(c['type'], 99))
        
        # Create connections based on the logical flow
        for i in range(len(sorted_components)):
            if i < len(sorted_components) - 1:
                # Connect in sequence
                source = sorted_components[i]
                target = sorted_components[i+1]
                
                # Skip connection if moving backward in the type order
                if type_order.get(source['type'], 99) > type_order.get(target['type'], 99):
                    continue
                
                # Generate appropriate connection description
                description = self._generate_connection_description(source, target)
                
                connections.append({
                    'from': source['name'],
                    'to': target['name'],
                    'type': 'default',
                    'description': description
                })
        
        # Add special connections
        for i, source in enumerate(sorted_components):
            for j, target in enumerate(sorted_components):
                # Skip self-connections and existing connections
                if i == j or any(c['from'] == source['name'] and c['to'] == target['name'] for c in connections):
                    continue
                
                # Connect UI to API/Services
                if source['type'] == 'user' and target['type'] == 'service' and 'api' in target['name'].lower():
                    connections.append({
                        'from': source['name'],
                        'to': target['name'],
                        'type': 'default',
                        'description': 'API Requests'
                    })
                
                # Connect Services to Databases
                elif source['type'] == 'service' and target['type'] == 'database':
                    connections.append({
                        'from': source['name'],
                        'to': target['name'],
                        'type': 'default',
                        'description': 'Data Operations'
                    })
                
                # Connect Auth services specifically
                elif 'auth' in source['name'].lower() and target['type'] != 'database':
                    connections.append({
                        'from': source['name'],
                        'to': target['name'],
                        'type': 'default',
                        'description': 'Authentication/Authorization'
                    })
        
        return connections
    
    def _generate_connection_description(self, source, target):
        """Generate a description for a connection between components"""
        source_type = source['type']
        target_type = target['type']
        
        if source_type == 'user' and target_type == 'service':
            return 'User Requests'
        elif source_type == 'service' and target_type == 'service':
            if 'api' in source['name'].lower() or 'gateway' in source['name'].lower():
                return 'API Routing'
            else:
                return 'Service Calls'
        elif source_type == 'service' and target_type == 'database':
            return 'Data Operations'
        elif source_type == 'service' and target_type == 'external':
            return 'External Integration'
        else:
            return 'Communication'
    
    def _extract_data_entities(self, description, data_model_text):
        """Extract data entities from description and data model text"""
        # This would be enhanced with NLP in a real implementation
        # For now, we'll do basic entity detection
        
        entities = []
        
        # Common entity patterns in web applications
        common_entities = [
            {
                'name': 'User',
                'attributes': [
                    {'name': 'id', 'type': 'UUID', 'key': True},
                    {'name': 'username', 'type': 'String'},
                    {'name': 'email', 'type': 'String'},
                    {'name': 'password', 'type': 'String'},
                    {'name': 'createdAt', 'type': 'Timestamp'}
                ]
            },
            {
                'name': 'Profile',
                'attributes': [
                    {'name': 'id', 'type': 'UUID', 'key': True},
                    {'name': 'userId', 'type': 'UUID'},
                    {'name': 'firstName', 'type': 'String'},
                    {'name': 'lastName', 'type': 'String'},
                    {'name': 'bio', 'type': 'Text'},
                    {'name': 'avatar', 'type': 'String'}
                ]
            }
        ]
        
        # Add common entities by default
        entities.extend(common_entities)
        
        # Look for entity mentions in description
        combined_text = f"{description} {data_model_text}".lower()
        
        # Define entity patterns to look for
        entity_patterns = [
            r'\b(customer|account|order|product|item|transaction|payment|invoice|subscription|content|article|post|comment|review)\b'
        ]
        
        # Extract unique entity matches
        entity_matches = set()
        for pattern in entity_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            entity_matches.update(matches)
        
        # Generate entities for each match
        for match in entity_matches:
            entity_name = match.capitalize()
            
            # Skip if we already have this entity
            if any(e['name'].lower() == entity_name.lower() for e in entities):
                continue
            
            # Generate attributes based on entity type
            attributes = [
                {'name': 'id', 'type': 'UUID', 'key': True},
                {'name': 'name', 'type': 'String'},
                {'name': 'description', 'type': 'Text'},
                {'name': 'createdAt', 'type': 'Timestamp'},
                {'name': 'updatedAt', 'type': 'Timestamp'}
            ]
            
            # Add entity-specific attributes
            if match.lower() == 'order':
                attributes.extend([
                    {'name': 'customerId', 'type': 'UUID'},
                    {'name': 'orderDate', 'type': 'Date'},
                    {'name': 'status', 'type': 'String'},
                    {'name': 'totalAmount', 'type': 'Decimal'}
                ])
            elif match.lower() == 'product':
                attributes.extend([
                    {'name': 'price', 'type': 'Decimal'},
                    {'name': 'category', 'type': 'String'},
                    {'name': 'inStock', 'type': 'Boolean'}
                ])
            elif match.lower() in ['post', 'article', 'content']:
                attributes.extend([
                    {'name': 'title', 'type': 'String'},
                    {'name': 'body', 'type': 'Text'},
                    {'name': 'authorId', 'type': 'UUID'},
                    {'name': 'publishedAt', 'type': 'Timestamp'}
                ])
            
            entities.append({
                'name': entity_name,
                'attributes': attributes
            })
        
        return entities
    
    def _identify_entity_relationships(self, entities):
        """Identify relationships between data entities"""
        relationships = []
        
        # Generate relationships based on entity names and attributes
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities):
                if i == j:
                    continue
                
                entity1_name = entity1['name'].lower()
                entity2_name = entity2['name'].lower()
                
                # Check for foreign key relationships in attributes
                fk_relationship = False
                for attr in entity1['attributes']:
                    attr_name = attr.get('name', '').lower()
                    if attr_name == entity2_name + 'id' or attr_name == entity2_name + '_id':
                        # Entity1 has a foreign key to Entity2
                        relationships.append({
                            'from': entity1['name'],
                            'to': entity2['name'],
                            'type': 'N:1'
                        })
                        fk_relationship = True
                        break
                
                if fk_relationship:
                    continue
                
                for attr in entity2['attributes']:
                    attr_name = attr.get('name', '').lower()
                    if attr_name == entity1_name + 'id' or attr_name == entity1_name + '_id':
                        # Entity2 has a foreign key to Entity1
                        relationships.append({
                            'from': entity2['name'],
                            'to': entity1['name'],
                            'type': 'N:1'
                        })
                        fk_relationship = True
                        break
                
                if fk_relationship:
                    continue
                
                # If no FK relationship found, look for common patterns
                # User -> Profile
                if entity1_name == 'user' and entity2_name == 'profile':
                    relationships.append({
                        'from': entity1['name'],
                        'to': entity2['name'],
                        'type': '1:1'
                    })
                # User -> Post/Content
                elif entity1_name == 'user' and entity2_name in ['post', 'content', 'article']:
                    relationships.append({
                        'from': entity1['name'],
                        'to': entity2['name'],
                        'type': '1:N'
                    })
                # Order -> Product (many-to-many via OrderItem)
                elif (entity1_name == 'order' and entity2_name == 'product') or (entity1_name == 'product' and entity2_name == 'order'):
                    relationships.append({
                        'from': 'Order',
                        'to': 'Product',
                        'type': 'N:M'
                    })
        
        return relationships
    
    def _generate_mermaid_architecture_diagram(self, components, connections, app_name):
        """Generate a mermaid diagram for architecture"""
        mermaid_code = f"graph TD\n    title[{app_name} Architecture]\n    \n"
        
        # Add components with appropriate shapes
        for i, component in enumerate(components):
            component_id = f"comp{i}"
            component_name = component['name']
            component_type = component['type']
            
            # Set shape based on component type
            if component_type == 'database':
                mermaid_code += f"    {component_id}[('{component_name}')]\n"
            elif component_type == 'external':
                mermaid_code += f"    {component_id}>'{component_name}']\n"
            elif component_type == 'user':
                mermaid_code += f"    {component_id}[/'{component_name}'/]\n"
            else:
                mermaid_code += f"    {component_id}['{component_name}']\n"
        
        # Add connections
        for conn in connections:
            from_name = conn['from']
            to_name = conn['to']
            description = conn.get('description', '')
            
            # Find component IDs
            from_id = None
            to_id = None
            
            for i, component in enumerate(components):
                if component['name'] == from_name:
                    from_id = f"comp{i}"
                if component['name'] == to_name:
                    to_id = f"comp{i}"
            
            if from_id and to_id:
                mermaid_code += f"    {from_id} -- {description} --> {to_id}\n"
        
        # Add styling
        mermaid_code += "    \n    style title fill:#f9f,stroke:#333,stroke-width:2px\n"
        
        # Return as a diagram
        return self.diagram_generator.generate_mermaid_diagram(
            mermaid_code,
            f"{app_name} Architecture"
        )
    
    def _generate_architecture_insights(self, hldd_analysis):
        """Generate insights based on HLDD analysis"""
        insights = []
        
        # Check overall score
        overall_score = hldd_analysis.get('overall_score', 0)
        if overall_score < 0.5:
            insights.append({
                'type': 'warning',
                'title': 'Low Overall Architecture Quality',
                'description': 'The architecture document lacks sufficient detail in multiple areas.',
                'recommendation': 'Consider a comprehensive architecture review and documentation update.'
            })
        elif overall_score < 0.7:
            insights.append({
                'type': 'info',
                'title': 'Room for Architecture Improvement',
                'description': 'The architecture documentation has some gaps that should be addressed.',
                'recommendation': 'Focus on improving the areas with the lowest scores.'
            })
        else:
            insights.append({
                'type': 'success',
                'title': 'Solid Architecture Foundation',
                'description': 'The architecture documentation provides good coverage of key areas.',
                'recommendation': 'Continue to maintain and update as the system evolves.'
            })
        
        # Check specific criteria scores
        scores = hldd_analysis.get('scores', {})
        for criterion, data in scores.items():
            score = data.get('score', 0)
            
            if score < 0.4:
                severity = 'warning'
                recommendation = f"The {criterion} aspects need significant improvement. Consider adding more details about {criterion} considerations."
            elif score < 0.7:
                severity = 'info'
                recommendation = f"The {criterion} aspects could be enhanced with more specific details."
            else:
                severity = 'success'
                recommendation = f"The {criterion} aspects are well-documented. Continue to refine as needed."
            
            insights.append({
                'type': severity,
                'title': f"{criterion.capitalize()} Score: {score:.2f}",
                'description': f"Analysis of {criterion} documentation and considerations.",
                'recommendation': recommendation
            })
        
        # Check for missing components
        missing_components = hldd_analysis.get('missing_components', [])
        if missing_components:
            components_list = ', '.join(missing_components)
            insights.append({
                'type': 'warning',
                'title': 'Missing Architecture Components',
                'description': f"The following components are not adequately covered: {components_list}",
                'recommendation': 'Add these missing components to the architecture documentation.'
            })
        
        return insights
    
    def _merge_dict(self, dict1, dict2):
        """Recursively merge two dictionaries, with dict2 values taking precedence"""
        merged = dict1.copy()
        
        for key, value in dict2.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_dict(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _extract_technologies_from_text(self, text):
        """Extract technology mentions from text"""
        # This would be enhanced with NLP in a real implementation
        # Common technology keywords to look for
        tech_keywords = [
            'react', 'angular', 'vue', 'node', 'express', 'spring', 'django', 'flask',
            'java', 'python', 'javascript', 'typescript', 'c#', 'go', 'ruby',
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'neo4j',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform', 'ansible',
            'kafka', 'rabbitmq', 'graphql', 'rest', 'oauth', 'jwt'
        ]
        
        text_lower = text.lower()
        found_technologies = []
        
        for tech in tech_keywords:
            if re.search(r'\b' + re.escape(tech) + r'\b', text_lower):
                found_technologies.append(tech.capitalize())
        
        return found_technologies

class ArchitectureAdvisor:
    """Provide conversational guidance for architecture decisions"""
    
    def __init__(self, architecture_agent):
        self.architecture_agent = architecture_agent
        self.conversation_history = {}
    
    def start_conversation(self, user_id):
        """Start a new architecture guidance conversation"""
        conversation_id = str(uuid.uuid4())
        self.conversation_history[conversation_id] = []
        return conversation_id
    
    def get_guidance(self, conversation_id, question):
        """Get architecture guidance based on a question"""
        if conversation_id not in self.conversation_history:
            return {"error": "Conversation not found"}
        
        # Add question to history
        self.conversation_history[conversation_id].append({
            "role": "user",
            "message": question
        })
        
        # Generate response based on question type
        if "database" in question.lower():
            response = self._generate_database_guidance(question)
        elif "scalability" in question.lower():
            response = self._generate_scalability_guidance(question)
        elif "security" in question.lower():
            response = self._generate_security_guidance(question)
        else:
            response = self._generate_general_guidance(question)
        
        # Add response to history
        self.conversation_history[conversation_id].append({
            "role": "assistant",
            "message": response
        })
        
        return {
            "response": response,
            "conversation_id": conversation_id
        }

# In architecture_agent.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class ArchitecturePatternLearner:
    """Learn architecture patterns from existing documents"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.model = KMeans(n_clusters=5)
        self.trained = False
    
    def train(self, documents):
        """Train on a corpus of architecture documents"""
        if len(documents) < 5:
            return False
            
        corpus = [doc.get('content', '') for doc in documents]
        features = self.vectorizer.fit_transform(corpus)
        self.model.fit(features)
        self.trained = True
        return True
    
    def suggest_patterns(self, document_text):
        """Suggest architecture patterns based on document text"""
        if not self.trained:
            return []
            
        # Transform the document using the same vectorizer
        features = self.vectorizer.transform([document_text])
        
        # Get the cluster
        cluster = self.model.predict(features)[0]
        
        # Return patterns associated with this cluster
        return self.get_patterns_for_cluster(cluster)

def get_architecture_agent(upload_folder, enable_background_tasks=True):
    """Factory function to get an instance of the Architecture Agent"""
    return ArchitectureAgent(upload_folder, enable_background_tasks)