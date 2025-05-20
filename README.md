# Medical Chatbot

A web-based medical chatbot that uses natural language processing to identify symptoms, suggest possible diagnoses, and provide health information to users.

![Medical Chatbot Screenshot](screenshots/medical_chatbot.png)

## 1. Project Overview

### Purpose and Goals

The Medical Chatbot aims to provide accessible preliminary health information to users by:
- Identifying symptoms from natural language descriptions
- Suggesting possible medical conditions based on reported symptoms
- Providing general health information and self-care recommendations
- Emphasizing the importance of professional medical consultation

### Key Features

- **Natural Language Symptom Extraction**: Identifies health symptoms from conversational text
- **Symptom-Based Diagnosis**: Suggests potential conditions based on reported symptoms
- **Confidence Scoring**: Provides confidence levels for each suggested diagnosis
- **Responsive Web Interface**: Works across desktop and mobile devices
- **Dark/Light Mode**: User-selectable interface theme
- **Chat History**: Stores user interactions for continuity of care
- **Medical Disclaimers**: Clear communication of limitations and non-diagnostic nature

### Target Users and Use Cases

- **General Public**: Initial assessment of symptoms before seeking medical care
- **Remote Communities**: Basic health information where medical access is limited
- **Health-Conscious Individuals**: Educational tool for understanding symptoms and conditions
- **Healthcare Providers**: Supplementary tool for patient intake and education

## 2. Technical Architecture

### Web Framework: Flask

Flask was chosen for this project because:
- Lightweight and minimalist design perfect for API-based applications
- Easy integration with various Python libraries for NLP and data processing
- Simple routing system for creating RESTful endpoints
- Built-in development server for rapid prototyping
- Extensive documentation and community support

### Database: MySQL

MySQL was selected as the database system for:
- Relational structure ideal for modeling symptom-disease relationships
- Strong performance for read-heavy operations
- Robust transaction support for data integrity
- Widespread adoption and tooling support
- Scalability for future growth

### Libraries and Dependencies

| Library | Purpose |
|---------|---------|
| Flask | Web framework for serving the application |
| Flask-CORS | Handling Cross-Origin Resource Sharing |
| MySQL Connector | Database connectivity for Python |
| NLTK | Natural language processing for symptom extraction |
| Google Generative AI | Response generation using Gemini model |

### System Architecture

```
┌─────────────┐     ┌─────────────────────────────────┐     ┌─────────────┐
│             │     │                                 │     │             │
│  Web Client │◄────┤  Flask Web Server (app.py)     │◄────┤  MySQL DB   │
│  (Browser)  │     │                                 │     │             │
└─────────────┘     └─────────────────────────────────┘     └─────────────┘
                                    ▲                             ▲
                                    │                             │
                                    ▼                             │
                    ┌─────────────────────────────────┐          │
                    │                                 │          │
                    │  Diagnosis System               │──────────┘
                    │  (diagnosis_system.py)          │
                    │                                 │
                    └─────────────────────────────────┘
                                    ▲
                    ┌───────────────┴───────────────┐
                    │                               │
┌─────────────┐     │                               │     ┌─────────────┐
│             │     │                               │     │             │
│ NLP         │◄────┤                               ├────►│ Gemini API  │
│ Processor   │     │                               │     │ Integration │
│             │     │                               │     │             │
└─────────────┘     └───────────────────────────────┘     └─────────────┘
```

## 3. Database Design

### Schema

The database consists of four main tables:

**symptoms**
- `id`: Primary key
- `name`: Symptom name (e.g., "fever", "cough")
- `description`: Detailed description of the symptom

**diseases**
- `id`: Primary key
- `name`: Disease name (e.g., "Common Cold", "Influenza")
- `description`: Description of the disease
- `treatment`: General treatment approaches

**symptoms_diseases**
- `id`: Primary key
- `symptom_id`: Foreign key to symptoms table
- `disease_id`: Foreign key to diseases table
- `correlation_strength`: Float value (0-1) indicating strength of correlation

**user_interactions**
- `id`: Primary key
- `user_id`: Identifier for the user
- `message`: User's message
- `response`: System's response
- `timestamp`: When the interaction occurred

### Symptom-Disease Correlation

The system uses a weighted correlation model:
- Each symptom-disease pair has a correlation strength (0-1)
- Diagnoses are ranked by summing correlation strengths of matched symptoms
- Confidence scores are calculated using both correlation strength and symptom coverage

### Data Flow

