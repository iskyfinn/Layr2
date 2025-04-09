import unittest
import os
import tempfile
from app.services.hldd_analyzer import HLDDAnalyzer

class TestHLDDAnalyzer(unittest.TestCase):
    """Test cases for the HLDD Analyzer service"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = HLDDAnalyzer()
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        
        # Create a sample HLDD text file for testing
        self.sample_hldd_path = os.path.join(self.test_dir.name, 'sample_hldd.txt')
        with open(self.sample_hldd_path, 'w') as f:
            f.write("""
            # Sample High-Level Design Document
            
            ## System Architecture
            
            The system uses a microservices architecture with the following components:
            
            - API Gateway for authentication and routing
            - User Service for user management
            - Content Service for managing content
            - Notification Service for handling notifications
            
            ## Security Considerations
            
            - All services use SSL/TLS encryption for data in transit
            - Authentication using JWT tokens
            - Authorization based on user roles
            - Regular security audits
            - Firewall protection
            
            ## Scalability Considerations
            
            - Horizontal scaling of services using Kubernetes
            - Load balancing with automatic scaling
            - Database partition strategy for high throughput
            - Caching layer for frequently accessed data
            
            ## Reliability Considerations
            
            - Redundancy for critical services
            - Backup strategy with daily snapshots
            - Disaster recovery plan
            - High availability configuration
            - Monitoring and alerting
            
            ## Database Design
            
            The system uses PostgreSQL for relational data and MongoDB for document storage.
            """)
    
    def tearDown(self):
        """Clean up test environment"""
        self.test_dir.cleanup()
    
    def test_read_text_document(self):
        """Test reading a text document"""
        content = self.analyzer._read_text(self.sample_hldd_path)
        self.assertIsInstance(content, str)
        self.assertIn("System Architecture", content)
        self.assertIn("microservices", content)
    
    def test_identify_missing_components(self):
        """Test identifying missing components in a document"""
        content = self.analyzer._read_text(self.sample_hldd_path)
        missing = self.analyzer._identify_missing_components(content)
        
        # The sample HLDD contains security, but not all required components
        self.assertIn('security', self.analyzer.required_components)
        self.assertNotIn('security', missing)
        
        # Verify that we can find at least one missing component
        self.assertTrue(len(missing) > 0)
    
    def test_calculate_criteria_scores(self):
        """Test calculating scores for evaluation criteria"""
        content = self.analyzer._read_text(self.sample_hldd_path)
        scores = self.analyzer._calculate_criteria_scores(content)
        
        # Check that all criteria have scores
        for criterion in self.analyzer.criteria:
            self.assertIn(criterion, scores)
            self.assertIn('score', scores[criterion])
            self.assertIn('keywords_found', scores[criterion])
        
        # Security score should be high given our sample document
        self.assertGreater(scores['security']['score'], 0.5)
    
    def test_generate_recommendations(self):
        """Test generating recommendations based on analysis"""
        # Create a mock analysis result
        mock_results = {
            'scores': {
                'security': {'score': 0.8, 'keywords_found': 5},
                'scalability': {'score': 0.7, 'keywords_found': 4},
                'reliability': {'score': 0.6, 'keywords_found': 3},
                'maintainability': {'score': 0.3, 'keywords_found': 1},
                'cost_optimization': {'score': 0.2, 'keywords_found': 1},
                'compliance': {'score': 0.1, 'keywords_found': 0}
            },
            'missing_components': ['monitoring', 'backup'],
            'overall_score': 0.65
        }
        
        recommendations = self.analyzer._generate_recommendations(mock_results)
        
        # Verify that recommendations are generated
        self.assertIsInstance(recommendations, list)
        self.assertTrue(len(recommendations) > 0)
        
        # Recommendations should include missing components
        self.assertTrue(any('monitoring' in rec for rec in recommendations))
        
        # Recommendations should include low-scoring criteria
        self.assertTrue(any('compliance' in rec.lower() for rec in recommendations))
    
    def test_analyze_document(self):
        """Test the full document analysis process"""
        results = self.analyzer.analyze_document(self.sample_hldd_path)
        
        # Check that all expected keys are in the results
        self.assertIn('scores', results)
        self.assertIn('missing_components', results)
        self.assertIn('overall_score', results)
        self.assertIn('acceptable', results)
        self.assertIn('recommendations', results)
        
        # Verify that the overall score is a float between 0 and 1
        self.assertIsInstance(results['overall_score'], float)
        self.assertGreaterEqual(results['overall_score'], 0.0)
        self.assertLessEqual(results['overall_score'], 1.0)

if __name__ == '__main__':
    unittest.main()