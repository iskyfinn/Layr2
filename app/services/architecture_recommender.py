# app/services/architecture_recommender.py

import re
import json
import numpy as np
from collections import defaultdict


class ArchitectureRecommender:
    """
    Service for recommending architecture based on use case and requirements
    """
    
    def __init__(self):
        # Load architecture patterns knowledge base
        self.patterns = self._load_patterns()
        
        # Define requirement categories
        self.requirement_categories = {
            'security': [
                'encryption', 'authentication', 'authorization', 'compliance',
                'audit', 'security', 'sensitive', 'privacy', 'confidential'
            ],
            'scalability': [
                'scale', 'volume', 'traffic', 'throughput', 'growth', 'concurrent',
                'users', 'load', 'capacity', 'performance', 'response time'
            ],
            'reliability': [
                'availability', 'uptime', 'failover', 'redundancy', 'backup',
                'recovery', 'disaster', 'fault tolerance', 'sla', 'reliable'
            ],
            'cost': [
                'budget', 'cost', 'expense', 'affordable', 'cheap', 'price',
                'investment', 'value', 'economical', 'efficient'
            ],
            'time_to_market': [
                'deadline', 'quick', 'rapid', 'fast', 'immediate', 'urgent',
                'time-to-market', 'speed', 'agile', 'iterative'
            ],
            'maintainability': [
                'maintain', 'update', 'change', 'extend', 'flexible', 'modular',
                'reuse', 'standardized', 'documented', 'simple'
            ],
            'integration': [
                'integrate', 'connect', 'interface', 'api', 'third-party',
                'existing systems', 'legacy', 'interoperable', 'data exchange'
            ]
        }
        
        # Define common use cases
        self.use_cases = {
            'web_application': [
                'web', 'browser', 'website', 'portal', 'online', 'internet',
                'responsive', 'web app', 'web application'
            ],
            'mobile_application': [
                'mobile', 'app', 'android', 'ios', 'smartphone', 'tablet',
                'mobile app', 'mobile application'
            ],
            'data_processing': [
                'processing', 'etl', 'analytics', 'data', 'large data', 'big data',
                'batch', 'stream', 'data pipeline', 'data processing'
            ],
            'api_service': [
                'api', 'service', 'microservice', 'restful', 'soap', 'graphql',
                'endpoint', 'interface', 'web service', 'api gateway'
            ],
            'internal_tool': [
                'internal', 'tool', 'admin', 'backoffice', 'dashboard', 'reporting',
                'monitoring', 'management', 'intranet'
            ]
        }
        
        # Cloud provider strengths
        self.cloud_strengths = {
            'aws': ['scalability', 'breadth of services', 'mature ecosystem', 'global reach', 'serverless'],
            'azure': ['enterprise integration', 'windows ecosystem', 'hybrid cloud', 'ml/ai services'],
            'google': ['data analytics', 'kubernetes', 'machine learning', 'global network', 'cost optimization'],
            'oracle': ['database performance', 'integrated stack', 'enterprise workloads', 'java ecosystem']
        }
    
    def _load_patterns(self):
        """Load architecture patterns (in real app, could be from a database or file)"""
        return {
            'microservices': {
                'description': 'Architecture with small, independent services that communicate over a network',
                'best_for': ['scalability', 'maintainability', 'agility'],
                'caution_for': ['cost', 'complexity', 'operational overhead'],
                'cloud_fit': {
                    'aws': 0.9, 'azure': 0.9, 'google': 0.9, 'oracle': 0.7
                },
                'use_cases': ['web_application', 'api_service'],
                'components': [
                    'API Gateway', 'Service Discovery', 'Container Orchestration', 
                    'Distributed Logging', 'Monitoring', 'CI/CD Pipeline'
                ]
            },
            'serverless': {
                'description': 'Event-driven architecture where code runs in stateless containers',
                'best_for': ['cost optimization', 'scalability', 'time_to_market'],
                'caution_for': ['vendor lock-in', 'cold starts', 'debugging'],
                'cloud_fit': {
                    'aws': 0.95, 'azure': 0.85, 'google': 0.9, 'oracle': 0.6
                },
                'use_cases': ['api_service', 'data_processing'],
                'components': [
                    'Function-as-a-Service', 'API Gateway', 'Event Bus', 
                    'Managed Database', 'Storage', 'Monitoring'
                ]
            },
            'monolithic': {
                'description': 'Traditional single-deployment architecture with all components in one application',
                'best_for': ['simplicity', 'time_to_market', 'small teams'],
                'caution_for': ['scalability', 'agility', 'large applications'],
                'cloud_fit': {
                    'aws': 0.7, 'azure': 0.8, 'google': 0.7, 'oracle': 0.9
                },
                'use_cases': ['internal_tool', 'web_application'],
                'components': [
                    'Application Server', 'Database', 'Load Balancer', 
                    'Caching', 'Monitoring', 'Backup System'
                ]
            },
            'event_driven': {
                'description': 'Architecture where components communicate through events',
                'best_for': ['loose coupling', 'scalability', 'responsiveness'],
                'caution_for': ['debugging', 'eventual consistency', 'complexity'],
                'cloud_fit': {
                    'aws': 0.9, 'azure': 0.9, 'google': 0.8, 'oracle': 0.6
                },
                'use_cases': ['data_processing', 'api_service'],
                'components': [
                    'Event Bus', 'Message Queue', 'Stream Processor', 
                    'Event Store', 'API Gateway', 'Subscriber Services'
                ]
            },
            'layered': {
                'description': 'Architecture organized in horizontal layers (presentation, business, data, etc.)',
                'best_for': ['maintainability', 'separation of concerns', 'testing'],
                'caution_for': ['performance', 'scalability', 'tight coupling'],
                'cloud_fit': {
                    'aws': 0.8, 'azure': 0.9, 'google': 0.8, 'oracle': 0.9
                },
                'use_cases': ['web_application', 'internal_tool', 'mobile_application'],
                'components': [
                    'Web Tier', 'Application Tier', 'Data Access Layer', 
                    'Database', 'Load Balancer', 'Caching'
                ]
            }
        }

