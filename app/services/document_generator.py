import os
import json
import datetime
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

class DocumentGenerator:
    """
    Service for generating High Level Design Documents (HLDDs) based on input
    from users
    """
    
    def __init__(self, output_dir=None):
        """Initialize the document generator"""
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
    
    def generate_hldd(self, application_info, tech_stack_info, architecture_info):
        """
        Generate a High Level Design Document (HLDD)
        
        Parameters:
        - application_info: Dict with application details
        - tech_stack_info: Dict with technology stack details
        - architecture_info: Dict with architecture details
        
        Returns:
        - Dict with document info including filename
        """
        try:
            app_name = application_info.get('name', 'Application')
            date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"{app_name.replace(' ', '_')}_HLDD_{date_str}.docx"
            
            if self.output_dir:
                file_path = os.path.join(self.output_dir, file_name)
            else:
                file_path = file_name
            
            # Generate document
            doc = self._create_document(application_info, tech_stack_info, architecture_info)
            
            # Save document
            doc.save(file_path)
            
            return {
                'file_name': file_name,
                'file_path': file_path,
                'success': True
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _create_document(self, application_info, tech_stack_info, architecture_info):
        """Create the HLDD document with proper formatting"""
        doc = Document()
        
        # Set up document styles
        self._setup_document_styles(doc)
        
        # Add document properties
        core_properties = doc.core_properties
        core_properties.title = f"{application_info.get('name', 'Application')} High Level Design Document"
        core_properties.subject = "Architecture Documentation"
        core_properties.creator = application_info.get('author', 'Layr')
        
        # Create cover page
        self._add_cover_page(doc, application_info)
        
        # Add table of contents
        self._add_toc(doc)
        
        # Add document sections
        self._add_introduction(doc, application_info)
        self._add_system_overview(doc, application_info)
        self._add_architecture_overview(doc, architecture_info)
        self._add_technology_stack(doc, tech_stack_info)
        self._add_data_architecture(doc, architecture_info.get('data_architecture', {}))
        self._add_security_architecture(doc, architecture_info.get('security', {}))
        self._add_deployment_architecture(doc, architecture_info.get('deployment', {}))
        self._add_operational_considerations(doc, architecture_info.get('operations', {}))
        self._add_appendices(doc, application_info)
        
        return doc
    
    def _setup_document_styles(self, doc):
        """Set up document styles for consistent formatting"""
        # Heading styles
        for i in range(1, 5):
            style = doc.styles[f'Heading {i}']
            font = style.font
            font.name = 'Calibri'
            font.size = Pt(20 - (i * 2))  # Decreasing sizes: 18, 16, 14, 12
            font.bold = True
            font.color.rgb = None  # Black
        
        # Normal text style
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)
        
        # Create a style for the TOC title
        toc_title_style = doc.styles.add_style('TOC Title', WD_STYLE_TYPE.PARAGRAPH)
        toc_title_font = toc_title_style.font
        toc_title_font.name = 'Calibri'
        toc_title_font.size = Pt(16)
        toc_title_font.bold = True
        
        # Create caption style
        caption_style = doc.styles.add_style('Caption', WD_STYLE_TYPE.PARAGRAPH)
        caption_font = caption_style.font
        caption_font.name = 'Calibri'
        caption_font.size = Pt(10)
        caption_font.italic = True
        
        paragraph_format = caption_style.paragraph_format
        paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def _add_cover_page(self, doc, application_info):
        """Add a cover page to the document"""
        # Add large title
        title_para = doc.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_para.add_run(f"{application_info.get('name', 'Application')}")
        title_run.font.size = Pt(24)
        title_run.font.bold = True
        
        # Add subtitle
        subtitle_para = doc.add_paragraph()
        subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle_run = subtitle_para.add_run("High Level Design Document")
        subtitle_run.font.size = Pt(18)
        subtitle_run.font.bold = True
        
        # Add version info
        doc.add_paragraph()  # Spacing
        version_para = doc.add_paragraph()
        version_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        version_para.add_run(f"Version: {application_info.get('version', '1.0')}")
        
        # Add date
        date_para = doc.add_paragraph()
        date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        date_para.add_run(f"Date: {datetime.datetime.now().strftime('%B %d, %Y')}")
        
        # Add author
        author_para = doc.add_paragraph()
        author_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        author_para.add_run(f"Author: {application_info.get('author', 'Architecture Team')}")
        
        # Add a page break
        doc.add_page_break()
    
    def _add_toc(self, doc):
        """Add table of contents"""
        toc_para = doc.add_paragraph()
        toc_para.style = 'TOC Title'
        toc_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        toc_run = toc_para.add_run("Table of Contents")
        
        doc.add_paragraph()  # Spacing
        
        # Insert TOC field code
        paragraph = doc.add_paragraph()
        run = paragraph.add_run()
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'begin')
        run._element.append(fldChar)
        
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = 'TOC \\o "1-3" \\h \\z \\u'  # TOC field code
        run._element.append(instrText)
        
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'separate')
        run._element.append(fldChar)
        
        fldChar = OxmlElement('w:t')
        fldChar.text = "Right-click to update table of contents."
        run._element.append(fldChar)
        
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'end')
        run._element.append(fldChar)
        
        # Add a page break
        doc.add_page_break()
    
    def _add_introduction(self, doc, application_info):
        """Add introduction section"""
        doc.add_heading('Introduction', level=1)
        
        doc.add_heading('Purpose', level=2)
        purpose_text = application_info.get('purpose', 'This High Level Design Document (HLDD) provides an overview of the system architecture.')
        doc.add_paragraph(purpose_text)
        
        doc.add_heading('Scope', level=2)
        scope_text = application_info.get('scope', 'This document describes the high-level design of the system including its components, interfaces, data structures, and technologies.')
        doc.add_paragraph(scope_text)
        
        doc.add_heading('Definitions, Acronyms, and Abbreviations', level=2)
        
        # Add a table for definitions
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        table.autofit = True
        
        # Add header row
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Term/Acronym'
        header_cells[1].text = 'Definition'
        
        # Make the header row bold
        for cell in header_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
        
        # Add definitions
        definitions = application_info.get('definitions', [
            {'term': 'HLDD', 'definition': 'High Level Design Document'},
            {'term': 'API', 'definition': 'Application Programming Interface'},
            {'term': 'DB', 'definition': 'Database'}
        ])
        
        for definition in definitions:
            row = table.add_row()
            row.cells[0].text = definition.get('term', '')
            row.cells[1].text = definition.get('definition', '')
    
    def _add_system_overview(self, doc, application_info):
        """Add system overview section"""
        doc.add_heading('System Overview', level=1)
        
        overview_text = application_info.get('overview', 'This section provides an overview of the system, its context, and its primary functions.')
        doc.add_paragraph(overview_text)
        
        doc.add_heading('System Context', level=2)
        context_text = application_info.get('context', 'This section describes the system context and its interactions with external systems and users.')
        doc.add_paragraph(context_text)
        
        doc.add_heading('System Functions', level=2)
        
        # Add functions as bullet points
        functions = application_info.get('functions', [
            'Function 1',
            'Function 2',
            'Function 3'
        ])
        
        for function in functions:
            p = doc.add_paragraph(style='List Bullet')
            p.add_run(function)
        
        doc.add_heading('User Roles', level=2)
        
        # Add user roles as a table
        roles = application_info.get('user_roles', [
            {'role': 'Administrator', 'description': 'System administrator with full access'},
            {'role': 'Application Owner', 'description': 'Owner responsible for the application'},
            {'role': 'Developer', 'description': 'Software engineer working on the application'},
            {'role': 'End User', 'description': 'User who interacts with the application'}
        ])
        
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        table.autofit = True
        
        # Add header row
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Role'
        header_cells[1].text = 'Description'
        
        # Make the header row bold
        for cell in header_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
        
        # Add roles
        for role in roles:
            row = table.add_row()
            row.cells[0].text = role.get('role', '')
            row.cells[1].text = role.get('description', '')
    
    def _add_architecture_overview(self, doc, architecture_info):
        """Add architecture overview section"""
        doc.add_heading('Architecture Overview', level=1)
        
        overview_text = architecture_info.get('overview', 'This section provides an overview of the system architecture including the primary components and their interactions.')
        doc.add_paragraph(overview_text)
        
        # Add architecture principles
        doc.add_heading('Architecture Principles', level=2)
        principles = architecture_info.get('principles', [
            'Scalability: The system should scale horizontally to handle increasing load',
            'Reliability: The system should be resilient to failures and maintain high availability',
            'Security: The system should implement defense in depth and follow security best practices',
            'Maintainability: The system should be easy to maintain and update'
        ])
        
        for principle in principles:
            p = doc.add_paragraph(style='List Bullet')
            p.add_run(principle)
        
        # Add architecture diagram placeholder
        doc.add_heading('Architecture Diagram', level=2)
        doc.add_paragraph('The following diagram illustrates the high-level architecture of the system:')
        
        # In a real scenario, you would insert an actual diagram here
        doc.add_paragraph('[Architecture Diagram Placeholder]')
        
        # Add component descriptions
        doc.add_heading('Component Descriptions', level=2)
        components = architecture_info.get('components', [
            {'name': 'Component 1', 'description': 'Description of component 1'},
            {'name': 'Component 2', 'description': 'Description of component 2'},
            {'name': 'Component 3', 'description': 'Description of component 3'}
        ])
        
        for component in components:
            doc.add_heading(component.get('name', 'Component'), level=3)
            doc.add_paragraph(component.get('description', 'Component description'))
    
    def _add_technology_stack(self, doc, tech_stack_info):
        """Add technology stack section"""
        doc.add_heading('Technology Stack', level=1)
        
        overview_text = tech_stack_info.get('overview', 'This section describes the technology stack used in the system.')
        doc.add_paragraph(overview_text)
        
        # Add technology categories
        categories = tech_stack_info.get('categories', [
            {
                'name': 'Frontend',
                'technologies': [
                    {'name': 'React', 'version': '18.x', 'purpose': 'UI framework'}
                ]
            },
            {
                'name': 'Backend',
                'technologies': [
                    {'name': 'Python', 'version': '3.9+', 'purpose': 'Server-side language'},
                    {'name': 'Flask', 'version': '2.x', 'purpose': 'Web framework'}
                ]
            },
            {
                'name': 'Database',
                'technologies': [
                    {'name': 'PostgreSQL', 'version': '14.x', 'purpose': 'Primary database'}
                ]
            },
            {
                'name': 'Infrastructure',
                'technologies': [
                    {'name': 'AWS', 'version': 'N/A', 'purpose': 'Cloud provider'},
                    {'name': 'Docker', 'version': 'Latest', 'purpose': 'Containerization'}
                ]
            }
        ])
        
        for category in categories:
            doc.add_heading(category.get('name', 'Category'), level=2)
            
            # Add technologies as a table
            table = doc.add_table(rows=1, cols=3)
            table.style = 'Table Grid'
            table.autofit = True
            
            # Add header row
            header_cells = table.rows[0].cells
            header_cells[0].text = 'Technology'
            header_cells[1].text = 'Version'
            header_cells[2].text = 'Purpose'
            
            # Make the header row bold
            for cell in header_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
            
            # Add technologies
            for tech in category.get('technologies', []):
                row = table.add_row()
                row.cells[0].text = tech.get('name', '')
                row.cells[1].text = tech.get('version', '')
                row.cells[2].text = tech.get('purpose', '')
    
    def _add_data_architecture(self, doc, data_architecture):
        """Add data architecture section"""
        doc.add_heading('Data Architecture', level=1)
        
        overview_text = data_architecture.get('overview', 'This section describes the data architecture of the system including data models, storage, and flows.')
        doc.add_paragraph(overview_text)
        
        # Add data stores
        doc.add_heading('Data Stores', level=2)
        data_stores = data_architecture.get('data_stores', [
            {'name': 'Primary Database', 'type': 'Relational', 'purpose': 'Main application data'},
            {'name': 'Cache', 'type': 'In-memory', 'purpose': 'Temporary data caching'}
        ])
        
        for store in data_stores:
            doc.add_heading(store.get('name', 'Data Store'), level=3)
            p = doc.add_paragraph()
            p.add_run('Type: ').bold = True
            p.add_run(store.get('type', 'N/A'))
            p.add_run('\nPurpose: ').bold = True
            p.add_run(store.get('purpose', 'N/A'))
        
        # Add data models
        doc.add_heading('Data Models', level=2)
        doc.add_paragraph('The following data models are used in the system:')
        
        # In a real scenario, you would include data model diagrams or descriptions
        doc.add_paragraph('[Data Model Diagram Placeholder]')
        
        # Add data flows
        doc.add_heading('Data Flows', level=2)
        doc.add_paragraph('The following diagram illustrates the data flows in the system:')
        
        # In a real scenario, you would include a data flow diagram
        doc.add_paragraph('[Data Flow Diagram Placeholder]')
    
    def _add_security_architecture(self, doc, security):
        """Add security architecture section"""
        doc.add_heading('Security Architecture', level=1)
        
        overview_text = security.get('overview', 'This section describes the security architecture of the system.')
        doc.add_paragraph(overview_text)
        
        # Add authentication and authorization
        doc.add_heading('Authentication and Authorization', level=2)
        auth_text = security.get('authentication', 'The system implements authentication and authorization mechanisms to ensure secure access to resources.')
        doc.add_paragraph(auth_text)
        
        # Add data protection
        doc.add_heading('Data Protection', level=2)
        data_protection_text = security.get('data_protection', 'The system implements measures to protect data at rest and in transit.')
        doc.add_paragraph(data_protection_text)
        
        # Add network security
        doc.add_heading('Network Security', level=2)
        network_security_text = security.get('network_security', 'The system implements network security measures to protect against threats.')
        doc.add_paragraph(network_security_text)
        
        # Add compliance
        doc.add_heading('Compliance', level=2)
        compliance_text = security.get('compliance', 'The system is designed to comply with relevant regulatory requirements.')
        doc.add_paragraph(compliance_text)
    
    def _add_deployment_architecture(self, doc, deployment):
        """Add deployment architecture section"""
        doc.add_heading('Deployment Architecture', level=1)
        
        overview_text = deployment.get('overview', 'This section describes the deployment architecture of the system.')
        doc.add_paragraph(overview_text)
        
        # Add deployment diagram placeholder
        doc.add_heading('Deployment Diagram', level=2)
        doc.add_paragraph('The following diagram illustrates the deployment architecture of the system:')
        
        # In a real scenario, you would insert an actual diagram here
        doc.add_paragraph('[Deployment Diagram Placeholder]')
        
        # Add environments
        doc.add_heading('Environments', level=2)
        environments = deployment.get('environments', [
            {'name': 'Development', 'description': 'Used for development and testing'},
            {'name': 'Staging', 'description': 'Used for integration testing and UAT'},
            {'name': 'Production', 'description': 'Used for the live system'}
        ])
        
        for env in environments:
            doc.add_heading(env.get('name', 'Environment'), level=3)
            doc.add_paragraph(env.get('description', 'Environment description'))
        
        # Add CI/CD
        doc.add_heading('CI/CD Pipeline', level=2)
        cicd_text = deployment.get('cicd', 'The system uses a CI/CD pipeline for automated testing and deployment.')
        doc.add_paragraph(cicd_text)
    
    def _add_operational_considerations(self, doc, operations):
        """Add operational considerations section"""
        doc.add_heading('Operational Considerations', level=1)
        
        overview_text = operations.get('overview', 'This section describes the operational considerations for the system.')
        doc.add_paragraph(overview_text)
        
        # Add monitoring and logging
        doc.add_heading('Monitoring and Logging', level=2)
        monitoring_text = operations.get('monitoring', 'The system implements monitoring and logging mechanisms to ensure operational visibility.')
        doc.add_paragraph(monitoring_text)
        
        # Add backup and recovery
        doc.add_heading('Backup and Recovery', level=2)
        backup_text = operations.get('backup', 'The system implements backup and recovery mechanisms to ensure data durability.')
        doc.add_paragraph(backup_text)
        
        # Add scaling and performance
        doc.add_heading('Scaling and Performance', level=2)
        scaling_text = operations.get('scaling', 'The system is designed to scale to handle increasing load and maintain performance.')
        doc.add_paragraph(scaling_text)
        
        # Add disaster recovery
        doc.add_heading('Disaster Recovery', level=2)
        dr_text = operations.get('disaster_recovery', 'The system implements disaster recovery measures to ensure business continuity.')
        doc.add_paragraph(dr_text)
    
    def _add_appendices(self, doc, application_info):
        """Add appendices section"""
        doc.add_heading('Appendices', level=1)
        
        # Add references
        doc.add_heading('References', level=2)
        references = application_info.get('references', [
            'Reference 1',
            'Reference 2',
            'Reference 3'
        ])
        
        for reference in references:
            p = doc.add_paragraph(style='List Bullet')
            p.add_run(reference)
        
        # Add revision history
        doc.add_heading('Revision History', level=2)
        
        # Add revision history as a table
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        table.autofit = True
        
        # Add header row
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Version'
        header_cells[1].text = 'Date'
        header_cells[2].text = 'Author'
        header_cells[3].text = 'Description'
        
        # Make the header row bold
        for cell in header_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
        
        # Add revision history entries
        revisions = application_info.get('revisions', [
            {
                'version': '1.0',
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'author': 'Architecture Team',
                'description': 'Initial version'
            }
        ])
        
        for revision in revisions:
            row = table.add_row()
            row.cells[0].text = revision.get('version', '')
            row.cells[1].text = revision.get('date', '')
            row.cells[2].text = revision.get('author', '')
            row.cells[3].text = revision.get('description', '')


def get_document_generator(output_dir=None):
    """Factory function to get an instance of the Document Generator"""
    return DocumentGenerator(output_dir)