# src/database/utils.py

import configparser
from sqlalchemy import create_engine
import os
from urllib.parse import quote_plus # <-- IMPORT THIS

def get_db_engine():
    """
    Creates and returns a SQLAlchemy engine for connecting to the MySQL database.
    It reads credentials from the config.ini file and URL-encodes the password.
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.ini')
    
    config = configparser.ConfigParser()
    config.read(config_path)

    try:
        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        database = config['mysql']['database']

        # --- THIS IS THE KEY FIX ---
        # URL-encode the password to handle special characters like '@', '%', '$' etc.
        safe_password = quote_plus(password)

        # Construct the database connection URL using the safe password
        db_url = f"mysql+mysqlconnector://{user}:{safe_password}@{host}/{database}"

        # --- Optional: you can add a debug print here to see the final URL ---
        # print(f"DEBUG: Connecting with URL: {db_url}")
        
        engine = create_engine(db_url)
        
        connection = engine.connect()
        connection.close()
        
        return engine

    except Exception as e:
        print(f"Error creating database engine: {e}")
        print("Please check your database credentials and settings in config/config.ini")
        return None