class ArchitectureRecommender:
    def recommend_architecture(self, use_case, requirements, baseline_systems=None):
        """
        Generate comprehensive architecture recommendations based on application details.
        
        :param use_case: String describing the application's primary use case
        :param requirements: List or string of application requirements
        :param baseline_systems: Optional existing systems or infrastructure
        :return: Dictionary of architecture recommendations
        """
        # Normalize inputs
        use_case = use_case.lower() if use_case else 'general_application'
        requirements = requirements if isinstance(requirements, list) else [requirements]
        
        # Determine identified use case
        identified_use_case = self._classify_use_case(use_case)
        
        # Analyze requirements
        requirement_priorities = self._analyze_requirements(requirements)
        
        # Recommend cloud providers
        cloud_recommendations = self._recommend_cloud_providers(
            identified_use_case, 
            requirement_priorities
        )
        
        # Recommend architectural patterns
        recommended_patterns = self._recommend_architectural_patterns(
            identified_use_case, 
            requirement_priorities
        )
        
        return {
            'identified_use_case': identified_use_case,
            'requirement_priorities': requirement_priorities,
            'cloud_recommendations': cloud_recommendations,
            'recommended_patterns': recommended_patterns,
            'baseline_systems_considered': baseline_systems
        }
    
    def _classify_use_case(self, use_case):
        """
        Classify the use case into a standard category
        """
        use_case_mapping = {
            'web': 'web_application',
            'mobile': 'mobile_application',
            'data': 'data_processing',
            'analytics': 'business_intelligence',
            'machine learning': 'ai_ml_application',
            'iot': 'internet_of_things',
            'enterprise': 'enterprise_system'
        }
        
        # Find the best match
        for key, category in use_case_mapping.items():
            if key in use_case:
                return category
        
        return 'general_application'
    
    def _analyze_requirements(self, requirements):
        """
        Analyze and prioritize requirements
        """
        # Default priorities
        priorities = {
            'security': 0.8,
            'scalability': 0.7,
            'reliability': 0.9,
            'maintainability': 0.6,
            'cost': 0.5
        }
        
        # Adjust priorities based on requirements
        for req in requirements:
            req = req.lower()
            if 'secure' in req or 'security' in req:
                priorities['security'] = min(priorities['security'] + 0.1, 1.0)
            if 'scale' in req or 'scalable' in req:
                priorities['scalability'] = min(priorities['scalability'] + 0.1, 1.0)
            if 'reliable' in req or 'uptime' in req:
                priorities['reliability'] = min(priorities['reliability'] + 0.1, 1.0)
            if 'maintain' in req or 'update' in req:
                priorities['maintainability'] = min(priorities['maintainability'] + 0.1, 1.0)
        
        return priorities
    
    def _recommend_cloud_providers(self, use_case, priorities):
        """
        Recommend cloud providers based on use case and priorities
        """
        # Default cloud recommendations
        cloud_recommendations = {
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
        
        # Adjust recommendations based on use case
        provider_strengths = {
            'web_application': 'aws',
            'mobile_application': 'google',
            'data_processing': 'google',
            'business_intelligence': 'azure',
            'ai_ml_application': 'google',
            'internet_of_things': 'aws',
            'enterprise_system': 'azure'
        }
        
        # Prioritize based on use case
        if use_case in provider_strengths:
            primary = provider_strengths[use_case]
            # Swap primary provider
            cloud_recommendations['primary'] = primary
            
            # Adjust scores and overall ranking
            ranking = cloud_recommendations['overall_ranking']
            primary_index = next(i for i, item in enumerate(ranking) if item['provider'] == primary)
            
            # Swap first and primary provider items
            ranking[0], ranking[primary_index] = ranking[primary_index], ranking[0]
        
        return cloud_recommendations
    
    def _recommend_architectural_patterns(self, use_case, priorities):
        """
        Recommend architectural patterns based on use case and priorities
        """
        # Base microservices pattern
        recommended_patterns = [
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
        
        # Adjust patterns based on use case and priorities
        use_case_patterns = {
            'web_application': {
                'pattern': 'microservices',
                'additional_pattern': 'serverless'
            },
            'mobile_application': {
                'pattern': 'backend_for_frontend',
                'additional_pattern': 'microservices'
            },
            'data_processing': {
                'pattern': 'event_driven',
                'additional_pattern': 'microservices'
            },
            'ai_ml_application': {
                'pattern': 'microservices',
                'additional_pattern': 'distributed_computing'
            }
        }
        
        return recommended_patterns

def _recommend_cloud_provider(self, requirements, pattern_recommendations):
    """Recommend cloud provider based on requirements and architecture patterns"""
    cloud_scores = {
        'aws': 0,
        'azure': 0,
        'google': 0,
        'oracle': 0
    }
    
    # Score based on requirements match to cloud strengths
    for req_name, req_priority in requirements.items():
        for cloud, strengths in self.cloud_strengths.items():
            if any(strength.lower() in req_name.lower() for strength in strengths):
                cloud_scores[cloud] += req_priority * 0.6
    
    # Score based on pattern fit with cloud providers
    for pattern_name, pattern_data in pattern_recommendations:
        pattern_obj = self.patterns[pattern_name]
        pattern_weight = pattern_data['overall_score']
        
        for cloud, fit_score in pattern_obj['cloud_fit'].items():
            cloud_scores[cloud] += fit_score * pattern_weight * 0.4
    
    # Get top recommendations
    sorted_clouds = sorted(cloud_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Create the overall_ranking array that the template expects
    overall_ranking = []
    for cloud, score in sorted_clouds:
        overall_ranking.append({
            'provider': cloud,
            'score': round(score, 2),
            'key_strengths': self._get_key_strengths(cloud, ['compute', 'storage', 'database'])
        })
    
    return {
        'primary': sorted_clouds[0][0],
        'secondary': sorted_clouds[1][0],
        'scores': {cloud: round(score, 2) for cloud, score in sorted_clouds},
        'overall_ranking': overall_ranking,
        'focus_areas': ['compute', 'storage', 'database']  # You might want to determine these dynamically
    }

def _get_key_strengths(self, cloud, focus_areas):
    """Get key strengths for a cloud provider"""
    # This is a placeholder - implement according to your data model
    strengths_map = {
        'aws': ['Breadth of services', 'Global reach', 'Mature ecosystem'],
        'azure': ['Enterprise integration', 'Hybrid cloud', 'Windows ecosystem'],
        'google': ['Data analytics', 'Kubernetes', 'Machine learning'],
        'oracle': ['Database performance', 'Integrated stack', 'Enterprise workloads']
    }
    return strengths_map.get(cloud, ['No specific strengths identified'])
    def _identify_use_case(self, use_case_text):
        """Identify the primary use case category from text description"""
        use_case_text = use_case_text.lower()
        use_case_scores = {}
        
        for category, keywords in self.use_cases.items():
            score = 0
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', use_case_text):
                    score += 1
            
            use_case_scores[category] = score
        
        # Get the top scoring use case
        if not use_case_scores or max(use_case_scores.values()) == 0:
            return 'unknown'
        
        return max(use_case_scores.items(), key=lambda x: x[1])[0]
    
    def _analyze_requirements(self, requirements_text):
        """Analyze requirements to determine priorities"""
        requirements_text = requirements_text.lower()
        requirement_scores = {}
        
        for category, keywords in self.requirement_categories.items():
            score = 0
            for keyword in keywords:
                matches = re.findall(r'\b' + re.escape(keyword) + r'\b', requirements_text)
                score += len(matches)
            
            # Normalize score (0-1 range)
            max_expected_occurrences = len(keywords)
            normalized_score = min(1.0, score / max_expected_occurrences)
            requirement_scores[category] = round(normalized_score, 2)
        
        # Ensure we have at least some priorities
        if sum(requirement_scores.values()) == 0:
            # Default to balanced priorities
            for category in self.requirement_categories.keys():
                requirement_scores[category] = 0.5
        
        return requirement_scores
    
    def _analyze_baseline_systems(self, baseline_text):
        """Analyze baseline systems to understand current technology stack"""
        baseline_text = baseline_text.lower()
        
        # Common technologies to look for
        technologies = {
            'languages': ['java', 'python', 'c#', '.net', 'javascript', 'typescript', 'go', 'ruby', 'php'],
            'databases': ['sql server', 'oracle', 'mysql', 'postgresql', 'mongodb', 'dynamodb', 'cosmos db', 'cassandra'],
            'cloud': ['aws', 'azure', 'google cloud', 'gcp', 'oracle cloud', 'on-premises', 'on-prem'],
            'frameworks': ['spring', 'django', 'flask', 'express', 'react', 'angular', 'vue', 'asp.net'],
            'infrastructure': ['kubernetes', 'docker', 'container', 'vm', 'serverless', 'lambda', 'ec2', 'ecs']
        }
        
        found_tech = defaultdict(list)
        
        for category, tech_list in technologies.items():
            for tech in tech_list:
                if re.search(r'\b' + re.escape(tech) + r'\b', baseline_text):
                    found_tech[category].append(tech)
        
        return dict(found_tech)
    
    def _score_patterns(self, use_case, requirements, baseline_tech=None):
        """Score each architecture pattern based on the use case and requirements"""
        pattern_scores = {}
        
        for pattern_name, pattern_data in self.patterns.items():
            score = 0
            reasoning = []
            
            # Score based on use case fit
            use_case_score = 1.0 if use_case in pattern_data['use_cases'] else 0.3
            score += use_case_score * 0.3  # 30% weight for use case fit
            
            if use_case_score > 0.5:
                reasoning.append(f"Good fit for {use_case} use case")
            else:
                reasoning.append(f"Not ideal for {use_case} use case")
            
            # Score based on requirements
            req_score = 0
            req_weight = 0
            
            for req_name, req_priority in requirements.items():
                if req_priority > 0:  # Only consider non-zero priorities
                    req_weight += req_priority
                    if req_name in pattern_data['best_for']:
                        req_score += req_priority
                        reasoning.append(f"Strong support for {req_name} requirement")
                    elif req_name in pattern_data['caution_for']:
                        # Still give some points but fewer
                        req_score += req_priority * 0.3
                        reasoning.append(f"Caution: {req_name} may be challenging with this pattern")
                    else:
                        # Neutral case
                        req_score += req_priority * 0.5
            
            # Normalize requirements score
            if req_weight > 0:
                req_score = req_score / req_weight
            else:
                req_score = 0.5  # Default score if no requirements specified
            
            score += req_score * 0.5  # 50% weight for requirements fit
            
            # Adjust score for baseline tech stack if available
            if baseline_tech:
                compatibility_score = self._assess_baseline_compatibility(pattern_name, baseline_tech)
                score += compatibility_score * 0.2  # 20% weight for baseline compatibility
                
                if compatibility_score > 0.7:
                    reasoning.append("Good compatibility with existing technology stack")
                elif compatibility_score < 0.4:
                    reasoning.append("May require significant changes to existing technology stack")
            
            pattern_scores[pattern_name] = {
                'overall_score': round(score, 2),
                'reasoning': reasoning
            }
        
        return pattern_scores
    
    def _assess_baseline_compatibility(self, pattern_name, baseline_tech):
        """Assess compatibility of an architecture pattern with baseline technology"""
        # This is a simplified implementation that could be expanded
        
        compatibility_score = 0.5  # Default neutral score
        
        # Examples of compatibility logic (simplified)
        if pattern_name == 'microservices':
            # Microservices work well with containerization
            if 'infrastructure' in baseline_tech and any(t in ['kubernetes', 'docker', 'container'] for t in baseline_tech['infrastructure']):
                compatibility_score = 0.9
            # Java and Spring are often used for microservices
            elif 'languages' in baseline_tech and 'java' in baseline_tech['languages']:
                compatibility_score = 0.8
        
        elif pattern_name == 'serverless':
            # Serverless works well with cloud environments
            if 'cloud' in baseline_tech and any(c in ['aws', 'azure', 'google cloud', 'gcp'] for c in baseline_tech['cloud']):
                compatibility_score = 0.9
            # On-premises environments are challenging for serverless
            elif 'cloud' in baseline_tech and any(c in ['on-premises', 'on-prem'] for c in baseline_tech['cloud']):
                compatibility_score = 0.3
        
        elif pattern_name == 'monolithic':
            # Monolithic works well with traditional stacks
            if 'languages' in baseline_tech and any(l in ['.net', 'java'] for l in baseline_tech['languages']):
                compatibility_score = 0.8
            # More compatible with on-premises environments
            if 'cloud' in baseline_tech and any(c in ['on-premises', 'on-prem'] for c in baseline_tech['cloud']):
                compatibility_score = 0.8
        
        return compatibility_score
    
    def _recommend_cloud_provider(self, requirements, pattern_recommendations):
        """Recommend cloud provider based on requirements and architecture patterns"""
        cloud_scores = {
            'aws': 0,
            'azure': 0,
            'google': 0,
            'oracle': 0
        }
        
        # Score based on requirements match to cloud strengths
        for req_name, req_priority in requirements.items():
            for cloud, strengths in self.cloud_strengths.items():
                if any(strength.lower() in req_name.lower() for strength in strengths):
                    cloud_scores[cloud] += req_priority * 0.6
        
        # Score based on pattern fit with cloud providers
        for pattern_name, pattern_data in pattern_recommendations:
            pattern_obj = self.patterns[pattern_name]
            pattern_weight = pattern_data['overall_score']
            
            for cloud, fit_score in pattern_obj['cloud_fit'].items():
                cloud_scores[cloud] += fit_score * pattern_weight * 0.4
        
        # Get top recommendations
        sorted_clouds = sorted(cloud_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'primary': sorted_clouds[0][0],
            'secondary': sorted_clouds[1][0],
            'scores': {cloud: round(score, 2) for cloud, score in sorted_clouds}
        }


def get_recommender():
    """Factory function to get an instance of the Architecture Recommender"""
    return ArchitectureRecommender()