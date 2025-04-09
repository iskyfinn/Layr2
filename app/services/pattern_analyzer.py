class PatternAnalyzer:
    """
    Service for analyzing and recommending architecture patterns and anti-patterns,
    and comparing cloud providers (AWS, Azure, Google Cloud, Oracle Cloud)
    """
    
    def __init__(self):
        # Architecture patterns knowledge base
        self.patterns = {
            'microservices': {
                'description': 'Breaking down an application into small, specialized services that communicate via APIs',
                'benefits': [
                    'Independent scaling of services',
                    'Technology diversity',
                    'Resilience through isolation',
                    'Easier continuous deployment'
                ],
                'challenges': [
                    'Increased operational complexity',
                    'Distributed system debugging',
                    'Network latency',
                    'Data consistency challenges'
                ],
                'cloud_implementations': {
                    'aws': ['ECS', 'EKS', 'App Mesh', 'API Gateway', 'Lambda'],
                    'azure': ['AKS', 'Service Fabric', 'Azure Functions', 'API Management'],
                    'google': ['GKE', 'Cloud Run', 'Cloud Functions', 'Apigee'],
                    'oracle': ['Container Engine for Kubernetes', 'API Gateway', 'Functions']
                }
            },
            'serverless': {
                'description': 'Running code without provisioning or managing servers, automatically scaling as needed',
                'benefits': [
                    'No server management',
                    'Pay-per-use pricing',
                    'Automatic scaling',
                    'Focus on code not infrastructure'
                ],
                'challenges': [
                    'Cold start latency',
                    'Limited execution duration',
                    'Vendor lock-in',
                    'Limited local testing'
                ],
                'cloud_implementations': {
                    'aws': ['Lambda', 'API Gateway', 'Step Functions', 'EventBridge'],
                    'azure': ['Azure Functions', 'Logic Apps', 'Event Grid'],
                    'google': ['Cloud Functions', 'Cloud Run', 'Workflows'],
                    'oracle': ['Functions', 'API Gateway', 'Events Service']
                }
            },
            'event_driven': {
                'description': 'Using events to trigger and communicate between decoupled services',
                'benefits': [
                    'Loose coupling',
                    'Scalability',
                    'Reactivity',
                    'Asynchronous processing'
                ],
                'challenges': [
                    'Eventual consistency',
                    'Complex debugging',
                    'Duplicate events handling',
                    'Error handling'
                ],
                'cloud_implementations': {
                    'aws': ['EventBridge', 'SNS', 'SQS', 'Kinesis'],
                    'azure': ['Event Grid', 'Event Hubs', 'Service Bus'],
                    'google': ['Pub/Sub', 'Cloud Tasks', 'Eventarc'],
                    'oracle': ['Events Service', 'Streaming', 'Messaging']
                }
            },
            'cqrs': {
                'description': 'Command Query Responsibility Segregation: separating read and write operations',
                'benefits': [
                    'Optimized query performance',
                    'Scalability of read and write sides',
                    'Simplified model design',
                    'Integration with event sourcing'
                ],
                'challenges': [
                    'Increased complexity',
                    'Data synchronization',
                    'Eventual consistency',
                    'Learning curve'
                ],
                'cloud_implementations': {
                    'aws': ['DynamoDB + ElastiCache', 'Aurora + OpenSearch'],
                    'azure': ['Cosmos DB (multi-model)', 'SQL Database + Cache for Redis'],
                    'google': ['Firestore + Memorystore', 'Spanner + BigQuery'],
                    'oracle': ['Autonomous Database', 'NoSQL Database']
                }
            },
            'api_gateway': {
                'description': 'Centralized entry point for API requests with routing, transformation, and security',
                'benefits': [
                    'Centralized control',
                    'Security enforcement',
                    'Traffic management',
                    'Analytics and monitoring'
                ],
                'challenges': [
                    'Single point of failure risk',
                    'Latency overhead',
                    'Configuration complexity',
                    'Deployment coordination'
                ],
                'cloud_implementations': {
                    'aws': ['API Gateway', 'AppSync (GraphQL)'],
                    'azure': ['API Management', 'Application Gateway'],
                    'google': ['Apigee', 'Cloud Endpoints'],
                    'oracle': ['API Gateway', 'API Platform']
                }
            },
            'circuit_breaker': {
                'description': 'Detecting failures and preventing cascade failures in distributed systems',
                'benefits': [
                    'Fail fast and recover',
                    'Graceful degradation',
                    'Fault isolation',
                    'Improved user experience during failures'
                ],
                'challenges': [
                    'Configuration complexity',
                    'Testing failure scenarios',
                    'Monitoring and alerting',
                    'Fallback implementation'
                ],
                'cloud_implementations': {
                    'aws': ['App Mesh', 'API Gateway (throttling)'],
                    'azure': ['API Management', 'Application Gateway', 'Service Fabric'],
                    'google': ['Istio on GKE', 'Cloud Endpoints'],
                    'oracle': ['API Gateway', 'Service Mesh']
                }
            }
        }
        
        # Anti-patterns knowledge base
        self.anti_patterns = {
            'monolithic_deployment': {
                'description': 'Deploying entire application as a single unit',
                'issues': [
                    'Long deployment times',
                    'Risk of full system outage',
                    'Scaling inefficiency',
                    'Technology lock-in'
                ],
                'remediation': 'Transition to microservices or modular monolith with independent deployable components'
            },
            'database_per_service': {
                'description': 'Each microservice has its own private database',
                'issues': [
                    'Data consistency challenges',
                    'Complex joins across services',
                    'Data duplication',
                    'Transaction management'
                ],
                'remediation': 'Consider shared databases for related services, event sourcing, or CQRS patterns'
            },
            'distributed_monolith': {
                'description': 'Microservices that are tightly coupled and must be deployed together',
                'issues': [
                    'Combines disadvantages of monoliths and distributed systems',
                    'Complex without benefits of independence',
                    'Deployment coordination overhead',
                    'Hard to test and maintain'
                ],
                'remediation': 'Identify and break dependencies, establish proper service boundaries, implement async communication'
            },
            'api_versioning_neglect': {
                'description': 'Not properly versioning APIs, breaking client applications',
                'issues': [
                    'Client breakage on changes',
                    'Forced client updates',
                    'Difficult to evolve APIs',
                    'Technical debt accumulation'
                ],
                'remediation': 'Implement proper API versioning strategy, use semantic versioning, maintain backward compatibility'
            },
            'direct_database_access': {
                'description': 'Applications accessing databases directly instead of through services',
                'issues': [
                    'Schema coupling',
                    'Difficult to evolve database schema',
                    'Security concerns',
                    'Potential data corruption'
                ],
                'remediation': 'Implement data access through APIs, use database views or stored procedures if direct access is needed'
            }
        }
        
        # Cloud provider comparison data
        self.cloud_comparison = {
            'compute': {
                'aws': {
                    'services': ['EC2', 'Lambda', 'ECS', 'EKS', 'Fargate', 'Batch', 'Lightsail'],
                    'strengths': ['Broadest selection of instance types', 'Mature autoscaling', 'Spot instances for cost savings'],
                    'considerations': ['Complex pricing', 'Regional feature differences']
                },
                'azure': {
                    'services': ['Virtual Machines', 'Functions', 'AKS', 'Container Instances', 'Batch', 'App Service'],
                    'strengths': ['Strong Windows integration', 'Hybrid deployment options', 'VMSS for autoscaling'],
                    'considerations': ['Reserved instance complexity', 'Some services are region limited']
                },
                'google': {
                    'services': ['Compute Engine', 'Cloud Functions', 'GKE', 'Cloud Run', 'App Engine'],
                    'strengths': ['Live migration during maintenance', 'Sustained use discounts', 'Advanced container orchestration'],
                    'considerations': ['Fewer instance types than competitors', 'Regional availability varies']
                },
                'oracle': {
                    'services': ['Compute', 'Functions', 'Container Engine for Kubernetes', 'Container Instances'],
                    'strengths': ['High performance bare metal', 'Consistent performance', 'Oracle-optimized compute'],
                    'considerations': ['Fewer global regions', 'Less mature container services']
                }
            },
            'storage': {
                'aws': {
                    'services': ['S3', 'EBS', 'EFS', 'FSx', 'Storage Gateway', 'Snow Family'],
                    'strengths': ['Mature object storage (S3)', 'Multiple storage classes', 'Extensive lifecycle management'],
                    'considerations': ['Cross-region data transfer costs', 'Storage class transition costs']
                },
                'azure': {
                    'services': ['Blob Storage', 'Files', 'Managed Disks', 'NetApp Files', 'StorSimple'],
                    'strengths': ['Integrated with Active Directory', 'Strong hybrid solutions', 'Geo-redundant storage'],
                    'considerations': ['Performance tiers complexity', 'Storage account limits']
                },
                'google': {
                    'services': ['Cloud Storage', 'Persistent Disk', 'Filestore', 'Transfer Service'],
                    'strengths': ['Automatic multi-regional redundancy', 'Single storage class with auto-tiering', 'Strong data transfer tools'],
                    'considerations': ['Fewer storage service options', 'Less mature file storage']
                },
                'oracle': {
                    'services': ['Object Storage', 'Block Volumes', 'File Storage', 'Data Transfer'],
                    'strengths': ['High performance block storage', 'Free ingress', 'Oracle integrated backup'],
                    'considerations': ['Fewer storage service options', 'Less mature lifecycle management']
                }
            },
            'database': {
                'aws': {
                    'services': ['RDS', 'DynamoDB', 'Aurora', 'Neptune', 'Redshift', 'ElastiCache', 'DocumentDB', 'Timestream'],
                    'strengths': ['Broad selection of database types', 'Aurora performance', 'DynamoDB scaling'],
                    'considerations': ['Pricing complexity', 'Reserved instance management']
                },
                'azure': {
                    'services': ['SQL Database', 'Cosmos DB', 'Database for MySQL/PostgreSQL/MariaDB', 'Cache for Redis', 'Synapse Analytics'],
                    'strengths': ['Cosmos DB flexibility', 'Deep SQL Server integration', 'Hyperscale options'],
                    'considerations': ['Performance tier selection complexity', 'DTU-based pricing model']
                },
                'google': {
                    'services': ['Cloud SQL', 'Bigtable', 'Firestore', 'Spanner', 'BigQuery', 'Memorystore'],
                    'strengths': ['Spanner global distribution', 'BigQuery performance', 'Strong analytics integration'],
                    'considerations': ['Fewer managed database options', 'Higher Spanner costs']
                },
                'oracle': {
                    'services': ['Autonomous Database', 'Database Service', 'MySQL Database Service', 'NoSQL Database'],
                    'strengths': ['Best Oracle Database performance', 'Self-driving Autonomous Database', 'Built-in optimization'],
                    'considerations': ['Focused primarily on Oracle databases', 'Fewer NoSQL options']
                }
            },
            'networking': {
                'aws': {
                    'services': ['VPC', 'Direct Connect', 'Route 53', 'CloudFront', 'Global Accelerator', 'Transit Gateway'],
                    'strengths': ['Mature VPC features', 'Extensive DNS options', 'Large global network'],
                    'considerations': ['Complex connectivity between VPCs', 'Regional networking differences']
                },
                'azure': {
                    'services': ['Virtual Network', 'ExpressRoute', 'DNS', 'CDN', 'Load Balancer', 'Front Door', 'Virtual WAN'],
                    'strengths': ['Strong hybrid networking', 'Global VNet peering', 'Integrated firewall'],
                    'considerations': ['More complex to set up than AWS', 'Service endpoint limitations']
                },
                'google': {
                    'services': ['VPC', 'Cloud Interconnect', 'Cloud DNS', 'Cloud CDN', 'Cloud Load Balancing', 'Network Service Tiers'],
                    'strengths': ['Global VPC without regions', 'Tier selection for cost optimization', 'Google backbone network'],
                    'considerations': ['Fewer VPC features than AWS', 'Less mature hybrid options']
                },
                'oracle': {
                    'services': ['Virtual Cloud Network', 'FastConnect', 'DNS', 'Load Balancer', 'Web Application Firewall'],
                    'strengths': ['Simple flat network design', 'Free ingress/egress within regions', 'Straightforward pricing'],
                    'considerations': ['Less feature-rich than competitors', 'Smaller global network']
                }
            }
        }
        
        # CPU-friendly optimizations
        self.is_cpu_optimized = True
    
    def analyze_tech_stack(self, tech_stack_description, use_case):
        """
        Analyze a technology stack description and provide pattern/anti-pattern insights
        
        Parameters:
        - tech_stack_description: String describing technology stack
        - use_case: String describing the use case
        
        Returns:
        - Dictionary with analysis results
        """
        tech_stack_lower = tech_stack_description.lower()
        use_case_lower = use_case.lower()
        
        # Identify relevant patterns
        relevant_patterns = self._identify_patterns(tech_stack_lower, use_case_lower)
        
        # Identify potential anti-patterns
        potential_anti_patterns = self._identify_anti_patterns(tech_stack_lower, use_case_lower)
        
        # Compare cloud providers for this use case
        cloud_comparison = self._compare_cloud_providers(tech_stack_lower, use_case_lower)
        
        return {
            'relevant_patterns': relevant_patterns,
            'potential_anti_patterns': potential_anti_patterns,
            'cloud_comparison': cloud_comparison
        }
    
    def _identify_patterns(self, tech_stack, use_case):
        """Identify architecture patterns relevant to the tech stack and use case"""
        relevant_patterns = []
        
        for pattern_name, pattern_data in self.patterns.items():
            relevance_score = 0
            relevance_factors = []
            
            # Check pattern keywords in tech stack
            pattern_keywords = pattern_data['description'].lower().split()
            for keyword in pattern_keywords:
                if len(keyword) > 4 and keyword in tech_stack:  # Only consider significant words
                    relevance_score += 1
                    relevance_factors.append(f"Tech stack mentions {keyword}")
            
            # Check if use case aligns with pattern benefits
            for benefit in pattern_data['benefits']:
                benefit_lower = benefit.lower()
                if any(term in use_case for term in benefit_lower.split() if len(term) > 4):
                    relevance_score += 2
                    relevance_factors.append(f"Use case aligns with benefit: {benefit}")
            
            # Check for specific technology mentions that suggest pattern use
            for cloud, implementations in pattern_data['cloud_implementations'].items():
                for impl in implementations:
                    if impl.lower() in tech_stack:
                        relevance_score += 3
                        relevance_factors.append(f"Tech stack uses {impl} which implements this pattern")
            
            # Only include patterns with sufficient relevance
            if relevance_score >= 2:
                relevant_patterns.append({
                    'pattern': pattern_name,
                    'description': pattern_data['description'],
                    'relevance_score': relevance_score,
                    'relevance_factors': relevance_factors,
                    'benefits': pattern_data['benefits'],
                    'challenges': pattern_data['challenges'],
                    'implementations': pattern_data['cloud_implementations']
                })
        
        # Sort by relevance score
        relevant_patterns.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # CPU optimization: limit results
        if self.is_cpu_optimized and len(relevant_patterns) > 3:
            return relevant_patterns[:3]
        
        return relevant_patterns
    
    def _identify_anti_patterns(self, tech_stack, use_case):
        """Identify potential anti-patterns in the tech stack"""
        potential_anti_patterns = []
        
        for anti_pattern_name, anti_pattern_data in self.anti_patterns.items():
            risk_score = 0
            risk_factors = []
            
            # Check anti-pattern keywords in tech stack
            anti_pattern_keywords = anti_pattern_data['description'].lower().split()
            for keyword in anti_pattern_keywords:
                if len(keyword) > 4 and keyword in tech_stack:
                    risk_score += 1
                    risk_factors.append(f"Tech stack mentions {keyword}")
            
            # Check for red flags in tech description
            issues = anti_pattern_data['issues']
            for issue in issues:
                issue_lower = issue.lower()
                issue_keywords = [word for word in issue_lower.split() if len(word) > 4]
                
                for keyword in issue_keywords:
                    if keyword in tech_stack:
                        risk_score += 1
                        risk_factors.append(f"Tech stack may have issue: {issue}")
            
            # Check specific anti-pattern indicators
            if anti_pattern_name == 'monolithic_deployment' and any(term in tech_stack for term in ['monolith', 'single deployment', 'all-in-one']):
                risk_score += 2
                risk_factors.append("Tech stack suggests monolithic deployment")
            
            elif anti_pattern_name == 'database_per_service' and all(term in tech_stack for term in ['microservice', 'database']) and 'shared database' not in tech_stack:
                risk_score += 2
                risk_factors.append("Tech stack suggests database per service without addressing consistency challenges")
            
            elif anti_pattern_name == 'distributed_monolith' and all(term in tech_stack for term in ['distributed', 'coupled', 'dependency']):
                risk_score += 2
                risk_factors.append("Tech stack suggests distributed components with tight coupling")
            
            # Only include anti-patterns with sufficient risk
            if risk_score >= 2:
                potential_anti_patterns.append({
                    'anti_pattern': anti_pattern_name,
                    'description': anti_pattern_data['description'],
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'issues': anti_pattern_data['issues'],
                    'remediation': anti_pattern_data['remediation']
                })
        
        # Sort by risk score
        potential_anti_patterns.sort(key=lambda x: x['risk_score'], reverse=True)
        
        # CPU optimization: limit results
        if self.is_cpu_optimized and len(potential_anti_patterns) > 3:
            return potential_anti_patterns[:3]
        
        return potential_anti_patterns
    
    def _compare_cloud_providers(self, tech_stack, use_case):
        """Compare cloud providers based on tech stack and use case"""
        cloud_scores = {
            'aws': 0,
            'azure': 0,
            'google': 0,
            'oracle': 0
        }
        
        cloud_recommendations = {}
        
        # Identify primary focus areas based on the use case and tech stack
        focus_areas = []
        
        if any(term in tech_stack or term in use_case for term in ['database', 'data', 'storage']):
            focus_areas.append('database')
            focus_areas.append('storage')
        
        if any(term in tech_stack or term in use_case for term in ['compute', 'processing', 'server', 'container']):
            focus_areas.append('compute')
        
        if any(term in tech_stack or term in use_case for term in ['network', 'connectivity', 'hybrid', 'multi-region']):
            focus_areas.append('networking')
        
        # If no specific areas identified, consider all areas
        if not focus_areas:
            focus_areas = ['compute', 'storage', 'database', 'networking']
        
        # Analyze each focus area
        for area in focus_areas:
            area_comparison = {}
            
            for cloud, data in self.cloud_comparison[area].items():
                cloud_score = 0
                
                # Check for service mentions in tech stack
                for service in data['services']:
                    if service.lower() in tech_stack:
                        cloud_score += 2
                
                # Check if strengths align with use case
                for strength in data['strengths']:
                    strength_lower = strength.lower()
                    if any(term in use_case for term in strength_lower.split() if len(term) > 4):
                        cloud_score += 1
                
                # Add score to total
                cloud_scores[cloud] += cloud_score
                
                # Add to area comparison
                area_comparison[cloud] = {
                    'services': data['services'],
                    'strengths': data['strengths'],
                    'considerations': data['considerations'],
                    'area_score': cloud_score
                }
            
            cloud_recommendations[area] = area_comparison
        
        # Calculate overall recommendation
        top_clouds = sorted(cloud_scores.items(), key=lambda x: x[1], reverse=True)
        
        result = {
            'focus_areas': focus_areas,
            'area_recommendations': cloud_recommendations,
            'overall_ranking': [
                {
                    'provider': cloud, 
                    'score': score,
                    'key_strengths': self._get_key_strengths(cloud, focus_areas)
                } for cloud, score in top_clouds
            ]
        }
        
        # CPU optimization: limit detailed results
        if self.is_cpu_optimized:
            # Only return top 2 providers in detail
            result['overall_ranking'] = result['overall_ranking'][:2]
        
        return result
    
    def _get_key_strengths(self, cloud, focus_areas):
        """Get key strengths for a cloud provider based on focus areas"""
        strengths = []
        
        for area in focus_areas:
            strengths.extend(self.cloud_comparison[area][cloud]['strengths'][:2])
        
        # Remove duplicates and limit to top 3 for conciseness
        unique_strengths = list(dict.fromkeys(strengths))
        return unique_strengths[:3]

def get_pattern_analyzer(cpu_optimized=True):
    """Factory function to get an instance of the Pattern Analyzer"""
    analyzer = PatternAnalyzer()
    analyzer.is_cpu_optimized = cpu_optimized
    return analyzer