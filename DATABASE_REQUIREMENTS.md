# Database Requirements for Medical Chatbot

## Overview
The Medical Chatbot application requires a relational database system to store medical knowledge, symptom-disease relationships, and user interactions. MySQL 8.0+ is the chosen database management system due to its reliability, performance characteristics, and support for the relational data model needed for medical information.

## Database Schema

### Core Tables
1. **symptoms**
   - Stores medical symptoms with descriptions
   - Fields: id (PK), name, description

2. **diseases**
   - Stores medical conditions/diseases with descriptions and treatments
   - Fields: id (PK), name, description, treatment

3. **symptoms_diseases**
   - Maps the relationships between symptoms and diseases
   - Includes correlation strength (0-1 scale) indicating how strongly a symptom suggests a disease
   - Fields: id (PK), symptom_id (FK), disease_id (FK), correlation_strength

4. **user_interactions**
   - Records all user conversations with the chatbot
   - Fields: id (PK), user_id, message, response, timestamp

### Relationships
- Many-to-many relationship between symptoms and diseases
- Each symptom can be associated with multiple diseases
- Each disease can be associated with multiple symptoms
- Correlation strength quantifies the relationship

## Technical Requirements

### MySQL Configuration
- Version: MySQL 8.0 or higher
- Character Set: UTF-8 (utf8mb4)
- Collation: utf8mb4_unicode_ci
- Storage Engine: InnoDB (for transaction support)

### Connection Requirements
- The application requires database credentials stored in environment variables
- Connection pooling is recommended for production deployments
- Minimum permissions: SELECT, INSERT, UPDATE, DELETE on application database
- Database creation permissions required for initial setup

### Performance Considerations
- Indexes on symptom_id and disease_id in the symptoms_diseases table
- Optimized for read-heavy operations (diagnostic queries)
- Expected data volume: 
  * Hundreds to thousands of symptoms
  * Hundreds to thousands of diseases
  * Tens of thousands of symptom-disease relationships
  * Potentially millions of user interactions over time

### Data Security
- No personally identifiable health information (PHI) should be stored
- User IDs should be anonymized or pseudonymized
- Database access should be restricted to application servers only
- Regular backups required

## Deployment Considerations
- Local development can use MySQL on localhost
- Production should use a managed database service when possible
- Database migrations should be versioned and tested before deployment
- Initial data seeding script is provided in setup_database.py