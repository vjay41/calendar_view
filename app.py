from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
from io import BytesIO
import os
from datetime import datetime
import psycopg2
from psycopg2 import pool

app = Flask(__name__)

# Database connection parameters
DB_HOST = 'localhost'
DB_NAME = 'emms_db'
DB_USER = 'nco'
DB_PASSWORD = 'nco'

# Initialize a connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1,  # Minimum number of connections
    5,  # Maximum number of connections
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

def get_patching_schedule():
    # Get a connection from the pool
    conn = connection_pool.getconn()
    try:
        query = "SELECT * FROM patching_schedule"
        df = pd.read_sql(query, conn)
    finally:
        # Return the connection back to the pool
        connection_pool.putconn(conn)
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
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    start = pd.to_datetime(start_str).to_datetime64()
    end = pd.to_datetime(end_str).to_datetime64()

    filtered_events = patching_schedule[
        (patching_schedule['start_time'] >= start) & (patching_schedule['end_time'] <= end)
    ]

    events = filtered_events.to_dict('records')
    for event in events:
        event['start_time'] = event['start_time'].isoformat()
        event['end_time'] = event['end_time'].isoformat()

    return jsonify(events)

@app.route('/export', methods=['GET'])
def export_to_excel():
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    start_datetime = pd.to_datetime(start_str).to_pydatetime()
    end_datetime = pd.to_datetime(end_str).to_pydatetime()

    start_datetime = start_datetime.replace(microsecond=0)
    end_datetime = end_datetime.replace(microsecond=0)

    start_date = start_datetime.strftime("%Y%m%d")
    end_date = end_datetime.strftime("%Y%m%d")

    filtered_events = patching_schedule[
        (patching_schedule['start_time'].dt.date >= start_datetime.date()) &
        (patching_schedule['end_time'].dt.date <= end_datetime.date())
    ]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_events.to_excel(writer, index=False, sheet_name='Patching Schedule')

    output.seek(0)

    download_name = f'patching_schedule_{start_date}-{end_date}.xlsx'

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=download_name
    )

if __name__ == '__main__':
    app.run(debug=True)
