#!/bin/bash
# Medical Chatbot Environment Setup Script

echo "Setting up environment for Medical Chatbot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d " " -f 2)
echo "Found Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "Installing required packages..."
pip install flask
pip install flask-cors
pip install mysql-connector-python
pip install nltk
pip install google-generativeai
pip install python-dotenv

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Create requirements.txt
echo "Creating requirements.txt..."
pip freeze > requirements.txt

# Create .env file template
echo "Creating .env file template..."
cat > .env.template << EOL
# Medical Chatbot Environment Variables
# Rename this file to .env and fill in your actual values

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=medical_chatbot
EOL

# Create actual .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.template .env
    echo "Created .env file. Please edit it with your actual credentials."
fi

# Check if MySQL is installed
if command -v mysql &> /dev/null; then
    echo "MySQL is installed."
    
    # Create database setup script
    cat > setup_database.sql << EOL
-- Medical Chatbot Database Setup

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS medical_chatbot;

-- Use the database
USE medical_chatbot;

-- Create symptoms table
CREATE TABLE IF NOT EXISTS symptoms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

-- Create diseases table
CREATE TABLE IF NOT EXISTS diseases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    treatment TEXT
);

-- Create symptoms_diseases relationship table
CREATE TABLE IF NOT EXISTS symptoms_diseases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symptom_id INT,
    disease_id INT,
    correlation_strength FLOAT,
    FOREIGN KEY (symptom_id) REFERENCES symptoms(id),
    FOREIGN KEY (disease_id) REFERENCES diseases(id)
);

-- Create user_interactions table
CREATE TABLE IF NOT EXISTS user_interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    message TEXT,
    response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
EOL
    
    echo "Created database setup script (setup_database.sql)."
    echo "You can run it with: mysql -u your_username -p < setup_database.sql"
else
    echo "MySQL is not installed. Please install MySQL 8.0 or higher."
fi

# Create directories if they don't exist
mkdir -p templates
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p screenshots

echo "Environment setup complete!"
echo "Next steps:"
echo "1. Edit the .env file with your actual credentials"
echo "2. Set up the MySQL database using setup_database.py or the SQL script"
echo "3. Run the application with 'python app.py'"