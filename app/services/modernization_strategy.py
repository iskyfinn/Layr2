import re
from collections import defaultdict
from flask import jsonify, current_app
from app.models.application import Application
from app.services.hldd_analyzer import HLDDAnalyzer
import os
from datetime import datetime


class ModernizationStrategy:
    def __init__(self):
        # Define modernization approaches
        self.strategies = {
            'rehost': {
                'name': 'Rehost (Lift and Shift)',
                'description': 'Moving applications to the cloud without making significant changes',
                'effort': 'Low',
                'business_impact': 'Low',
                'technical_debt': 'High',
                'best_for': ['legacy applications', 'stable workloads', 'time constraints', 'cost reduction'],
                'steps': [
                    'Identify applications for migration',
                    'Assess infrastructure requirements',
                    'Create migration plan',
                    'Set up cloud environment',
                    'Migrate application and data',
                    'Test and validate',
                    'Cut over to cloud'
                ]
            },
            'replatform': {
                'name': 'Replatform (Lift and Reshape)',
                'description': 'Making some cloud optimizations without changing the core architecture',
                'effort': 'Medium',
                'business_impact': 'Medium',
                'technical_debt': 'Medium',
                'best_for': ['database migrations', 'containerization', 'managed services', 'scalability improvements'],
                'steps': [
                    'Identify applications for replatforming',
                    'Analyze application components',
                    'Determine platform changes',
                    'Adapt application for new platform',
                    'Migrate to cloud platform',
                    'Optimize for cloud features',
                    'Test and validate'
                ]
            },
            'refactor': {
                'name': 'Refactor / Re-architect',
                'description': 'Significantly modifying the application to better leverage cloud capabilities',
                'effort': 'High',
                'business_impact': 'High',
                'technical_debt': 'Low',
                'best_for': ['monolithic applications', 'high performance needs', 'scalability requirements', 'agility improvements'],
                'steps': [
                    'Analyze application architecture',
                    'Design new cloud-native architecture',
                    'Break monolith into services',
                    'Implement new architecture',
                    'Migrate data',
                    'Set up CI/CD pipeline',
                    'Implement cloud-native features',
                    'Test and validate'
                ]
            },
            'rebuild': {
                'name': 'Rebuild',
                'description': 'Rebuilding the application from scratch as cloud-native',
                'effort': 'Very High',
                'business_impact': 'Very High',
                'technical_debt': 'Very Low',
                'best_for': ['outdated technology', 'significant business changes', 'competitive pressure', 'technical limitations'],
                'steps': [
                    'Gather business requirements',
                    'Design cloud-native architecture',
                    'Implement with modern technology stack',
                    'Migrate data from old system',
                    'Set up DevOps practices',
                    'Test and validate',
                    'Gradually replace old system'
                ]
            },
            'replace': {
                'name': 'Replace (Repurchase)',
                'description': 'Abandoning existing application in favor of commercial SaaS solutions',
                'effort': 'Medium',
                'business_impact': 'High',
                'technical_debt': 'Low',
                'best_for': ['commodity functionality', 'non-core business functions', 'standardized processes', 'resource constraints'],
                'steps': [
                    'Identify replacement SaaS options',
                    'Evaluate and select vendor',
                    'Plan data migration',
                    'Configure SaaS solution',
                    'Integrate with other systems',
                    'Migrate user data',
                    'Train users on new system'
                ]
            },
            'retain': {
                'name': 'Retain (Revisit)',
                'description': 'Keeping applications on-premises with no immediate changes',
                'effort': 'Very Low',
                'business_impact': 'Low',
                'technical_debt': 'High',
                'best_for': ['recent investments', 'compliance requirements', 'low change benefit', 'pending retirement'],
                'steps': [
                    'Document reasons for retention',
                    'Schedule regular reassessment',
                    'Optimize current infrastructure',
                    'Plan for eventual migration',
                    'Monitor application performance',
                    'Maintain security updates',
                    'Document technical debt'
                ]
            }
        }
        
        # Define factors that influence strategy selection
        self.factors = {
            'business_criticality': ['critical', 'important', 'supporting', 'non-critical'],
            'technical_complexity': ['simple', 'moderate', 'complex', 'very complex'],
            'age': ['new', 'recent', 'mature', 'legacy'],
            'change_frequency': ['frequent', 'regular', 'occasional', 'rare'],
            'cloud_readiness': ['ready', 'adaptable', 'challenging', 'not ready'],
            'security_compliance': ['standard', 'sensitive', 'regulated', 'highly regulated']
        }

    def recommend_strategy(self, app_info, hldd_analysis, **kwargs):
        """
        Recommend modernization strategies tailored to the app's current architecture.

        Args:
            app_info (dict): Info about the application (description, tech_stack, age, business_value)
            hldd_analysis (dict): Analysis result from HLDDAnalyzer

        Returns:
            dict: Structured modernization strategy recommendations
        """
        description = app_info.get('description', '').lower()
        tech_stack = app_info.get('tech_stack', '').lower()
        business_value = app_info.get('business_value', '').lower()
        age = app_info.get('age', 'new')
        hldd_score = hldd_analysis.get('overall_score', 0.5)

        strategies = []

        # 🟩 Strategy 1: Cloud Migration
        if 'on-prem' in description or age == 'legacy' or 'bare metal' in tech_stack:
            cloud_score = 80 if hldd_score < 0.7 else 60
            strategies.append({
                'strategy': {
                    'name': 'Cloud Migration',
                    'description': 'Migrate the application to a cloud platform (e.g., AWS, Azure, GCP) for improved scalability, resilience, and reduced infrastructure overhead.'
                },
                'justification': 'App is either legacy or tied to on-premise infrastructure. Cloud can increase agility and reduce ops cost.',
                'benefits': ['Elastic scaling', 'Managed services', 'Global access'],
                'considerations': ['Data security', 'Migration complexity', 'Training'],
                'score': cloud_score
            })

        # 🟩 Strategy 2: Microservices Transformation
        if 'monolith' in description or 'spring boot' in tech_stack or 'tight coupling' in hldd_analysis.get('missing_components', []):
            microservices_score = 75 if hldd_score < 0.65 else 60
            strategies.append({
                'strategy': {
                    'name': 'Microservices Transformation',
                    'description': 'Decompose the app into modular microservices to improve scalability, fault isolation, and development velocity.'
                },
                'justification': 'Monolithic architecture or lack of separation of concerns makes scaling and agility harder.',
                'benefits': ['Independent deployments', 'Technology polyglot', 'Team autonomy'],
                'considerations': ['Increased complexity', 'Orchestration', 'Distributed tracing'],
                'score': microservices_score
            })

        # 🟩 Strategy 3: Containerization
        if any(x in tech_stack for x in ['python', 'node', 'java']) and 'docker' not in tech_stack:
            container_score = 90 if hldd_score >= 0.6 else 70
            strategies.append({
                'strategy': {
                    'name': 'Containerization',
                    'description': 'Package the application and its dependencies into containers (e.g., Docker) to ensure environment consistency and scalable deployment.'
                },
                'justification': 'Containerization provides consistent environments and is a stepping stone for cloud-native and CI/CD.',
                'benefits': ['Portability', 'Isolation', 'Faster deployments'],
                'considerations': ['Learning curve for orchestration', 'Security hardening'],
                'score': container_score
            })

        # 🟩 Strategy 4: API-First Re-Architecture
        if 'integration' in business_value or 'partner' in description:
            api_score = 80
            strategies.append({
                'strategy': {
                    'name': 'API-First Re-Architecture',
                    'description': 'Design system boundaries around APIs for better decoupling, external partner integration, and reusability.'
                },
                'justification': 'APIs improve developer experience, third-party integrations, and scalability.',
                'benefits': ['Modularity', 'Third-party integrations', 'Developer enablement'],
                'considerations': ['Versioning', 'Security (auth, rate limits)', 'Lifecycle management'],
                'score': api_score
            })

        # 🟩 Strategy 5: Event-Driven Rewiring
        if 'latency' in description or 'real-time' in business_value:
            eda_score = 70
            strategies.append({
                'strategy': {
                    'name': 'Event-Driven Architecture (EDA)',
                    'description': 'Enable real-time and asynchronous communication using events and message queues for decoupling and responsiveness.'
                },
                'justification': 'Ideal for use cases like streaming, decoupling, or scaling specific domains independently.',
                'benefits': ['Loose coupling', 'Scalability', 'Real-time processing'],
                'considerations': ['Debugging events', 'Idempotency', 'Tooling (Kafka, SNS/SQS)'],
                'score': eda_score
            })

        strategies.sort(key=lambda x: x['score'], reverse=True)
        
        # Add specialized detection for field service applications
        is_field_service_app = any(term in description.lower() for term in ['electrician', 'field service', 'technician', 'maintenance', 'repair', 'installation'])
        
        # If this is a field service app but no strategies were matched yet, add specialized recommendations
        if is_field_service_app:
            # Mobile-first strategy
            mobile_score = 95
            strategies.append({
                'strategy': {
                    'name': 'Mobile-First Field Service Application',
                    'description': 'Develop a mobile-optimized application specifically designed for field electricians with offline capabilities, location services, and efficient data capture.'
                },
                'justification': 'Field electricians spend most of their time at customer locations and need reliable mobile tools that work with or without internet connectivity.',
                'benefits': [
                    'Offline work order management', 
                    'GPS and mapping integration', 
                    'Photo/document capture',
                    'Digital signature collection',
                    'Reduced paperwork',
                    'Real-time updates when connected'
                ],
                'considerations': [
                    'iOS/Android compatibility', 
                    'Reliable local data storage', 
                    'Sync conflict resolution',
                    'Battery optimization',
                    'Integration with existing systems'
                ],
                'score': mobile_score
            })
            
            # Cloud backend strategy
            cloud_score = 88
            strategies.append({
                'strategy': {
                    'name': 'Cloud-Backed Service Platform',
                    'description': 'Build a scalable cloud backend that supports the mobile application while providing scheduling, dispatching, customer management, and reporting capabilities.'
                },
                'justification': 'A robust cloud platform allows business operations to centrally manage field work while providing real-time visibility and integration capabilities.',
                'benefits': [
                    'Centralized scheduling and dispatching',
                    'Customer history and equipment tracking',
                    'Inventory management',
                    'Real-time business insights',
                    'Integration with accounting/ERP systems',
                    'Automated billing workflows'
                ],
                'considerations': [
                    'Data security and compliance',
                    'API design for mobile/web clients',
                    'Notification systems',
                    'Scalability for busy periods',
                    'Backup and disaster recovery'
                ],
                'score': cloud_score
            })
            
            # Customer portal strategy
            portal_score = 78
            strategies.append({
                'strategy': {
                    'name': 'Customer Self-Service Portal',
                    'description': 'Create a responsive web portal that allows customers to request service, view appointment status, access historical service records, and make payments online.'
                },
                'justification': 'Modern customers expect digital self-service options. A customer portal improves satisfaction while reducing administrative overhead for scheduling and payment processing.',
                'benefits': [
                    'Customer satisfaction improvement', 
                    '24/7 service request capability', 
                    'Automated appointment reminders',
                    'Online payment processing',
                    'Reduced phone call volume',
                    'Digital service history access'
                ],
                'considerations': [
                    'User experience design', 
                    'Security of customer data', 
                    'Integration with field service system',
                    'Payment processor integration',
                    'Mobile responsive design'
                ],
                'score': portal_score
            })
            
            # IoT integration strategy
            iot_score = 72
            strategies.append({
                'strategy': {
                    'name': 'Smart Home Integration Platform',
                    'description': 'Develop capabilities to integrate with and service smart home electrical systems, providing diagnostics, monitoring, and advanced service capabilities.'
                },
                'justification': 'As homes become increasingly connected, electricians need tools to diagnose, connect with, and service smart electrical systems and IoT devices.',
                'benefits': [
                    'Remote diagnostics capabilities', 
                    'Preventative maintenance opportunities', 
                    'Expanded service offerings',
                    'Competitive differentiation',
                    'Data-driven service recommendations',
                    'Higher value customer relationships'
                ],
                'considerations': [
                    'IoT device compatibility', 
                    'Security protocols', 
                    'Staff training requirements',
                    'Data privacy concerns',
                    'Ongoing platform updates'
                ],
                'score': iot_score
            })
            
            # AI-powered strategy
            ai_score = 65
            strategies.append({
                'strategy': {
                    'name': 'AI-Enhanced Service Optimization',
                    'description': 'Implement AI capabilities for intelligent scheduling, predictive maintenance, job estimation, and technician knowledge support.'
                },
                'justification': 'AI can significantly improve operational efficiency by optimizing routes, predicting service needs, and providing intelligent assistance to technicians in the field.',
                'benefits': [
                    'Intelligent scheduling and routing', 
                    'Predictive maintenance capabilities', 
                    'Automated job estimation',
                    'Technician knowledge assistance',
                    'Improved first-time fix rates',
                    'Resource optimization'
                ],
                'considerations': [
                    'Data collection for AI training', 
                    'Integration complexity', 
                    'Ongoing AI model maintenance',
                    'User acceptance and training',
                    'Ethical AI implementation'
                ],
                'score': ai_score
            })

        # Add a default recommendation if no strategies were matched at all
        if not strategies:
            default_score = 75
            strategies.append({
                'strategy': {
                    'name': 'Cloud-Native Application',
                    'description': 'Build the electrician app as a cloud-native application with modern frameworks and responsive design.'
                },
                'justification': 'A cloud-native approach provides scalability, flexibility, and modern user experience for field service applications.',
                'benefits': ['Elastic scaling', 'Mobile-friendly interfaces', 'Offline capabilities'],
                'considerations': ['Cloud infrastructure setup', 'Development expertise', 'Cross-device testing'],
                'score': default_score
            })
            
            # Add a second strategy to ensure multiple strategies are present
            strategies.append({
                'strategy': {
                    'name': 'Mobile-First Development',
                    'description': 'Focus on creating a robust mobile application first, optimized for field electricians.'
                },
                'justification': 'Electricians primarily work in the field and need mobile-optimized tools that work reliably.',
                'benefits': ['Field-ready tools', 'Offline functionality', 'Location services'],
                'considerations': ['iOS/Android compatibility', 'Battery optimization', 'Rugged device support'],
                'score': default_score - 5
            })

        # Simplify structure to match template expectations
        simplified_strategies = []
        for strategy in strategies:
            simplified_strategies.append({
                'name': strategy['strategy']['name'],
                'description': strategy['strategy']['description'],
                'score': strategy['score'],
                'justification': strategy['justification'],
                'benefits': strategy['benefits'],
                'considerations': strategy['considerations']
            })

        return {
            'recommended_strategies': simplified_strategies,
            'generated_at': datetime.utcnow().isoformat(),
            'hldd_score': hldd_score,
            'inputs': {
                'app_info': app_info,
                'analysis_summary': hldd_analysis.get('summary', 'N/A')
            }
        }
    
    def _analyze_factors(self, text, hldd_analysis=None):
        """Analyze application factors from text description"""
        factors = {}
        
        # Business criticality
        if any(term in text for term in ['mission critical', 'core business', 'revenue']):
            factors['business_criticality'] = 'critical'
        elif any(term in text for term in ['important', 'key process', 'significant']):
            factors['business_criticality'] = 'important'
        elif any(term in text for term in ['supporting', 'internal', 'operational']):
            factors['business_criticality'] = 'supporting'
        else:
            factors['business_criticality'] = 'non-critical'
        
        # Technical complexity
        if any(term in text for term in ['monolithic', 'legacy', 'complex', 'tightly coupled']):
            factors['technical_complexity'] = 'complex'
        elif any(term in text for term in ['microservices', 'modern', 'cloud native']):
            factors['technical_complexity'] = 'simple'
        else:
            factors['technical_complexity'] = 'moderate'
        
        # Age
        if any(term in text for term in ['legacy', 'old', 'outdated', 'mainframe']):
            factors['age'] = 'legacy'
        elif any(term in text for term in ['new', 'recent', 'modern']):
            factors['age'] = 'new'
        else:
            factors['age'] = 'mature'
        
        # Change frequency
        if any(term in text for term in ['agile', 'frequent changes', 'continuous']):
            factors['change_frequency'] = 'frequent'
        elif any(term in text for term in ['stable', 'unchanging', 'fixed']):
            factors['change_frequency'] = 'rare'
        else:
            factors['change_frequency'] = 'occasional'
        
        # Cloud readiness
        if any(term in text for term in ['cloud native', 'containerized', 'cloud ready']):
            factors['cloud_readiness'] = 'ready'
        elif any(term in text for term in ['on-premise', 'legacy', 'mainframe']):
            factors['cloud_readiness'] = 'not ready'
        else:
            factors['cloud_readiness'] = 'adaptable'
        
        # Security/Compliance
        if any(term in text for term in ['hipaa', 'pci', 'gdpr', 'regulated', 'compliance']):
            factors['security_compliance'] = 'regulated'
        elif any(term in text for term in ['sensitive', 'secure', 'confidential']):
            factors['security_compliance'] = 'sensitive'
        else:
            factors['security_compliance'] = 'standard'
        
        # Use HLDD analysis if available
        if hldd_analysis:
            # Technical debt assessment from HLDD
            scores = hldd_analysis.get('scores', {})
            if scores:
                avg_score = sum(data.get('score', 0) for data in scores.values()) / len(scores)
                if avg_score < 0.4:
                    factors['technical_debt'] = 'high'
                elif avg_score < 0.7:
                    factors['technical_debt'] = 'medium'
                else:
                    factors['technical_debt'] = 'low'
        
        return factors
    
    def _score_strategies(self, factors, text):
        """Score modernization strategies based on application factors"""
        strategy_scores = {}
        
        for strategy_id, strategy_data in self.strategies.items():
            score = 0
            reasoning = []
            
            # Score based on business criticality
            if factors.get('business_criticality') == 'critical':
                # Critical systems may warrant more investment in refactoring
                if strategy_id in ['refactor', 'rebuild']:
                    score += 0.8
                    reasoning.append("Business-critical application justifies significant modernization investment")
                elif strategy_id == 'retain':
                    score += 0.2
                    reasoning.append("Retention is risky for business-critical applications")
            elif factors.get('business_criticality') == 'non-critical':
                # Non-critical systems may be candidates for replacement or minimal effort
                if strategy_id in ['replace', 'rehost', 'retain']:
                    score += 0.7
                    reasoning.append("Non-critical application can be handled with lower-effort approaches")
            
            # Score based on technical complexity
            if factors.get('technical_complexity') in ['complex', 'very complex']:
                if strategy_id == 'rehost':
                    score += 0.7
                    reasoning.append("Complex applications often benefit from rehosting first to reduce immediate risk")
                elif strategy_id == 'rebuild':
                    score += 0.5
                    reasoning.append("Rebuilding can address complex technical debt, but carries execution risk")
            elif factors.get('technical_complexity') == 'simple':
                if strategy_id in ['refactor', 'replatform']:
                    score += 0.8
                    reasoning.append("Simpler applications are good candidates for refactoring or replatforming")
            
            # Score based on age
            if factors.get('age') == 'legacy':
                if strategy_id in ['rebuild', 'replace']:
                    score += 0.8
                    reasoning.append("Legacy applications often benefit most from rebuild or replacement")
                elif strategy_id == 'rehost':
                    score += 0.6
                    reasoning.append("Rehosting can be a first step for legacy applications")
            elif factors.get('age') == 'new':
                if strategy_id in ['refactor', 'replatform']:
                    score += 0.9
                    reasoning.append("Newer applications are well-suited for refactoring or replatforming")
                elif strategy_id in ['rebuild', 'replace']:
                    score += 0.3
                    reasoning.append("Rebuilding or replacing newer applications rarely provides enough ROI")
            
            # Score based on cloud readiness
            if factors.get('cloud_readiness') == 'ready':
                if strategy_id in ['replatform', 'refactor']:
                    score += 0.9
                    reasoning.append("Cloud-ready applications can quickly benefit from replatforming or refactoring")
            elif factors.get('cloud_readiness') == 'not ready':
                if strategy_id in ['rehost', 'rebuild']:
                    score += 0.7
                    reasoning.append("Cloud-unready applications need either simple rehosting or complete rebuild")
            
            # Score based on security/compliance
            if factors.get('security_compliance') in ['regulated', 'highly regulated']:
                if strategy_id in ['rehost', 'retain']:
                    score += 0.7
                    reasoning.append("Regulated applications may benefit from cautious approach like rehosting or retention")
                elif strategy_id == 'replace':
                    score += 0.4
                    reasoning.append("Replacement with SaaS may introduce compliance challenges")
            
            # Check for specific terms in text that might favor certain strategies
            text_lower = text.lower()
            
            if any(term in text_lower for term in ['cost reduction', 'quick win', 'immediate benefits']):
                if strategy_id in ['rehost', 'replatform']:
                    score += 0.5
                    reasoning.append("Emphasis on quick wins favors rehosting or replatforming")
            
            if any(term in text_lower for term in ['scalability', 'performance', 'modernize']):
                if strategy_id in ['refactor', 'rebuild']:
                    score += 0.5
                    reasoning.append("Emphasis on performance and scalability favors refactoring or rebuilding")
            
            if any(term in text_lower for term in ['standard functionality', 'commodity', 'non-differentiating']):
                if strategy_id == 'replace':
                    score += 0.7
                    reasoning.append("Commodity functionality is well-suited for replacement with SaaS")
            
            # Normalize score (0-1 range)
            normalized_score = min(1.0, score / 3.0)  # Assuming maximum raw score around 3.0
            
            strategy_scores[strategy_id] = {
                'overall_score': round(normalized_score, 2),
                'reasoning': reasoning
            }
        
        return strategy_scores

# Factory function to get a strategy instance
def get_modernization_strategy():
    """Factory function to get an instance of the Modernization Strategy recommender"""
    return ModernizationStrategy()

# Create an instance that can be imported by other modules
modernization_strategy = get_modernization_strategy()