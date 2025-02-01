from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
from io import BytesIO
import os
from datetime import datetime
import psycopg2
from psycopg2 import pool
from dateutil.parser import parse

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

def get_patching_schedule(start=None, end=None):
    conn = connection_pool.getconn()
    try:
        query = """
            SELECT * FROM patching_schedule 
            WHERE (%s IS NULL OR start_time >= %s)
            AND (%s IS NULL OR end_time <= %s)
        """
        df = pd.read_sql(query, conn, params=(start, start, end, end))
    finally:
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

@app.route('/unique-deployment-ids', methods=['GET'])
def unique_deployment_ids():
    try:
        # Fetch unique Deployment_IDs and sort them alphabetically
        unique_ids = sorted(patching_schedule['deployment_id'].unique().tolist(), key=str)
        return jsonify(unique_ids)
    except Exception as e:
        app.logger.error(f"Error fetching unique deployment IDs: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/events', methods=['GET'])
def get_events():
    try:
        start_str = request.args.get('start')
        end_str = request.args.get('end')
        deployment_id = request.args.get('deployment_id')
        environment = request.args.get('environment')

        start = pd.to_datetime(start_str).to_datetime64()
        end = pd.to_datetime(end_str).to_datetime64()

        filtered_events = patching_schedule[
            (patching_schedule['start_time'] <= end) &
            (patching_schedule['end_time'] >= start)
        ]

        if deployment_id:
            filtered_events = filtered_events[filtered_events['deployment_id'] == deployment_id]

        if environment:
            filtered_events = filtered_events[filtered_events['environment'] == environment]

        events = filtered_events.to_dict('records')
        for event in events:
            event['seal_id'] = event['seal_id']
            event['application_name'] = event['application_name']
            event['deployment_id'] = event['deployment_id']
            event['asset_name'] = event['asset_name']
            event['asset_function'] = event['asset_function']
            event['event_type'] = event['event_type']
            event['description'] = event['description']
            event['start_time'] = event['start_time'].isoformat()
            event['end_time'] = event['end_time'].isoformat()
            event['location'] = event['location']  # Include location

        return jsonify(events)
    except Exception as e:
        app.logger.error(f"Error fetching events: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/export', methods=['GET'])
def export_to_excel():
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    start_datetime = validate_date(start_str).to_pydatetime()
    end_datetime = validate_date(end_str).to_pydatetime()

    start_datetime = start_datetime.replace(microsecond=0)
    end_datetime = end_datetime.replace(microsecond=0)

    start_date = start_datetime.strftime("%Y%m%d")
    end_date = end_datetime.strftime("%Y%m%d")

    filtered_events = patching_schedule[
        (patching_schedule['start_time'].dt.date <= end_datetime.date()) &
        (patching_schedule['end_time'].dt.date >= start_datetime.date())
    ]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_events.to_excel(writer, index=False, sheet_name='Patching Schedule')

    output.seek(0)

    download_name = f'patching_schedule_{start_date}-{end_date}.xlsx'

    response = send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=download_name
    )
    response.headers["Content-Disposition"] = f"attachment; filename={download_name}"

    return response

@app.route('/unique-locations', methods=['GET'])
def unique_locations():
    try:
        deployment_id = request.args.get('deployment_id')
        if deployment_id:
            filtered_schedule = patching_schedule[patching_schedule['deployment_id'] == deployment_id]
        else:
            filtered_schedule = patching_schedule

        unique_locations = sorted(filtered_schedule['location'].unique().tolist(), key=str)
        return jsonify(unique_locations)
    except Exception as e:
        app.logger.error(f"Error fetching unique locations: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)