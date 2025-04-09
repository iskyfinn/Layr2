# Layr - Architecture Analysis Platform

Layr is a web application designed to assist application owners, software engineers, architects, and Architecture Review Board (ARB) members throughout the application review process, from Permit to Initiate (PTI) to Permit to Operate (PTO).

## Features

- **HLDD Analysis**: Upload High Level Design Documents (HLDDs) for architectural analysis
- **Architecture Recommendations**: Receive recommendations on architecture based on use cases and requirements
- **Modernization Strategies**: Get suggestions for application modernization
- **Pattern Analysis**: Learn about patterns and anti-patterns relevant to your application
- **Cloud Provider Comparison**: Compare AWS, Azure, Oracle, and Google Cloud products
- **Diagram Generation**: Create architecture diagrams for documentation
- **HLDD Generation**: Automatically generate HLDDs based on user input
- **ARB Workflow**: Streamlined process for ARB reviews and voting

## System Requirements

- Python 3.9 or higher
- Flask 2.3.2
- SQL database (SQLite by default, can be configured for PostgreSQL, MySQL, etc.)
- Modern web browser

## Installation

1. Clone the repository:

```bash
git clone https://github.com/iskyfinn/Layr2.git
cd Layr2
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python run.py
```

The application will be available at http://localhost:5000

## Project Structure

- **app/**: Main application package
  - **__init__.py**: Application initialization
  - **config.py**: Configuration settings
  - **models/**: Database models
  - **services/**: Business logic and analysis tools
  - **routes/**: API endpoints and view functions
  - **templates/**: HTML templates
  - **static/**: CSS, JavaScript, and images
- **tests/**: Unit tests
- **run.py**: Application entry point
- **requirements.txt**: Dependencies

## Usage

1. **User Registration**: Create an account with appropriate role (Application Owner, Software Engineer, Architect, ARB Member)
2. **Create Application**: Define an application with use case, baseline systems, and requirements
3. **Upload or Generate HLDD**: Provide High Level Design Document for review
4. **Analysis**: Get architectural analysis, recommendations, and insights
5. **ARB Review**: ARB members can review and vote on applications
6. **Decision**: Applications receive final approval or rejection

## Key Components

### HLDD Analyzer

Evaluates architecture documents across key criteria:
- Security
- Scalability
- Reliability
- Maintainability
- Cost optimization
- Compliance

### Architecture Recommender

Recommends architecture patterns based on:
- Use case type
- Specific requirements
- Baseline systems
- Cloud compatibility

### Modernization Strategy

Provides recommendations for application modernization:
- Rehost (Lift and Shift)
- Replatform
- Refactor/Re-architect
- Rebuild
- Replace (Repurchase)

### Pattern Analyzer

Analyzes technology stacks for:
- Architecture patterns
- Anti-patterns
- Cloud provider compatibility

### Document and Diagram Generator

Creates documentation and visualizations:
- High Level Design Documents
- Architecture diagrams
- Deployment diagrams
- Data model diagrams
- Sequence diagrams

## Development

### Running Tests

```bash
python -m unittest discover tests
```

### Adding New Features

1. Create models in the `app/models/` directory
2. Implement business logic in the `app/services/` directory
3. Add routes in the `app/routes/` directory
4. Create templates in the `app/templates/` directory
5. Update static files as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask web framework
- Bootstrap for frontend styling
- Chart.js for data visualization
- Python libraries: docx, PyMuPDF, Pillow, etc.