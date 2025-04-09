import re
from collections import defaultdict

class ModernizationStrategy:
    """
    Service for recommending application modernization strategies
    """
    
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
    
    def recommend_strategy(self, application_info, hldd_analysis=None):
        """
        Recommend modernization strategy based on application information
        
        Parameters:
        - application_info: Dictionary with application details
        - hldd_analysis: Optional HLDD analysis results
        
        Returns:
        - Dictionary with modernization recommendations
        """
        try:
            # Extract information
            app_description = application_info.get('description', '')
            tech_stack = application_info.get('tech_stack', '')
            age = application_info.get('age', '')
            business_value = application_info.get('business_value', '')
            
            # Combined text for analysis
            combined_text = f"{app_description} {tech_stack} {age} {business_value}".lower()
            
            # Analyze application factors
            factors = self._analyze_factors(combined_text, hldd_analysis)
            
            # Score each modernization strategy
            strategy_scores = self._score_strategies(factors, combined_text)
            
            # Get top recommendations
            recommended_strategies = sorted(strategy_scores.items(), key=lambda x: x[1]['overall_score'], reverse=True)
            
            # Format the response
            return {
                'factors': factors,
                'recommended_strategies': [
                    {
                        'strategy': self.strategies[strategy],
                        'score': data['overall_score'],
                        'reasoning': data['reasoning']
                    } for strategy, data in recommended_strategies[:3]  # Return top 3 strategies
                ]
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'recommended_strategies': []
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


def get_modernization_strategy():
    """Factory function to get an instance of the Modernization Strategy recommender"""
    return ModernizationStrategy()