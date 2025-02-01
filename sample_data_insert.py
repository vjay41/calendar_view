import psycopg2
from datetime import datetime, timedelta
import random

# Database connection parameters
DB_HOST = 'localhost'
DB_NAME = 'emms_db'
DB_USER = 'nco'
DB_PASSWORD = 'nco'

# Connect to the database
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()

# Drop the table if it exists and recreate it with the updated schema
cursor.execute("""
    DROP TABLE IF EXISTS patching_schedule;
    CREATE TABLE patching_schedule (
        seal_id VARCHAR(255),
        deployment_id VARCHAR(255),
        application_name VARCHAR(255),
        asset_name VARCHAR(255),
        environment VARCHAR(255),
        location VARCHAR(255),  -- Moved location after environment
        asset_function VARCHAR(255),
        event_type VARCHAR(255),
        description VARCHAR(255),
        start_time TIMESTAMP,
        end_time TIMESTAMP
    );
""")

# Sample data
environments = ['PROD', 'UAT', 'DEV']
event_types = ['Maintenance', 'Upgrade', 'Patch']
asset_functions = ['Database', 'Web Server', 'Application Server']
descriptions = ['Routine maintenance', 'Security patch', 'Feature upgrade']
locations = ['New York', 'San Francisco', 'London', 'Tokyo', 'Sydney']  # Sample locations

# Generate 100 sample records
for _ in range(100):
    seal_id = f'SEAL-{random.randint(1000, 9999)}'
    deployment_id = f'DEPLOY-{random.randint(100, 999)}'
    application_name = f'App-{random.randint(1, 50)}'
    asset_name = f'Asset-{random.randint(1, 100)}'
    environment = random.choice(environments)
    location = random.choice(locations)  # Randomly select a location
    asset_function = random.choice(asset_functions)
    event_type = random.choice(event_types)
    description = random.choice(descriptions)

    # Random start and end times within the current and next two months
    start_time = datetime.now() + timedelta(days=random.randint(0, 90))
    end_time = start_time + timedelta(hours=random.randint(1, 4))

    # Insert the record into the database
    cursor.execute("""
        INSERT INTO patching_schedule (
            seal_id, deployment_id, application_name, asset_name, environment,
            location, asset_function, event_type, description, start_time, end_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (seal_id, deployment_id, application_name, asset_name, environment,
          location, asset_function, event_type, description, start_time, end_time))

# Commit the transaction
conn.commit()

# Close the connection
cursor.close()
conn.close()

print("100 sample records inserted successfully.")
