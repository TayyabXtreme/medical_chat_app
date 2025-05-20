import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIProcessor:
    def __init__(self, api_key=None):
        # Set API key from environment variable or parameter
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            print("Warning: No Gemini API key provided")
    
    def generate_response(self, user_message, detected_symptoms, diagnoses):
        """Generate a natural language response using Gemini"""
        if not self.api_key:
            return self._generate_fallback_response(detected_symptoms, diagnoses)
        
        try:
            # Prepare system prompt with medical disclaimer
            system_prompt = """
            You are a medical chatbot assistant designed to provide general health information.
            Important disclaimers:
            1. You are not a licensed medical professional.
            2. Your responses are for informational purposes only and do not constitute medical advice.
            3. Always advise users to consult with a healthcare professional for proper diagnosis and treatment.
            
            Based on the user's message and the symptoms and potential diagnoses detected, 
            provide a helpful, informative response that:
            1. Acknowledges the symptoms they've described
            2. Provides general information about possible conditions
            3. Offers general self-care tips if appropriate
            4. Always emphasizes the importance of consulting a healthcare professional
            5. Never make definitive diagnoses or prescribe treatments
            """
            
            # Prepare context for the model
            context = {
                "detected_symptoms": detected_symptoms,
                "possible_diagnoses": diagnoses
            }
            
            # Configure the model
            model = genai.GenerativeModel('gemini-pro')
            
            # Create the prompt with system instructions, user message and context
            full_prompt = f"{system_prompt}\n\nUser message: {user_message}\n\nAdditional context: {json.dumps(context)}"
            
            # Generate response
            response = model.generate_content(full_prompt)
            
            return response.text
            
        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            return self._generate_fallback_response(detected_symptoms, diagnoses)
    
    def _generate_fallback_response(self, detected_symptoms, diagnoses):
        """Generate a fallback response without using Gemini"""
        response = "I've analyzed your symptoms"
        
        if detected_symptoms:
            response += f" including {', '.join(detected_symptoms)}"
        
        if diagnoses:
            response += ".\n\nBased on this information, here are some possible conditions to consider:\n"
            for i, diagnosis in enumerate(diagnoses[:3], 1):
                response += f"\n{i}. {diagnosis['disease']} (confidence: {diagnosis['confidence']}%)\n"
                response += f"   {diagnosis['description']}\n"
                response += f"   General treatment approach: {diagnosis['treatment']}\n"
        else:
            response += ", but I couldn't determine any specific conditions based on the information provided."
        
        response += "\n\nIMPORTANT: This is not a medical diagnosis. Please consult with a healthcare professional for proper evaluation and treatment."
        
        return response
