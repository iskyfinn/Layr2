import os
import json
import re
import tempfile
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class DiagramGenerator:
    """
    Service for generating architecture diagrams based on system descriptions
    and requirements. This implementation is CPU-friendly, avoiding heavy
    dependencies like matplotlib or graphviz.
    """
    
    def __init__(self, output_dir=None):
        """Initialize the diagram generator"""
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Define standard colors for different components
        self.colors = {
            'component': '#ADD8E6',  # Light blue
            'database': '#90EE90',   # Light green
            'service': '#FFD700',    # Gold
            'external': '#D3D3D3',   # Light gray
            'user': '#FFA07A',       # Light salmon
            'background': '#FFFFFF', # White
            'line': '#000000',       # Black
            'text': '#000000',       # Black
            'border': '#000000',     # Black
            'highlight': '#FF4500'   # Orange red
        }
        
        # Define standard shapes/styles
        self.styles = {
            'component': 'rectangle',
            'database': 'cylinder',
            'service': 'rectangle_rounded',
            'external': 'cloud',
            'user': 'person',
            'connector': 'arrow'
        }
    
    def generate_system_architecture_diagram(self, components, connections, title="System Architecture"):
        """
        Generate a system architecture diagram
        
        Parameters:
        - components: List of component dictionaries (name, type, description)
        - connections: List of connection dictionaries (from, to, type, description)
        - title: Diagram title
        
        Returns:
        - Dict with diagram info including filename
        """
        try:
            # Generate unique filename
            file_name = self._sanitize_filename(f"{title}_diagram.png")
            
            if self.output_dir:
                file_path = os.path.join(self.output_dir, file_name)
            else:
                file_path = file_name
            
            # Create diagram
            image = self._create_architecture_diagram(components, connections, title)
            
            # Save image
            image.save(file_path)
            
            return {
                'file_name': file_name,
                'file_path': file_path,
                'width': image.width,
                'height': image.height,
                'success': True
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def generate_deployment_diagram(self, environments, components, title="Deployment Architecture"):
        """
        Generate a deployment diagram
        
        Parameters:
        - environments: List of environment dictionaries (name, components)
        - components: List of component dictionaries (name, type, env, host)
        - title: Diagram title
        
        Returns:
        - Dict with diagram info including filename
        """
        try:
            # Generate unique filename
            file_name = self._sanitize_filename(f"{title}_diagram.png")
            
            if self.output_dir:
                file_path = os.path.join(self.output_dir, file_name)
            else:
                file_path = file_name
            
            # Create diagram
            image = self._create_deployment_diagram(environments, components, title)
            
            # Save image
            image.save(file_path)
            
            return {
                'file_name': file_name,
                'file_path': file_path,
                'width': image.width,
                'height': image.height,
                'success': True
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def generate_sequence_diagram(self, sequence, title="Sequence Diagram"):
        """
        Generate a sequence diagram
        
        Parameters:
        - sequence: List of sequence step dictionaries (from, to, action, notes)
        - title: Diagram title
        
        Returns:
        - Dict with diagram info including filename
        """
        try:
            # Generate unique filename
            file_name = self._sanitize_filename(f"{title}_diagram.png")
            
            if self.output_dir:
                file_path = os.path.join(self.output_dir, file_name)
            else:
                file_path = file_name
            
            # Create diagram
            image = self._create_sequence_diagram(sequence, title)
            
            # Save image
            image.save(file_path)
            
            return {
                'file_name': file_name,
                'file_path': file_path,
                'width': image.width,
                'height': image.height,
                'success': True
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def generate_data_model_diagram(self, entities, relationships, title="Data Model"):
        """
        Generate a data model diagram
        
        Parameters:
        - entities: List of entity dictionaries (name, attributes)
        - relationships: List of relationship dictionaries (from, to, type)
        - title: Diagram title
        
        Returns:
        - Dict with diagram info including filename
        """
        try:
            # Generate unique filename
            file_name = self._sanitize_filename(f"{title}_diagram.png")
            
            if self.output_dir:
                file_path = os.path.join(self.output_dir, file_name)
            else:
                file_path = file_name
            
            # Create diagram
            image = self._create_data_model_diagram(entities, relationships, title)
            
            # Save image
            image.save(file_path)
            
            return {
                'file_name': file_name,
                'file_path': file_path,
                'width': image.width,
                'height': image.height,
                'success': True
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def generate_mermaid_diagram(self, mermaid_code, title="Diagram"):
        """
        Generate a diagram from Mermaid syntax.
        This returns the Mermaid code as text since this is a simpler alternative
        for document inclusion than trying to render the diagram directly.
        
        Parameters:
        - mermaid_code: String with Mermaid diagram code
        - title: Diagram title
        
        Returns:
        - Dict with diagram info including the mermaid code
        """
        try:
            # Generate unique filename (for potential future rendering)
            file_name = self._sanitize_filename(f"{title}_diagram.md")
            
            if self.output_dir:
                file_path = os.path.join(self.output_dir, file_name)
                
                # Save mermaid code to file
                with open(file_path, 'w') as f:
                    f.write(f"# {title}\n\n```mermaid\n{mermaid_code}\n```\n")
            else:
                file_path = file_name
            
            return {
                'file_name': file_name,
                'file_path': file_path,
                'mermaid_code': mermaid_code,
                'success': True
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _create_architecture_diagram(self, components, connections, title):
        """Create a system architecture diagram"""
        # Determine image size based on component count
        width = max(800, len(components) * 150)
        height = max(600, (len(components) // 3 + 1) * 200)
        
        # Create image with white background
        image = Image.new('RGB', (width, height), self.colors['background'])
        draw = ImageDraw.Draw(image)
        
        # Load or create font (fallback to default)
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
            component_font = ImageFont.truetype("arial.ttf", 14)
            connection_font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            title_font = ImageFont.load_default()
            component_font = ImageFont.load_default()
            connection_font = ImageFont.load_default()
        
        # Draw title
        draw.text((width//2 - len(title)*5, 20), title, font=title_font, fill=self.colors['text'])
        
        # Arrange components in a grid
        cols = min(4, len(components))
        rows = (len(components) + cols - 1) // cols
        
        cell_width = width // cols
        cell_height = (height - 60) // rows
        
        component_positions = {}
        
        for i, component in enumerate(components):
            row = i // cols
            col = i % cols
            
            x = col * cell_width + cell_width // 2
            y = row * cell_height + cell_height // 2 + 60  # Add 60px for title
            
            # Calculate component dimensions
            comp_width = min(150, cell_width - 20)
            comp_height = min(80, cell_height - 40)
            
            # Draw component based on type
            component_type = component.get('type', 'component')
            component_name = component.get('name', f'Component {i+1}')
            
            if component_type == 'database':
                # Draw a cylinder for database
                self._draw_cylinder(
                    draw, 
                    x - comp_width//2, y - comp_height//2, 
                    x + comp_width//2, y + comp_height//2, 
                    self.colors['database'], 
                    self.colors['border']
                )
            elif component_type == 'service':
                # Draw a rounded rectangle for service
                self._draw_rounded_rectangle(
                    draw, 
                    x - comp_width//2, y - comp_height//2, 
                    x + comp_width//2, y + comp_height//2, 
                    10, 
                    self.colors['service'], 
                    self.colors['border']
                )
            elif component_type == 'external':
                # Draw a cloud shape for external systems
                self._draw_cloud(
                    draw, 
                    x - comp_width//2, y - comp_height//2, 
                    x + comp_width//2, y + comp_height//2, 
                    self.colors['external'], 
                    self.colors['border']
                )
            elif component_type == 'user':
                # Draw a person shape for users
                self._draw_person(
                    draw, 
                    x - comp_width//2, y - comp_height//2, 
                    x + comp_width//2, y + comp_height//2, 
                    self.colors['user'], 
                    self.colors['border']
                )
            else:
                # Draw a rectangle for default components
                draw.rectangle(
                    [x - comp_width//2, y - comp_height//2, x + comp_width//2, y + comp_height//2], 
                    fill=self.colors['component'], 
                    outline=self.colors['border'], 
                    width=2
                )
            
            # Draw component name
            text_width = len(component_name) * 7
            if text_width > comp_width:
                # Split name into multiple lines if too long
                words = component_name.split()
                lines = []
                current_line = words[0]
                
                for word in words[1:]:
                    if len(current_line + " " + word) * 7 <= comp_width:
                        current_line += " " + word
                    else:
                        lines.append(current_line)
                        current_line = word
                
                lines.append(current_line)
                
                for j, line in enumerate(lines):
                    line_y = y - (len(lines) - 1) * 10 + j * 20
                    draw.text((x - len(line)*3.5, line_y), line, font=component_font, fill=self.colors['text'])
            else:
                draw.text((x - text_width//2, y - 7), component_name, font=component_font, fill=self.colors['text'])
            
            # Store component position for connections
            component_positions[component_name] = (x, y)
        
        # Draw connections
        for connection in connections:
            from_comp = connection.get('from')
            to_comp = connection.get('to')
            conn_type = connection.get('type', 'default')
            description = connection.get('description', '')
            
            if from_comp in component_positions and to_comp in component_positions:
                start_x, start_y = component_positions[from_comp]
                end_x, end_y = component_positions[to_comp]
                
                # Calculate connection points
                # Draw arrow
                if conn_type == 'bidirectional':
                    self._draw_bidirectional_arrow(draw, start_x, start_y, end_x, end_y, self.colors['line'])
                else:
                    self._draw_arrow(draw, start_x, start_y, end_x, end_y, self.colors['line'])
                
                # Draw description at midpoint
                if description:
                    mid_x = (start_x + end_x) // 2
                    mid_y = (start_y + end_y) // 2
                    
                    # Adjust text position to avoid overlapping the line
                    offset = 15
                    if abs(end_y - start_y) < abs(end_x - start_x):  # More horizontal
                        mid_y += offset
                    else:  # More vertical
                        mid_x += offset
                    
                    draw.text((mid_x - len(description)*3, mid_y), description, font=connection_font, fill=self.colors['text'])
        
        return image
    
    def _create_deployment_diagram(self, environments, components, title):
        """Create a deployment diagram"""
        # Calculate image dimensions
        width = max(800, len(environments) * 250)
        height = max(600, len(components) * 60 + 100)
        
        # Create image with white background
        image = Image.new('RGB', (width, height), self.colors['background'])
        draw = ImageDraw.Draw(image)
        
        # Load or create font (fallback to default)
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
            env_font = ImageFont.truetype("arial.ttf", 16)
            component_font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            title_font = ImageFont.load_default()
            env_font = ImageFont.load_default()
            component_font = ImageFont.load_default()
        
        # Draw title
        draw.text((width//2 - len(title)*5, 20), title, font=title_font, fill=self.colors['text'])
        
        # Draw environments
        env_width = (width - 40) // len(environments)
        env_padding = 20
        
        env_components = {}
        for component in components:
            env_name = component.get('env', 'Default')
            if env_name not in env_components:
                env_components[env_name] = []
            env_components[env_name].append(component)
        
        for i, env in enumerate(environments):
            env_name = env.get('name', f'Environment {i+1}')
            
            # Calculate environment rectangle
            env_x1 = i * env_width + env_padding
            env_y1 = 60
            env_x2 = (i + 1) * env_width - env_padding
            env_y2 = height - 20
            
            # Draw environment box
            draw.rectangle([env_x1, env_y1, env_x2, env_y2], outline=self.colors['border'], width=2)
            
            # Draw environment name
            draw.text((env_x1 + 10, env_y1 + 10), env_name, font=env_font, fill=self.colors['text'])
            
            # Draw components in this environment
            components_in_env = env_components.get(env_name, [])
            
            for j, component in enumerate(components_in_env):
                comp_name = component.get('name', f'Component {j+1}')
                comp_type = component.get('type', 'component')
                host = component.get('host', 'Server')
                
                # Calculate component position
                comp_height = 50
                comp_width = env_width - 2 * env_padding - 20
                
                comp_x1 = env_x1 + env_padding
                comp_y1 = env_y1 + 50 + j * (comp_height + 10)
                comp_x2 = comp_x1 + comp_width
                comp_y2 = comp_y1 + comp_height
                
                # Draw component based on type
                if comp_type == 'database':
                    self._draw_cylinder(draw, comp_x1, comp_y1, comp_x2, comp_y2, self.colors['database'], self.colors['border'])
                elif comp_type == 'service':
                    self._draw_rounded_rectangle(draw, comp_x1, comp_y1, comp_x2, comp_y2, 10, self.colors['service'], self.colors['border'])
                elif comp_type == 'external':
                    self._draw_cloud(draw, comp_x1, comp_y1, comp_x2, comp_y2, self.colors['external'], self.colors['border'])
                else:
                    draw.rectangle([comp_x1, comp_y1, comp_x2, comp_y2], fill=self.colors['component'], outline=self.colors['border'], width=2)
                
                # Draw component name
                name_x = comp_x1 + 10
                name_y = comp_y1 + 5
                draw.text((name_x, name_y), comp_name, font=component_font, fill=self.colors['text'])
                
                # Draw host name if different from component
                if host and host != comp_name:
                    host_x = comp_x1 + 10
                    host_y = comp_y1 + 25
                    draw.text((host_x, host_y), f"Host: {host}", font=component_font, fill=self.colors['text'])
        
        return image
    from PIL import Image, ImageDraw, ImageFont
import io
import logging

def get_diagram_generator():
    """
    Initialize and return a diagram generator
    
    Returns:
        dict: A dictionary containing diagram generation methods
    """
    try:
        return {
            'generate_system_diagram': generate_system_diagram,
            'generate_component_diagram': generate_component_diagram,
            'generate_deployment_diagram': generate_deployment_diagram
        }
    except Exception as e:
        logging.error(f"Error initializing diagram generator: {e}")
        return {}

def generate_system_diagram(components, connections):
    """
    Generate a system diagram based on components and connections
    
    Args:
        components (list): List of system components
        connections (list): List of connections between components
    
    Returns:
        bytes: Image bytes of the generated diagram
    """
    try:
        # Create a new image with a white background
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font = ImageFont.load_default()
        
        # Draw components
        for i, component in enumerate(components):
            x = (i % 4) * 200 + 50
            y = (i // 4) * 150 + 50
            draw.rectangle([x, y, x+150, y+100], outline='black')
            draw.text((x+10, y+10), component['name'], fill='black', font=font)
        
        # Draw basic connections (simplified)
        for connection in connections:
            # This is a very basic connection drawing
            draw.line([(100, 100), (700, 500)], fill='gray', width=2)
        
        # Save image to a bytes buffer
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    except Exception as e:
        logging.error(f"Error generating system diagram: {e}")
        return None

def generate_component_diagram(components):
    """
    Generate a component diagram
    
    Args:
        components (list): List of components
    
    Returns:
        bytes: Image bytes of the generated diagram
    """
    try:
        # Similar to system diagram, but focused on components
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font = ImageFont.load_default()
        
        # Draw components
        for i, component in enumerate(components):
            x = (i % 4) * 200 + 50
            y = (i // 4) * 150 + 50
            draw.rectangle([x, y, x+150, y+100], outline='black')
            draw.text((x+10, y+10), component.get('name', 'Component'), fill='black', font=font)
            draw.text((x+10, y+30), component.get('type', 'Type'), fill='gray', font=font)
        
        # Save image to a bytes buffer
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    except Exception as e:
        logging.error(f"Error generating component diagram: {e}")
        return None

def generate_deployment_diagram(environments, components):
    """
    Generate a deployment diagram
    
    Args:
        environments (list): List of deployment environments
        components (list): List of components deployed in environments
    
    Returns:
        bytes: Image bytes of the generated diagram
    """
    try:
        # Similar to other diagrams, but showing deployment contexts
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font = ImageFont.load_default()
        
        # Draw environments
        for i, env in enumerate(environments):
            x = 50
            y = i * 150 + 50
            draw.rectangle([x, y, x+700, y+100], outline='black', fill='lightgray')
            draw.text((x+10, y+10), env.get('name', 'Environment'), fill='black', font=font)
        
        # Save image to a bytes buffer
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    except Exception as e:
        logging.error(f"Error generating deployment diagram: {e}")
        return None
    def _create_sequence_diagram(self, sequence, title):
        """Create a sequence diagram"""
        # Extract all unique actors from the sequence
        actors = []
        for step in sequence:
            from_actor = step.get('from')
            to_actor = step.get('to')
            
            if from_actor and from_actor not in actors:
                actors.append(from_actor)
            
            if to_actor and to_actor not in actors:
                actors.append(to_actor)
        
        # Calculate image dimensions
        actor_spacing = 150
        width = max(800, len(actors) * actor_spacing + 100)
        height = max(600, len(sequence) * 60 + 200)
        
        # Create image with white background
        image = Image.new('RGB', (width, height), self.colors['background'])
        draw = ImageDraw.Draw(image)
        
        # Load or create font (fallback to default)
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
            actor_font = ImageFont.truetype("arial.ttf", 14)
            message_font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            title_font = ImageFont.load_default()
            actor_font = ImageFont.load_default()
            message_font = ImageFont.load_default()
        
        # Draw title
        draw.text((width//2 - len(title)*5, 20), title, font=title_font, fill=self.colors['text'])
        
        # Draw actors at the top
        actor_positions = {}
        for i, actor in enumerate(actors):
            x = (i + 1) * actor_spacing
            y = 80
            
            # Draw actor box
            actor_width = len(actor) * 10 + 20
            actor_height = 40
            
            draw.rectangle(
                [x - actor_width//2, y - actor_height//2, x + actor_width//2, y + actor_height//2],
                fill=self.colors['component'],
                outline=self.colors['border'],
                width=2
            )
            
            # Draw actor name
            draw.text((x - len(actor)*4, y - 7), actor, font=actor_font, fill=self.colors['text'])
            
            # Store actor position
            actor_positions[actor] = x
            
            # Draw lifeline (dashed vertical line)
            for dash_y in range(y + actor_height//2, height - 20, 10):
                draw.line([x, dash_y, x, dash_y + 5], fill=self.colors['line'], width=1)
        
        # Draw sequence steps
        step_y = 150
        for step in sequence:
            from_actor = step.get('from')
            to_actor = step.get('to')
            action = step.get('action', '')
            notes = step.get('notes', '')
            
            if from_actor in actor_positions and to_actor in actor_positions:
                from_x = actor_positions[from_actor]
                to_x = actor_positions[to_actor]
                
                # Draw arrow
                if from_actor == to_actor:
                    # Self-call (loopback arrow)
                    loop_width = 40
                    draw.line([from_x, step_y, from_x + loop_width, step_y], fill=self.colors['line'], width=1)
                    draw.line([from_x + loop_width, step_y, from_x + loop_width, step_y + 20], fill=self.colors['line'], width=1)
                    draw.line([from_x + loop_width, step_y + 20, from_x, step_y + 20], fill=self.colors['line'], width=1)
                    
                    # Arrow tip
                    self._draw_arrow_tip(draw, from_x, step_y + 20, from_x + 5, step_y + 20, self.colors['line'])
                    
                    # Message text
                    draw.text((from_x + loop_width + 10, step_y), action, font=message_font, fill=self.colors['text'])
                else:
                    # Draw arrow between actors
                    draw.line([from_x, step_y, to_x, step_y], fill=self.colors['line'], width=1)
                    
                    # Arrow tip
                    if from_x < to_x:
                        self._draw_arrow_tip(draw, to_x - 10, step_y, to_x, step_y, self.colors['line'])
                    else:
                        self._draw_arrow_tip(draw, to_x + 10, step_y, to_x, step_y, self.colors['line'])
                    
                    # Message text
                    mid_x = (from_x + to_x) // 2
                    draw.text((mid_x - len(action)*3, step_y - 15), action, font=message_font, fill=self.colors['text'])
                
                # Draw notes if any
                if notes:
                    note_y = step_y + 25
                    note_width = len(notes) * 5 + 20
                    note_height = 30
                    note_x = max(from_x, to_x) + 50
                    
                    # Note box with folded corner
                    self._draw_note(draw, note_x, note_y, note_x + note_width, note_y + note_height, self.colors['external'], self.colors['border'])
                    
                    # Note text
                    draw.text((note_x + 10, note_y + 10), notes, font=message_font, fill=self.colors['text'])
                    
                    # Increase step_y to account for note
                    step_y += note_height + 10
                
                # Move to next step
                step_y += 40
        
        return image
    
    def _create_data_model_diagram(self, entities, relationships, title):
        """Create a data model diagram"""
        # Calculate image dimensions based on entity count
        cols = min(4, len(entities))
        rows = (len(entities) + cols - 1) // cols
        
        width = max(800, cols * 200 + 100)
        height = max(600, rows * 250 + 100)
        
        # Create image with white background
        image = Image.new('RGB', (width, height), self.colors['background'])
        draw = ImageDraw.Draw(image)
        
        # Load or create font (fallback to default)
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
            entity_font = ImageFont.truetype("arial.ttf", 14)
            attribute_font = ImageFont.truetype("arial.ttf", 12)
            relationship_font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            title_font = ImageFont.load_default()
            entity_font = ImageFont.load_default()
            attribute_font = ImageFont.load_default()
            relationship_font = ImageFont.load_default()
        
        # Draw title
        draw.text((width//2 - len(title)*5, 20), title, font=title_font, fill=self.colors['text'])
        
        # Arrange entities in a grid and draw them
        cell_width = width // cols
        cell_height = (height - 60) // rows
        
        entity_positions = {}
        
        for i, entity in enumerate(entities):
            row = i // cols
            col = i % cols
            
            entity_name = entity.get('name', f'Entity{i+1}')
            attributes = entity.get('attributes', [])
            
            # Calculate entity box dimensions
            box_width = 180
            box_height = max(80, 30 + len(attributes) * 20)
            
            x = col * cell_width + cell_width // 2
            y = row * cell_height + 100 + box_height // 2
            
            # Draw entity box
            draw.rectangle(
                [x - box_width//2, y - box_height//2, x + box_width//2, y + box_height//2],
                fill=self.colors['component'],
                outline=self.colors['border'],
                width=2
            )
            
            # Draw entity name section
            name_section_height = 30
            draw.line(
                [x - box_width//2, y - box_height//2 + name_section_height, x + box_width//2, y - box_height//2 + name_section_height],
                fill=self.colors['border'],
                width=2
            )
            
            # Draw entity name
            draw.text(
                (x - len(entity_name)*4, y - box_height//2 + 10),
                entity_name,
                font=entity_font,
                fill=self.colors['text']
            )
            
            # Draw attributes
            for j, attr in enumerate(attributes):
                attr_name = attr.get('name', f'attribute{j}')
                attr_type = attr.get('type', '')
                is_key = attr.get('key', False)
                
                # Format attribute text
                if attr_type:
                    attr_text = f"{attr_name}: {attr_type}"
                else:
                    attr_text = attr_name
                
                if is_key:
                    attr_text = "PK " + attr_text
                
                # Draw attribute
                attr_y = y - box_height//2 + name_section_height + 10 + j * 20
                draw.text(
                    (x - box_width//2 + 10, attr_y),
                    attr_text,
                    font=attribute_font,
                    fill=self.colors['text']
                )
            
            # Store entity position for relationships
            entity_positions[entity_name] = (x, y)
        
        # Draw relationships
        for rel in relationships:
            from_entity = rel.get('from')
            to_entity = rel.get('to')
            rel_type = rel.get('type', '1:N')  # Default to one-to-many
            
            if from_entity in entity_positions and to_entity in entity_positions:
                from_x, from_y = entity_positions[from_entity]
                to_x, to_y = entity_positions[to_entity]
                
                # Draw relationship line
                draw.line([from_x, from_y, to_x, to_y], fill=self.colors['line'], width=1)
                
                # Draw relationship type at midpoint
                mid_x = (from_x + to_x) // 2
                mid_y = (from_y + to_y) // 2
                
                draw.text(
                    (mid_x - len(rel_type)*3, mid_y - 10),
                    rel_type,
                    font=relationship_font,
                    fill=self.colors['text']
                )
                
                # Draw cardinality symbols
                # For simplicity, just draw text indicators
                if '1:1' in rel_type:
                    # One-to-one
                    self._draw_one_symbol(draw, from_x, from_y, to_x, to_y, 20, self.colors['line'])
                    self._draw_one_symbol(draw, to_x, to_y, from_x, from_y, 20, self.colors['line'])
                elif '1:N' in rel_type:
                    # One-to-many
                    self._draw_one_symbol(draw, from_x, from_y, to_x, to_y, 20, self.colors['line'])
                    self._draw_many_symbol(draw, to_x, to_y, from_x, from_y, 20, self.colors['line'])
                elif 'N:M' in rel_type:
                    # Many-to-many
                    self._draw_many_symbol(draw, from_x, from_y, to_x, to_y, 20, self.colors['line'])
                    self._draw_many_symbol(draw, to_x, to_y, from_x, from_y, 20, self.colors['line'])
        
        return image
    
    def _sanitize_filename(self, filename):
        """Sanitize filename to ensure it's valid"""
        # Replace invalid characters
        return re.sub(r'[\\/*?:"<>|]', "_", filename)
    
    # Drawing utility functions
    def _draw_arrow(self, draw, x1, y1, x2, y2, color):
        """Draw an arrow from (x1,y1) to (x2,y2)"""
        # Draw line
        draw.line([x1, y1, x2, y2], fill=color, width=1)
        
        # Draw arrowhead
        self._draw_arrow_tip(draw, x2, y2, x1, y1, color)
    
    def _draw_arrow_tip(self, draw, x1, y1, x2, y2, color):
        """Draw an arrow tip at (x1,y1) coming from direction (x2,y2)"""
        # Calculate arrow direction
        length = 10.0
        dx = x1 - x2
        dy = y1 - y2
        
        # Normalize
        distance = (dx**2 + dy**2)**0.5
        if distance == 0:
            return
        
        dx = dx / distance
        dy = dy / distance
        
        # Calculate perpendicular direction
        pdx = -dy
        pdy = dx
        
        # Draw arrowhead
        x_left = int(x1 - length * dx + length/2 * pdx)
        y_left = int(y1 - length * dy + length/2 * pdy)
        
        x_right = int(x1 - length * dx - length/2 * pdx)
        y_right = int(y1 - length * dy - length/2 * pdy)
        
        draw.polygon([x1, y1, x_left, y_left, x_right, y_right], fill=color)
    
    def _draw_bidirectional_arrow(self, draw, x1, y1, x2, y2, color):
        """Draw a bidirectional arrow between (x1,y1) and (x2,y2)"""
        # Draw line
        draw.line([x1, y1, x2, y2], fill=color, width=1)
        
        # Draw arrowheads at both ends
        self._draw_arrow_tip(draw, x2, y2, x1, y1, color)
        self._draw_arrow_tip(draw, x1, y1, x2, y2, color)
    
    def _draw_cylinder(self, draw, x1, y1, x2, y2, fill_color, outline_color):
        """Draw a cylinder shape for databases"""
        width = x2 - x1
        height = y2 - y1
        ellipse_height = min(height // 3, 15)
        
        # Draw main rectangle
        draw.rectangle([x1, y1 + ellipse_height//2, x2, y2 - ellipse_height//2], fill=fill_color, outline=outline_color, width=2)
        
        # Draw top ellipse
        draw.ellipse([x1, y1, x2, y1 + ellipse_height], fill=fill_color, outline=outline_color, width=2)
        
        # Draw bottom ellipse
        draw.ellipse([x1, y2 - ellipse_height, x2, y2], fill=fill_color, outline=outline_color, width=2)
        
        # Draw ellipse arc at the bottom for 3D effect
        draw.arc([x1, y2 - ellipse_height, x2, y2], 0, 180, fill=outline_color, width=2)
    
    def _draw_rounded_rectangle(self, draw, x1, y1, x2, y2, radius, fill_color, outline_color):
        """Draw a rectangle with rounded corners"""
        # Draw main rectangle
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill_color, outline=fill_color)
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill_color, outline=fill_color)
        
        # Draw corners
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill_color, outline=fill_color)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill_color, outline=fill_color)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill_color, outline=fill_color)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill_color, outline=fill_color)
        
        # Draw outline
        draw.arc([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=outline_color, width=2)
        draw.arc([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=outline_color, width=2)
        draw.arc([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=outline_color, width=2)
        draw.arc([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=outline_color, width=2)
        draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline_color, width=2)
        draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline_color, width=2)
        draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline_color, width=2)
        draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline_color, width=2)
    
    def _draw_cloud(self, draw, x1, y1, x2, y2, fill_color, outline_color):
        """Draw a simple cloud shape for external systems"""
        width = x2 - x1
        height = y2 - y1
        
        # Calculate cloud bubbles
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        radius1 = min(width, height) // 3
        radius2 = min(width, height) // 4
        
        # Draw cloud shape using overlapping circles
        draw.ellipse([cx - radius1, cy - radius1, cx + radius1, cy + radius1], fill=fill_color)
        draw.ellipse([x1 + radius2, cy - radius2, x1 + radius2*3, cy + radius2], fill=fill_color)
        draw.ellipse([x2 - radius2*3, cy - radius2, x2 - radius2, cy + radius2], fill=fill_color)
        draw.ellipse([cx - radius2, y1 + radius2, cx + radius2, y1 + radius2*3], fill=fill_color)
        draw.ellipse([cx - radius2, y2 - radius2*3, cx + radius2, y2 - radius2], fill=fill_color)
        
        # Draw outline (simplified)
        draw.arc([cx - radius1, cy - radius1, cx + radius1, cy + radius1], 0, 360, fill=outline_color, width=2)
    
    def _draw_person(self, draw, x1, y1, x2, y2, fill_color, outline_color):
        """Draw a person shape for user components"""
        width = x2 - x1
        height = y2 - y1
        
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        
        head_radius = min(width, height) // 4
        
        # Draw head
        draw.ellipse([cx - head_radius, y1 + head_radius, cx + head_radius, y1 + head_radius*3], 
                     fill=fill_color, outline=outline_color, width=2)
        
        # Draw body
        body_top = y1 + head_radius*3
        body_width = head_radius*2
        
        # Torso
        draw.polygon([cx, body_top, cx - body_width, y2, cx + body_width, y2], 
                     fill=fill_color, outline=outline_color, width=2)
        
        # Arms
        draw.line([cx - body_width//2, body_top + head_radius, cx + body_width//2, body_top + head_radius],
                 fill=outline_color, width=2)
    
    def _draw_note(self, draw, x1, y1, x2, y2, fill_color, outline_color):
        """Draw a note shape with folded corner"""
        fold_size = min((x2 - x1) // 4, (y2 - y1) // 4, 20)
        
        # Draw main rectangle
        draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=outline_color, width=2)
        
        # Draw folded corner
        draw.polygon([x2 - fold_size, y1, x2, y1 + fold_size, x2, y1], 
                     fill=self.colors['background'], outline=outline_color, width=2)
        
        # Draw fold line
        draw.line([x2 - fold_size, y1, x2 - fold_size, y1 + fold_size, x2, y1 + fold_size],
                 fill=outline_color, width=2)
    
    def _draw_one_symbol(self, draw, x1, y1, x2, y2, distance, color):
        """Draw a '1' cardinality symbol near (x1,y1) in the direction of (x2,y2)"""
        # Calculate direction vector
        dx = x2 - x1
        dy = y2 - y1
        
        # Normalize
        length = (dx**2 + dy**2)**0.5
        if length == 0:
            return
        
        dx = dx / length
        dy = dy / length
        
        # Calculate position
        pos_x = int(x1 + dx * distance)
        pos_y = int(y1 + dy * distance)
        
        # Draw '1' symbol
        draw.text((pos_x - 3, pos_y - 6), "1", fill=color)
    
    def _draw_many_symbol(self, draw, x1, y1, x2, y2, distance, color):
        """Draw a 'many' cardinality symbol near (x1,y1) in the direction of (x2,y2)"""
        # Calculate direction vector
        dx = x2 - x1
        dy = y2 - y1
        
        # Normalize
        length = (dx**2 + dy**2)**0.5
        if length == 0:
            return
        
        dx = dx / length
        dy = dy / length
        
        # Calculate position
        pos_x = int(x1 + dx * distance)
        pos_y = int(y1 + dy * distance)
        
        # Draw 'N' symbol (or '*' for many)
        draw.text((pos_x - 3, pos_y - 6), "N", fill=color)


def get_diagram_generator(output_dir=None, cpu_optimized=True):
    """Factory function to get an instance of the Diagram Generator"""
    return DiagramGenerator(output_dir)