import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_db_connection(with_database=True):
    """Create database connection to MySQL"""
    try:
        connection_params = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', '')
        }
        
        # Only add database parameter if requested
        if with_database:
            connection_params['database'] = os.getenv('MYSQL_DATABASE', 'medical_chatbot')
            
        connection = mysql.connector.connect(**connection_params)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def setup_database():
    """Set up the database and tables"""
    try:
        # Connect without specifying database
        connection = create_db_connection(with_database=False)
        if connection is None:
            print("Failed to connect to MySQL server")
            return
            
        cursor = connection.cursor()
        
        # Create database
        db_name = os.getenv('MYSQL_DATABASE', 'medical_chatbot')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        
        # Create symptoms table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS symptoms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT
        )
        """)
        
        # Create diseases table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS diseases (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            treatment TEXT
        )
        """)
        
        # Create symptoms_diseases relationship table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS symptoms_diseases (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symptom_id INT,
            disease_id INT,
            correlation_strength FLOAT,
            FOREIGN KEY (symptom_id) REFERENCES symptoms(id),
            FOREIGN KEY (disease_id) REFERENCES diseases(id)
        )
        """)
        
        # Create user_interactions table to store chat history
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(255),
            message TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database setup complete")
    except Error as e:
        print(f"Error setting up database: {e}")

def populate_sample_data():
    """Populate the database with sample data"""
    connection = create_db_connection()
    if connection is None:
        return
    
    cursor = connection.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM symptoms")
    if cursor.fetchone()[0] > 0:
        print("Sample data already exists. Skipping population.")
        cursor.close()
        connection.close()
        return
    
    # Sample symptoms
    symptoms = [
        ("fever", "Elevated body temperature above the normal range"),
        ("cough", "Sudden expulsion of air from the lungs"),
        ("headache", "Pain in the head or upper neck"),
        ("fatigue", "Extreme tiredness resulting from mental or physical exertion"),
        ("sore throat", "Pain or irritation in the throat that often worsens with swallowing"),
        ("chest pain", "Pain or discomfort in the chest area"),
        ("shortness of breath", "Difficulty breathing or a feeling of not getting enough air"),
        ("nausea", "Feeling of discomfort in the stomach with an urge to vomit"),
        ("vomiting", "Forceful expulsion of stomach contents through the mouth"),
        ("diarrhea", "Loose, watery bowel movements that occur more frequently than usual"),
        ("rash", "Area of irritated or swollen skin"),
        ("joint pain", "Discomfort, pain or inflammation arising from any joint"),
        ("muscle pain", "Pain affecting the muscles"),
        ("dizziness", "Feeling faint, woozy, weak or unsteady"),
        ("runny nose", "Excess drainage of mucus from the nose"),
        ("congestion", "Feeling of stuffiness or blockage in the nasal passages")
    ]
    
    # Sample diseases
    diseases = [
        ("Common Cold", "A viral infection of the upper respiratory tract", "Rest, fluids, over-the-counter medications for symptoms"),
        ("Influenza", "A viral infection that attacks respiratory system", "Rest, fluids, antiviral medications in severe cases"),
        ("COVID-19", "Infectious disease caused by the SARS-CoV-2 virus", "Rest, fluids, medication for symptoms, seek medical attention if severe"),
        ("Allergic Rhinitis", "Inflammation of the nasal passages caused by allergens", "Antihistamines, nasal corticosteroids, avoiding allergens"),
        ("Bronchitis", "Inflammation of the lining of bronchial tubes", "Rest, fluids, medication for symptoms, possibly antibiotics"),
        ("Pneumonia", "Infection that inflames air sacs in lungs", "Antibiotics, rest, fluids, oxygen therapy in severe cases"),
        ("Migraine", "Recurring headache that causes moderate to severe pain", "Pain relievers, triptans, preventive medications"),
        ("Gastroenteritis", "Inflammation of the stomach and intestines", "Fluids, rest, bland diet, anti-diarrheal medications")
    ]
    
    # Insert symptoms
    cursor.executemany("INSERT INTO symptoms (name, description) VALUES (%s, %s)", symptoms)
    
    # Insert diseases
    cursor.executemany("INSERT INTO diseases (name, description, treatment) VALUES (%s, %s, %s)", diseases)
    
    # Get symptom and disease IDs for relationships
    cursor.execute("SELECT id, name FROM symptoms")
    symptoms_map = {name: id for id, name in cursor.fetchall()}
    
    cursor.execute("SELECT id, name FROM diseases")
    diseases_map = {name: id for id, name in cursor.fetchall()}
    
    # Define symptom-disease relationships with correlation strength (0-1)
    relationships = [
        # Common Cold symptoms
        (symptoms_map["fever"], diseases_map["Common Cold"], 0.6),
        (symptoms_map["cough"], diseases_map["Common Cold"], 0.8),
        (symptoms_map["sore throat"], diseases_map["Common Cold"], 0.7),
        (symptoms_map["headache"], diseases_map["Common Cold"], 0.5),
        (symptoms_map["fatigue"], diseases_map["Common Cold"], 0.6),
        (symptoms_map["runny nose"], diseases_map["Common Cold"], 0.9),
        (symptoms_map["congestion"], diseases_map["Common Cold"], 0.8),
        
        # Influenza symptoms
        (symptoms_map["fever"], diseases_map["Influenza"], 0.9),
        (symptoms_map["cough"], diseases_map["Influenza"], 0.7),
        (symptoms_map["fatigue"], diseases_map["Influenza"], 0.9),
        (symptoms_map["headache"], diseases_map["Influenza"], 0.7),
        (symptoms_map["sore throat"], diseases_map["Influenza"], 0.5),
        (symptoms_map["muscle pain"], diseases_map["Influenza"], 0.8),
        (symptoms_map["runny nose"], diseases_map["Influenza"], 0.4),
        
        # COVID-19 symptoms
        (symptoms_map["fever"], diseases_map["COVID-19"], 0.8),
        (symptoms_map["cough"], diseases_map["COVID-19"], 0.8),
        (symptoms_map["fatigue"], diseases_map["COVID-19"], 0.7),
        (symptoms_map["shortness of breath"], diseases_map["COVID-19"], 0.7),
        (symptoms_map["headache"], diseases_map["COVID-19"], 0.5),
        (symptoms_map["sore throat"], diseases_map["COVID-19"], 0.4),
        (symptoms_map["congestion"], diseases_map["COVID-19"], 0.4),
        
        # Allergic Rhinitis symptoms
        (symptoms_map["runny nose"], diseases_map["Allergic Rhinitis"], 0.9),
        (symptoms_map["congestion"], diseases_map["Allergic Rhinitis"], 0.9),
        (symptoms_map["headache"], diseases_map["Allergic Rhinitis"], 0.4),
        (symptoms_map["sore throat"], diseases_map["Allergic Rhinitis"], 0.3),
        
        # Bronchitis symptoms
        (symptoms_map["cough"], diseases_map["Bronchitis"], 0.9),
        (symptoms_map["shortness of breath"], diseases_map["Bronchitis"], 0.7),
        (symptoms_map["chest pain"], diseases_map["Bronchitis"], 0.6),
        (symptoms_map["fatigue"], diseases_map["Bronchitis"], 0.5),
        
        # Pneumonia symptoms
        (symptoms_map["fever"], diseases_map["Pneumonia"], 0.8),
        (symptoms_map["cough"], diseases_map["Pneumonia"], 0.9),
        (symptoms_map["shortness of breath"], diseases_map["Pneumonia"], 0.9),
        (symptoms_map["chest pain"], diseases_map["Pneumonia"], 0.7),
        (symptoms_map["fatigue"], diseases_map["Pneumonia"], 0.7),
        
        # Migraine symptoms
        (symptoms_map["headache"], diseases_map["Migraine"], 0.9),
        (symptoms_map["nausea"], diseases_map["Migraine"], 0.7),
        (symptoms_map["vomiting"], diseases_map["Migraine"], 0.5),
        (symptoms_map["dizziness"], diseases_map["Migraine"], 0.6),
        
        # Gastroenteritis symptoms
        (symptoms_map["nausea"], diseases_map["Gastroenteritis"], 0.8),
        (symptoms_map["vomiting"], diseases_map["Gastroenteritis"], 0.8),
        (symptoms_map["diarrhea"], diseases_map["Gastroenteritis"], 0.9),
        (symptoms_map["fever"], diseases_map["Gastroenteritis"], 0.5),
        (symptoms_map["fatigue"], diseases_map["Gastroenteritis"], 0.6)
    ]
    
    # Insert relationships
    cursor.executemany("INSERT INTO symptoms_diseases (symptom_id, disease_id, correlation_strength) VALUES (%s, %s, %s)", relationships)
    
    connection.commit()
    cursor.close()
    connection.close()
    print("Sample data populated")

if __name__ == "__main__":
    print("Setting up Medical Chatbot database...")
    setup_database()
    print("Populating sample data...")
    populate_sample_data()
    print("Database setup complete!")