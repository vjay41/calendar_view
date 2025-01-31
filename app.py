from flask import Flask, render_template, request, send_file
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# Sample server patching schedule data
patching_schedule = [
    {"title": "Server 1 Patching", "start": "2023-10-05T09:00:00", "end": "2023-10-05T12:00:00"},
    {"title": "Server 2 Patching", "start": "2023-10-10T14:00:00", "end": "2023-10-10T16:00:00"},
    {"title": "Server 3 Patching", "start": "2023-10-15T10:00:00", "end": "2023-10-15T13:00:00"},
    {"title": "Server 4 Patching", "start": "2023-10-20T08:00:00", "end": "2023-10-20T11:00:00"},
]

@app.route('/')
def index():
    return render_template('index.html', events=patching_schedule)

@app.route('/export', methods=['GET'])
def export_to_excel():
    # Convert patching schedule to a DataFrame
    df = pd.DataFrame(patching_schedule)

    # Create an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Patching Schedule')

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