1. User sends a message through the web interface
2. System extracts symptoms using NLP
3. Extracted symptoms are matched against the database
4. Potential diagnoses are retrieved based on symptom correlations
5. Response is generated and stored in user_interactions
6. Response with diagnoses is sent back to the user

## 4. Implementation Details

### NLP Processing Workflow

```python
def extract_symptoms(self, text):
    # Preprocess text (lowercase, tokenization)
    text_lower = text.lower()
    
    # Match against known symptoms using both:
    # 1. Direct keyword matching
    # 2. Synonym/alias matching
    
    detected_symptoms = []
    
    # Check for common symptoms and their aliases
    common_symptoms = {
        "fever": ["fever", "high temperature", "hot"],
        "cough": ["cough", "coughing"],
        # Additional symptoms and aliases...
    }
    
    for symptom, aliases in common_symptoms.items():
        if any(alias in text_lower for alias in aliases):
            detected_symptoms.append(symptom)
    
    # Also check database symptoms
    for symptom in all_symptoms:
        if symptom.lower() in text_lower and symptom not in detected_symptoms:
            detected_symptoms.append(symptom)
            
    return detected_symptoms
```

### Diagnosis Algorithm

The diagnosis algorithm works as follows:

1. Extract symptoms from user input
2. Query the database for diseases related to these symptoms
3. Calculate confidence scores based on:
   - Sum of correlation strengths between symptoms and diseases
   - Proportion of disease's typical symptoms that are present
4. Rank diagnoses by confidence score
5. Return top diagnoses with confidence percentages

```python
# Confidence calculation
symptom_coverage = matching / total if total > 0 else 0
confidence = (correlation * 0.7 + symptom_coverage * 0.3) * 100
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the main chatbot interface |
| `/api/chat` | POST | Processes user messages and returns responses |
| `/api/symptoms` | GET | Returns a list of all symptoms in the database |

## 5. Setup and Installation

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/TayyabXtreme/medical_chat_app.git
cd medical_chat_app
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
source venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up MySQL Database

1. Install MySQL if not already installed
2. Create a new database:
```sql
CREATE DATABASE medical_chatbot;
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=medical_chatbot
```

### Step 6: Initialize the Database

```bash
python setup_database.py
```

### Step 7: Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 6. Limitations and Future Improvements

### Current Limitations

- **Limited Symptom Recognition**: The system can only identify symptoms explicitly mentioned
- **No Contextual Understanding**: Cannot interpret symptoms in context (duration, severity, etc.)
- **Limited Medical Knowledge Base**: Database contains only a subset of common conditions
- **No Personalization**: Doesn't account for user's medical history or demographics
- **English-Only Support**: No multilingual capabilities

### Security Considerations

- **Data Encryption**: Implement end-to-end encryption for all medical data
- **User Authentication**: Add secure login system for persistent user profiles
- **HIPAA Compliance**: Additional measures needed for compliance with health data regulations
- **Regular Security Audits**: Implement scheduled security reviews

### Future Roadmap

- **Advanced NLP**: Implement more sophisticated symptom extraction using medical NLP models
- **Personalized Profiles**: Allow users to save medical history and preferences
- **Multilingual Support**: Add capability to process symptoms in multiple languages
- **Integration with Medical APIs**: Connect with medical knowledge bases for expanded information
- **Mobile Application**: Develop native mobile apps for improved accessibility
- **Voice Interface**: Add speech recognition for hands-free interaction

## 7. Ethical Considerations

### Medical Disclaimer

This system is designed for informational purposes only and does not provide medical advice, diagnosis, or treatment. The chatbot:

- Is not a substitute for professional medical advice
- Should not be used in emergency situations
- Cannot diagnose conditions with certainty
- Provides general information that may not apply to specific individuals

All users should be encouraged to consult with qualified healthcare providers for any medical concerns.

### Privacy Considerations

- User conversations may contain sensitive health information
- Data storage should comply with relevant health privacy regulations
- Users should be informed about data collection and usage
- Implement data minimization principles (only collect what's necessary)
- Provide options for users to delete their conversation history

### Responsible AI in Healthcare

- Regular monitoring for biases in diagnosis suggestions
- Transparency about AI limitations and confidence levels
- Clear communication of the system's non-diagnostic nature
- Continuous evaluation of accuracy and safety
- Expert medical review of knowledge base and algorithms

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NLTK team for natural language processing tools
- Google for Gemini API access
- Flask team for the web framework
- All contributors to the open-source libraries used in this project
