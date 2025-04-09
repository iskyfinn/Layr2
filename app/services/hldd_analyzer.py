import os
import re
import docx
import fitz  # PyMuPDF
import pandas as pd
import numpy as np
from app.config import Config

class HLDDAnalyzer:
    """
    Service for analyzing High Level Design Documents (HLDD) and evaluating
    architectural soundness
    """
    
    def __init__(self):
        self.criteria = {
            'security': {
                'weight': 0.25,
                'keywords': [
                    'encryption', 'authentication', 'authorization', 
                    'identity', 'compliance', 'audit', 'security', 
                    'firewall', 'waf', 'ssl', 'tls', 'certificate'
                ]
            },
            'scalability': {
                'weight': 0.20,
                'keywords': [
                    'scaling', 'autoscale', 'load balancer', 'distributed', 
                    'partition', 'throughput', 'performance', 'capacity',
                    'kubernetes', 'containers', 'microservices'
                ]
            },
            'reliability': {
                'weight': 0.20,
                'keywords': [
                    'redundancy', 'failover', 'backup', 'recovery', 
                    'high availability', 'fault tolerance', 'resilience',
                    'sla', 'uptime', 'disaster recovery'
                ]
            },
            'maintainability': {
                'weight': 0.15,
                'keywords': [
                    'documentation', 'monitoring', 'logging', 'observability',
                    'ci/cd', 'pipeline', 'testing', 'version control',
                    'deployment', 'configuration management'
                ]
            },
            'cost_optimization': {
                'weight': 0.10,
                'keywords': [
                    'cost', 'budget', 'optimization', 'reserved', 
                    'spot instances', 'autoscaling', 'serverless',
                    'pay-as-you-go', 'rightsizing', 'lifecycle'
                ]
            },
            'compliance': {
                'weight': 0.10,
                'keywords': [
                    'gdpr', 'hipaa', 'pci', 'sox', 'fedramp', 'compliance',
                    'regulation', 'policy', 'audit', 'governance', 'data protection'
                ]
            }
        }
        
        # Required architecture components
        self.required_components = [
            'database', 'application server', 'networking', 'security', 
            'authentication', 'monitoring', 'backup', 'disaster recovery'
        ]
    
    def read_document(self, file_path):
        """Extract text content from various document formats"""
        _, file_extension = os.path.splitext(file_path)
        
        if file_extension.lower() == '.docx':
            return self._read_docx(file_path)
        elif file_extension.lower() == '.pdf':
            return self._read_pdf(file_path)
        elif file_extension.lower() in ['.txt', '.md']:
            return self._read_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _read_docx(self, file_path):
        """Extract text from DOCX file"""
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    
    def _read_pdf(self, file_path):
        """Extract text from PDF file"""
        doc = fitz.open(file_path)
        full_text = []
        for page in doc:
            full_text.append(page.get_text())
        return '\n'.join(full_text)
    
    def _read_text(self, file_path):
        """Read plain text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def analyze_document(self, file_path):
        """
        Analyze HLDD document and return architecture evaluation results
        """
        try:
            # Extract text from document
            document_text = self.read_document(file_path)
            
            # Run analysis
            results = {
                'scores': self._calculate_criteria_scores(document_text),
                'missing_components': self._identify_missing_components(document_text),
                'overall_score': 0,
                'acceptable': False,
                'recommendations': []
            }
            
            # Calculate overall weighted score
            overall_score = 0
            for criterion, data in results['scores'].items():
                overall_score += data['score'] * self.criteria[criterion]['weight']
            
            results['overall_score'] = round(overall_score, 2)
            results['acceptable'] = overall_score >= 0.7 and len(results['missing_components']) <= 1
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
            return results
        
        except Exception as e:
            return {
                'error': str(e),
                'scores': {},
                'missing_components': [],
                'overall_score': 0,
                'acceptable': False,
                'recommendations': ["Error analyzing document. Please check file format and try again."]
            }
    
    def _calculate_criteria_scores(self, text):
        """Calculate scores for each evaluation criterion"""
        text = text.lower()
        scores = {}
        
        for criterion, data in self.criteria.items():
            keyword_count = 0
            for keyword in data['keywords']:
                keyword_count += len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
            
            # Normalize score (0-1 range)
            max_expected_occurrences = len(data['keywords']) * 2
            normalized_score = min(1.0, keyword_count / max_expected_occurrences)
            
            scores[criterion] = {
                'score': round(normalized_score, 2),
                'keywords_found': keyword_count
            }
        
        return scores
    
    def _identify_missing_components(self, text):
        """Identify any required components missing from the architecture"""
        text = text.lower()
        missing_components = []
        
        for component in self.required_components:
            if re.search(r'\b' + re.escape(component) + r'\b', text) is None:
                missing_components.append(component)
        
        return missing_components
    
    def _generate_recommendations(self, results):
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Recommend addressing missing components
        if results['missing_components']:
            components_list = ', '.join(results['missing_components'])
            recommendations.append(
                f"Add details about the following components: {components_list}"
            )
        
        # Recommend improvements for low-scoring criteria
        for criterion, data in results['scores'].items():
            if data['score'] < 0.5:
                recommendations.append(
                    f"Enhance {criterion} details. Consider adding more information about " +
                    f"{', '.join(self.criteria[criterion]['keywords'][:3])}"
                )
        
        return recommendations


import docx
import fitz  # PyMuPDF
import pandas as pd
import os
import logging

def get_analyzer():
    """
    Initialize and return an HLDD analyzer
    
    Returns:
        dict: A dictionary containing analyzer configuration or methods
    """
    try:
        # Example minimal implementation
        return {
            'analyze_docx': analyze_docx,
            'analyze_pdf': analyze_pdf,
            'extract_text': extract_document_text,
            'analyze_csv': analyze_csv
        }
    except Exception as e:
        logging.error(f"Error initializing HLDD analyzer: {e}")
        return {}

def analyze_docx(file_path):
    """
    Analyze a Word document for HLDD content
    
    Args:
        file_path (str): Path to the Word document
    
    Returns:
        dict: Analysis results
    """
    try:
        # Basic document analysis
        doc = docx.Document(file_path)
        
        # Extract text from paragraphs
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        return {
            'success': True,
            'paragraphs': paragraphs,
            'paragraph_count': len(paragraphs)
        }
    except Exception as e:
        logging.error(f"Error analyzing DOCX document: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def analyze_pdf(file_path):
    """
    Analyze a PDF document for HLDD content
    
    Args:
        file_path (str): Path to the PDF document
    
    Returns:
        dict: Analysis results
    """
    try:
        # Open the PDF
        pdf_document = fitz.open(file_path)
        
        # Extract text from all pages
        text_pages = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text_pages.append(page.get_text())
        
        # Combine texts
        full_text = '\n'.join(text_pages)
        
        return {
            'success': True,
            'pages': text_pages,
            'page_count': len(text_pages),
            'total_text': full_text
        }
    except Exception as e:
        logging.error(f"Error analyzing PDF document: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def analyze_csv(file_path):
    """
    Analyze a CSV file using pandas
    
    Args:
        file_path (str): Path to the CSV file
    
    Returns:
        dict: Analysis results
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        return {
            'success': True,
            'columns': list(df.columns),
            'row_count': len(df),
            'column_count': len(df.columns),
            'summary': df.describe().to_dict()
        }
    except Exception as e:
        logging.error(f"Error analyzing CSV document: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def extract_document_text(file_path):
    """
    Extract full text from a document based on its extension
    
    Args:
        file_path (str): Path to the document
    
    Returns:
        str: Extracted text from the document
    """
    try:
        # Determine file type
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.docx':
            doc = docx.Document(file_path)
            full_text = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
        elif ext == '.pdf':
            pdf_document = fitz.open(file_path)
            text_pages = [page.get_text() for page in pdf_document]
            full_text = '\n'.join(text_pages)
        elif ext == '.csv':
            df = pd.read_csv(file_path)
            full_text = df.to_string()
        else:
            return f"Unsupported file type: {ext}"
        
        return full_text
    except Exception as e:
        logging.error(f"Error extracting document text: {e}")
        return ""