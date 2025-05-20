from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from diagnosis_system import MedicalDiagnosisSystem
from openai_processor import OpenAIProcessor  # We'll keep the class name but it now uses Gemini
from database import create_db_connection, setup_database, populate_sample_data
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MedicalChatbot:
    def __init__(self, gemini_api_key=None):
        self.diagnosis_system = MedicalDiagnosisSystem()
        self.openai_processor = OpenAIProcessor(api_key=gemini_api_key)
    
    def process_message(self, user_id, message):
        """Process a user message and generate a response"""
        try:
            # Extract symptoms from message
            symptoms = self.diagnosis_system.nlp_processor.extract_symptoms(message)
            
            # Get possible diagnoses
            diagnoses = self.diagnosis_system.get_possible_diagnoses(symptoms)
            
            # Generate response
            response = self.openai_processor.generate_response(message, symptoms, diagnoses)
            
            # Save interaction to database
            try:
                self._save_interaction(user_id, message, response)
            except Exception as e:
                print(f"Error saving interaction: {e}")
            
            return {
                "response": response,
                "detected_symptoms": symptoms,
                "possible_diagnoses": diagnoses
            }
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                "response": "I'm sorry, I encountered an error while processing your message. Please try again.",
                "detected_symptoms": [],
                "possible_diagnoses": []
            }
    
    def _save_interaction(self, user_id, message, response):
        """Save the interaction to the database"""
        connection = create_db_connection()
        if connection is None:
            return
        
        cursor = connection.cursor()
        query = "INSERT INTO user_interactions (user_id, message, response) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, message, response))
        
        connection.commit()
        cursor.close()
        connection.close()


from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    """Serve the main chatbot interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chatbot interactions"""
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Use the global chatbot instance instead of creating a new one each time
    result = chatbot.process_message(user_id, message)
    
    return jsonify(result)

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """API endpoint to get all available symptoms"""
    connection = create_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection error"}), 500
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, name, description FROM symptoms")
    symptoms = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return jsonify(symptoms)

# Part 7: Setup and Run
def main():
    """Main function to set up and run the application"""
    print("Setting up medical chatbot system...")
    
    # Set up database
    setup_database()
    
    # Populate with sample data
    populate_sample_data()
    
    # Get API key from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    # Create a global chatbot instance with the API key
    global chatbot
    chatbot = MedicalChatbot(gemini_api_key=gemini_api_key)
    
    # Run Flask app
    print("Starting web server...")
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
