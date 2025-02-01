from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
from io import BytesIO
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Database connection parameters
DB_HOST = 'localhost'
DB_NAME = 'emms_db'
DB_USER = 'nco'
DB_PASSWORD = 'nco'

def get_patching_schedule():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    query = "SELECT * FROM patching_schedule"  # Adjust the table name as necessary
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load patching schedule from PostgreSQL
patching_schedule = get_patching_schedule()

# Convert 'start_time' and 'end_time' columns to datetime
patching_schedule['start_time'] = pd.to_datetime(patching_schedule['start_time'])
patching_schedule['end_time'] = pd.to_datetime(patching_schedule['end_time'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events', methods=['GET'])
def get_events():
    # Get start and end dates from the request
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    # Convert to datetime64[ns] for comparison
    start = pd.to_datetime(start_str).to_datetime64()
    end = pd.to_datetime(end_str).to_datetime64()

    # Filter events within the date range
    filtered_events = patching_schedule[
        (patching_schedule['start_time'] >= start) & (patching_schedule['end_time'] <= end)
    ]

    # Convert to list of dictionaries and ensure dates are in ISO format
    events = filtered_events.to_dict('records')
    for event in events:
        event['start_time'] = event['start_time'].isoformat()  # Convert to ISO format
        event['end_time'] = event['end_time'].isoformat()      # Convert to ISO format

    return jsonify(events)

@app.route('/export', methods=['GET'])
def export_to_excel():
    # Get start and end dates from the request
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    # Convert to datetime objects, stripping microseconds
    start_datetime = pd.to_datetime(start_str).to_pydatetime()
    end_datetime = pd.to_datetime(end_str).to_pydatetime()

    # Remove microseconds to avoid extra characters
    start_datetime = start_datetime.replace(microsecond=0)
    end_datetime = end_datetime.replace(microsecond=0)

    # Format dates into YYYYMMDD format for filename
    start_date = start_datetime.strftime("%Y%m%d")
    end_date = end_datetime.strftime("%Y%m%d")

    # Filter events within the date range
    filtered_events = patching_schedule[
        (patching_schedule['start_time'].dt.date >= start_datetime.date()) &
        (patching_schedule['end_time'].dt.date <= end_datetime.date())
    ]

    # Create an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_events.to_excel(writer, index=False, sheet_name='Patching Schedule')

    output.seek(0)

    # Construct the filename with date range
    download_name = f'patching_schedule_{start_date}-{end_date}.xlsx'

    # Return the Excel file as a download
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=download_name
    )

if __name__ == '__main__':
    app.run(debug=True)
