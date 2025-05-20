import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from database import create_db_connection

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class NLPProcessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text):
        """Preprocess text for NLP analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words
        ]
        
        return processed_tokens
    
    def extract_symptoms(self, text):
        """Extract potential symptoms from user input"""
        try:
            # Hardcoded symptoms for testing when database connection fails
            fallback_symptoms = ["fever", "cough", "headache", "fatigue", "sore throat", 
                                 "chest pain", "shortness of breath", "nausea"]
            
            all_symptoms = fallback_symptoms
            
            try:
                connection = create_db_connection()
                if connection is not None:
                    cursor = connection.cursor()
                    cursor.execute("SELECT name FROM symptoms")
                    all_symptoms = [symptom[0] for symptom in cursor.fetchall()]
                    cursor.close()
                    connection.close()
            except Exception as e:
                print(f"Error fetching symptoms from database: {e}")
            
            # Preprocess user input
            text_lower = text.lower()
            
            # Simple symptom matching with improved logic
            detected_symptoms = []
            
            # Add common symptoms that might be mentioned
            common_symptoms = {
                "fever": ["fever", "high temperature", "hot"],
                "cough": ["cough", "coughing"],
                "headache": ["headache", "head pain", "head ache"],
                "fatigue": ["fatigue", "tired", "exhausted", "tiredness"],
                "sore throat": ["sore throat", "throat pain", "throat ache"],
                "chest pain": ["chest pain", "pain in chest"],
                "shortness of breath": ["shortness of breath", "hard to breathe", "difficulty breathing"],
                "nausea": ["nausea", "feel sick", "feeling sick"],
                "cold": ["cold", "runny nose", "stuffy nose"],
                "flu": ["flu", "influenza", "flue"]
            }
            
            # Check for common symptoms in the text
            for symptom, aliases in common_symptoms.items():
                if any(alias in text_lower for alias in aliases):
                    detected_symptoms.append(symptom)
            
            # Also check database symptoms
            for symptom in all_symptoms:
                if symptom.lower() in text_lower and symptom not in detected_symptoms:
                    detected_symptoms.append(symptom)
            
            print(f"Detected symptoms: {detected_symptoms}")
            return detected_symptoms
        except Exception as e:
            print(f"Error in extract_symptoms: {e}")
            return []
