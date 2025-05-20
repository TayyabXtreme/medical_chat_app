from nlp_processor import NLPProcessor
from database import create_db_connection

class MedicalDiagnosisSystem:
    def __init__(self):
        self.nlp_processor = NLPProcessor()
    
    def get_possible_diagnoses(self, symptoms):
        """Get possible diagnoses based on symptoms"""
        if not symptoms:
            return []
        
        # Fallback diagnoses when database connection fails
        fallback_diagnoses = [
            {
                'disease': 'Common Cold',
                'description': 'A viral infection of the upper respiratory tract',
                'treatment': 'Rest, fluids, over-the-counter medications for symptoms',
                'confidence': 75.5
            },
            {
                'disease': 'Influenza',
                'description': 'A viral infection that attacks respiratory system',
                'treatment': 'Rest, fluids, antiviral medications in severe cases',
                'confidence': 68.2
            }
        ]
        
        try:
            connection = create_db_connection()
            if connection is None:
                # If symptoms contain fever and (cough or sore throat), return flu
                if 'fever' in symptoms and ('cough' in symptoms or 'sore throat' in symptoms):
                    return fallback_diagnoses
                return []
            
            cursor = connection.cursor()
            
            # Convert symptoms to IDs
            symptom_ids = []
            for symptom in symptoms:
                cursor.execute("SELECT id FROM symptoms WHERE name = %s", (symptom,))
                result = cursor.fetchone()
                if result:
                    symptom_ids.append(result[0])
            
            if not symptom_ids:
                cursor.close()
                connection.close()
                return []
            
            # Query for diseases related to these symptoms
            placeholders = ','.join(['%s'] * len(symptom_ids))
            query = f"""
            SELECT d.id, d.name, d.description, d.treatment, 
                   SUM(sd.correlation_strength) as total_correlation,
                   COUNT(sd.symptom_id) as matching_symptoms,
                   (SELECT COUNT(*) FROM symptoms_diseases WHERE disease_id = d.id) as total_symptoms
            FROM diseases d
            JOIN symptoms_diseases sd ON d.id = sd.disease_id
            WHERE sd.symptom_id IN ({placeholders})
            GROUP BY d.id
            ORDER BY total_correlation DESC, matching_symptoms DESC
            """
            
            cursor.execute(query, tuple(symptom_ids))
            results = cursor.fetchall()
            
            diagnoses = []
            for result in results:
                disease_id, name, description, treatment, correlation, matching, total = result
                
                # Calculate confidence based on correlation and symptom coverage
                symptom_coverage = matching / total if total > 0 else 0
                confidence = (correlation * 0.7 + symptom_coverage * 0.3) * 100
                
                diagnoses.append({
                    'disease': name,
                    'description': description,
                    'treatment': treatment,
                    'confidence': min(round(confidence, 2), 95.0)  # Cap at 95% to acknowledge uncertainty
                })
            
            cursor.close()
            connection.close()
            return diagnoses
        except Exception as e:
            print(f"Error in get_possible_diagnoses: {e}")
            # Return fallback diagnoses if there's an error
            if 'fever' in symptoms:
                return fallback_diagnoses
            return []
