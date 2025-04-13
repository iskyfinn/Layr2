# app/services/hldd_generator.py
import os
import uuid
import traceback
from datetime import datetime
from flask import current_app
from typing import Dict, Any
import logging

class HLDDGenerator:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        logging.info(f"HLDDGenerator initialized with folder: {upload_folder}")

    
# In app/services/hldd_generator.py


def generate_hldd_recommendation(user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate HLDD recommendations based on user inputs
    
    Args:
        user_inputs (dict): User-provided application information
    
    Returns:
        dict: Comprehensive HLDD recommendation
    """
    # Use case templates
    use_case_templates = {
        'web_application': {
            'description': 'Web-based application serving users through a browser interface',
            'typical_functions': [
                'User registration and authentication',
                'Content management',
                'Data visualization',
                'User interaction and engagement'
            ],
            'recommended_technologies': {
                'frontend': ['React', 'Vue.js', 'Angular'],
                'backend': ['Python (Flask/Django)', 'Node.js (Express)', 'Java (Spring)'],
                'database': ['PostgreSQL', 'MongoDB', 'MySQL']
            }
        },
        'mobile_application': {
            'description': 'Mobile app for iOS and/or Android platforms',
            'typical_functions': [
                'User authentication',
                'Offline functionality',
                'Push notifications',
                'Device integration'
            ],
            'recommended_technologies': {
                'mobile_framework': ['React Native', 'Flutter', 'Native (Swift/Kotlin)'],
                'backend': ['Node.js', 'Python (Django)', 'Firebase'],
                'database': ['Realm', 'SQLite', 'Firebase Firestore']
            }
        },
        'enterprise_software': {
            'description': 'Complex software solution for business operations',
            'typical_functions': [
                'Multi-user access control',
                'Advanced reporting',
                'Integration with existing systems',
                'Complex workflow management'
            ],
            'recommended_technologies': {
                'frontend': ['React', 'Angular', 'Vue.js'],
                'backend': ['Java (Spring)', 'C# (.NET)', 'Python (Django)'],
                'database': ['Oracle', 'SQL Server', 'PostgreSQL'],
                'integration': ['Microservices', 'Enterprise Service Bus']
            }
        }
    }
    
    # Security templates
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

    # Basic structure combining both use case + security (extend as needed)
    recommendation = {
        'use_case_template': use_case_templates.get(user_inputs.get('use_case', ''), {}),
        'security_template': security_templates.get(user_inputs.get('sensitivity', ''), {}),
        'basicInfo': {
            'name': user_inputs.get('name', 'Untitled Application'),
            'description': user_inputs.get('description', '')
        }
    }

    return recommendation
    
    def _identify_use_case(description: str) -> str:
        """
        Identify the use case based on description keywords
        """
        description = description.lower()
        
        # Define keyword mappings
        use_case_keywords = {
            'web_application': ['web', 'online', 'browser', 'saas', 'platform'],
            'mobile_application': ['mobile', 'app', 'smartphone', 'ios', 'android'],
            'enterprise_software': ['enterprise', 'business', 'corporate', 'workflow', 'erp', 'crm']
        }
        
        # Check for keywords
        for use_case, keywords in use_case_keywords.items():
            if any(keyword in description for keyword in keywords):
                return use_case
        
        # Default to web application if no match
        return 'web_application'
    
    def _determine_sensitivity(description: str) -> str:
        """
        Determine data sensitivity level
        """
        description = description.lower()
        
        # Define sensitivity keywords
        sensitivity_keywords = {
            'high_sensitivity': [
                'financial', 'healthcare', 'personal data', 'confidential', 
                'regulated', 'compliance', 'secure', 'banking', 'medical'
            ],
            'medium_sensitivity': [
                'customer', 'user', 'profile', 'authentication', 'protected',
                'internal', 'enterprise', 'business'
            ]
        }
        
        # Check for high sensitivity keywords
        if any(keyword in description for keyword in sensitivity_keywords['high_sensitivity']):
            return 'high_sensitivity'
        
        # Check for medium sensitivity keywords
        if any(keyword in description for keyword in sensitivity_keywords['medium_sensitivity']):
            return 'medium_sensitivity'
        
        # Default to low sensitivity
        return 'low_sensitivity'
    
    # Determine use case template
    use_case = _identify_use_case(user_inputs.get('description', ''))
    use_case_template = use_case_templates.get(use_case, 
        use_case_templates['web_application'])
    
    # Determine security level
    sensitivity = _determine_sensitivity(user_inputs.get('description', ''))
    security_template = security_templates.get(sensitivity, 
        security_templates['low_sensitivity'])
    
    # Generate comprehensive recommendation
    return {
        'basicInfo': {
            'name': user_inputs.get('name', 'New Application'),
            'description': user_inputs.get('description', use_case_template['description']),
            'version': '1.0'
        },
        'architectureInfo': {
            'overview': 'Scalable and maintainable architecture design',
            'security': security_template,
            'components': [
                {'name': 'Frontend', 'description': 'User interface layer'},
                {'name': 'Backend', 'description': 'Business logic and data processing'},
                {'name': 'Database', 'description': 'Data storage and retrieval'}
            ]
        },
        'technologyStack': {
            'overview': 'Modern, scalable technology stack',
            'categories': [
                {
                    'name': 'Frontend',
                    'technologies': [
                        {
                            'name': use_case_template['recommended_technologies']['frontend'][0],
                            'version': 'Latest',
                            'purpose': 'User interface framework'
                        }
                    ]
                },
                {
                    'name': 'Backend',
                    'technologies': [
                        {
                            'name': use_case_template['recommended_technologies']['backend'][0],
                            'version': 'Latest',
                            'purpose': 'Server-side logic and API'
                        }
                    ]
                }
            ]
        }
    }
    
    def build_hldd_structure(self, application, user_inputs):
        """
        Build a comprehensive HLDD content structure
        
        :param application: Application model instance
        :param user_inputs: User-provided inputs for HLDD generation
        :return: Dictionary representing HLDD content
        """
        current_app.logger.info("Entering build_hldd_structure method")
        
        # Determine author name with multiple fallback options
        def get_author_name(user):
            if not user:
                return 'System User'
            
            # Try multiple potential attributes for the user's name
            name_attributes = [
                'name',  # First attempt
                'username',  # Common alternative
                'email',  # Fallback to email
                'first_name',  # Another potential attribute
            ]
            
            for attr in name_attributes:
                if hasattr(user, attr) and getattr(user, attr):
                    return str(getattr(user, attr))
            
            return 'Unknown User'

        # Import recommender dynamically to avoid circular imports
        from app.services.architecture_recommender import get_recommender
        
        # Get architecture recommendations
        recommender = get_recommender()
        try:
            arch_recommendations = recommender.recommend_architecture(
                application.use_case or '',
                application.requirements or ''
            )
        except Exception as arch_error:
            current_app.logger.warning(f"Architecture recommendation error: {str(arch_error)}")
            arch_recommendations = {
                'recommended_patterns': [{'pattern': 'Microservices'}]
            }

        return {
            'metadata': {
                'document_title': f"HLDD for {application.name}",
                'version': '1.0',
                'creation_date': datetime.utcnow().isoformat(),
                'authors': [get_author_name(application.user) if hasattr(application, 'user') else 'System User']
            },
            
            'executive_summary': {
                'project_summary': user_inputs.get('description', application.description or ''),
                'key_objectives': user_inputs.get('objectives', []),
                'target_audience': user_inputs.get('target_audience', []),
                'key_architectural_decisions': arch_recommendations.get('recommended_patterns', [])
            },
            'scope_and_objectives': {
                'project_description': user_inputs.get('description', application.description or ''),
                'project_scope': user_inputs.get('scope', ''),
                'in_scope_items': user_inputs.get('functions', []),
                'out_of_scope_items': []
            },
            'architecture_design': {
                'architectural_style': arch_recommendations.get('recommended_patterns', [{}])[0].get('pattern', 'Microservices'),
                'domain_driven_design': {
                    'core_domains': [],
                    'bounded_contexts': []
                },
                'api_design': {
                    'style': 'RESTful',
                    'versioning_strategy': 'Semantic Versioning'
                }
            },
                        'basicInfo': {
                'name': application.name,
                'description': user_inputs.get('description', application.description or ''),
                'version': '1.0',
                'creation_date': datetime.datetime.utcnow().isoformat(),
                'authors': [get_author_name(application.user) if hasattr(application, 'user') else 'System User']
            },
            'architectureInfo': {
                'architectural_style': arch_recommendations.get('recommended_patterns', [{}])[0].get('pattern', 'Microservices'),
                'key_architectural_decisions': arch_recommendations.get('recommended_patterns', [])
            },
            'technology_stack': self.extract_technology_stack(application),
            'cross_cutting_concerns': {
                'security': {
                    'authentication': 'To be defined',
                    'data_encryption': 'To be implemented'
                },
                'scalability': {
                    'strategy': 'Horizontal scaling'
                }
            }
        }
    
    def extract_technology_stack(self, application):
        """
        Extract technology stack from ApplicationTechnology model
        
        :param application: Application model instance
        :return: List of technology stack details
        """
        from app.models.application import ApplicationTechnology
        
        technologies = ApplicationTechnology.query.filter_by(application_id=application.id).all()
        return [
            {
                'area': tech.category or 'Uncategorized',
                'technology': tech.technology_name,
                'vendor': tech.vendor or 'Not Specified',
                'rationale': tech.notes or 'No specific rationale'
            } for tech in technologies
        ]
    
    def create_docx(self, file_path, hldd_content):
        """
        Create a Word document from HLDD content
        
        :param file_path: Path to save the document
        :param hldd_content: Dictionary containing HLDD content
        """
        # Placeholder for actual document generation
        # In a real implementation, use python-docx or similar library
        with open(file_path, 'w') as f:
            f.write(str(hldd_content))

def get_document_generator(upload_folder):
    """
    Factory function to get an HLDD generator instance
    
    :param upload_folder: Folder to store generated documents
    :return: HLDDGenerator instance
    """
    return HLDDGenerator(upload_folder)