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
        cursor.execute("CREATE DATABASE IF NOT EXISTS medical_chatbot")
        cursor.execute("USE medical_chatbot")
        
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
    
    # Sample symptoms
    symptoms = [
        ("fever", "Elevated body temperature above the normal range"),
        ("cough", "Sudden expulsion of air from the lungs"),
        ("headache", "Pain in the head or upper neck"),
        ("fatigue", "Extreme tiredness resulting from mental or physical exertion"),
        ("sore throat", "Pain or irritation in the throat that often worsens with swallowing"),
        ("chest pain", "Pain or discomfort in the chest area"),
        ("shortness of breath", "Difficulty breathing or a feeling of not getting enough air"),
        ("nausea", "Feeling of discomfort in the stomach with an urge to vomit")
    ]
    
    # Sample diseases
    diseases = [
        ("Common Cold", "A viral infection of the upper respiratory tract", "Rest, fluids, over-the-counter medications for symptoms"),
        ("Influenza", "A viral infection that attacks respiratory system", "Rest, fluids, antiviral medications in severe cases"),
        ("COVID-19", "Infectious disease caused by the SARS-CoV-2 virus", "Rest, isolation, symptom management, medical care for severe cases"),
        ("Pneumonia", "Infection that inflames air sacs in one or both lungs", "Antibiotics for bacterial pneumonia, rest, fluids"),
        ("Bronchitis", "Inflammation of the lining of bronchial tubes", "Rest, fluids, symptom relief medications")
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
        
        # Influenza symptoms
        (symptoms_map["fever"], diseases_map["Influenza"], 0.9),
        (symptoms_map["cough"], diseases_map["Influenza"], 0.7),
        (symptoms_map["fatigue"], diseases_map["Influenza"], 0.9),
        (symptoms_map["headache"], diseases_map["Influenza"], 0.7),
        (symptoms_map["sore throat"], diseases_map["Influenza"], 0.5),
        
        # COVID-19 symptoms
        (symptoms_map["fever"], diseases_map["COVID-19"], 0.8),
        (symptoms_map["cough"], diseases_map["COVID-19"], 0.9),
        (symptoms_map["fatigue"], diseases_map["COVID-19"], 0.8),
        (symptoms_map["shortness of breath"], diseases_map["COVID-19"], 0.7),
        
        # Pneumonia symptoms
        (symptoms_map["fever"], diseases_map["Pneumonia"], 0.8),
        (symptoms_map["cough"], diseases_map["Pneumonia"], 0.9),
        (symptoms_map["shortness of breath"], diseases_map["Pneumonia"], 0.9),
        (symptoms_map["chest pain"], diseases_map["Pneumonia"], 0.7),
        (symptoms_map["fatigue"], diseases_map["Pneumonia"], 0.7),
        
        # Bronchitis symptoms
        (symptoms_map["cough"], diseases_map["Bronchitis"], 0.9),
        (symptoms_map["shortness of breath"], diseases_map["Bronchitis"], 0.7),
        (symptoms_map["chest pain"], diseases_map["Bronchitis"], 0.6),
        (symptoms_map["fatigue"], diseases_map["Bronchitis"], 0.5)
    ]
    
    # Insert relationships
    cursor.executemany("INSERT INTO symptoms_diseases (symptom_id, disease_id, correlation_strength) VALUES (%s, %s, %s)", relationships)
    
    connection.commit()
    cursor.close()
    connection.close()
    print("Sample data populated")
