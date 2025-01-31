from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
from io import BytesIO
import os
from datetime import datetime

app = Flask(__name__)

# Load patching schedule from CSV
csv_file = os.path.join(os.path.dirname(__file__), 'data', 'patching_schedule.csv')
patching_schedule = pd.read_csv(csv_file)

# Convert 'start' and 'end' columns to datetime
patching_schedule['start'] = pd.to_datetime(patching_schedule['start'])
patching_schedule['end'] = pd.to_datetime(patching_schedule['end'])

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
        (patching_schedule['start'] >= start) & (patching_schedule['end'] <= end)
        ]

    # Convert to list of dictionaries and ensure dates are in ISO format
    events = filtered_events.to_dict('records')
    for event in events:
        event['start'] = event['start'].isoformat()  # Convert to ISO format
        event['end'] = event['end'].isoformat()      # Convert to ISO format

    return jsonify(events)

@app.route('/export', methods=['GET'])
def export_to_excel():
    # Get start and end dates from the request
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    # Convert to datetime64[ns] for comparison
    start = pd.to_datetime(start_str).to_datetime64()
    end = pd.to_datetime(end_str).to_datetime64()

    # Filter events within the date range
    filtered_events = patching_schedule[
        (patching_schedule['start'] >= start) & (patching_schedule['end'] <= end)
        ]

    # Create an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_events.to_excel(writer, index=False, sheet_name='Patching Schedule')

    output.seek(0)

    # Return the Excel file as a download
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='patching_schedule.xlsx'
    )

if __name__ == '__main__':
    app.run(debug=True)