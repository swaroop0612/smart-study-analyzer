from flask import Flask, request, jsonify
from analyze import get_summary, get_efficiency, get_subject_hours, get_daily_hours, get_focus_trend, get_distraction_analysis, get_insights, load_data
from flask_cors import CORS
import csv
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# CSV file name
CSV_FILE = 'study_data.csv'

# These are the columns we will save
COLUMNS = ['name', 'date', 'subject', 'hours', 'break_time', 'focus', 'distraction']


def create_csv_if_not_exists():
    # If the CSV file doesn't exist yet, create it with column headers
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writeheader()


@app.route('/')
def home():
    return "Smart Study Analyzer backend is running!"


@app.route('/log', methods=['POST'])
def log_session():
    # Get the data sent from the frontend
    data = request.get_json()

    # Basic check — make sure all fields are present
    for col in COLUMNS:
        if col not in data:
            return jsonify({"error": f"Missing field: {col}"}), 400

    # Make sure the CSV file exists
    create_csv_if_not_exists()

    # Save the data as a new row in the CSV
with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writerow({
            'name':        data['name'],
            'date':        data['date'],
            'subject':     data['subject'],
            'hours':       data['hours'],
            'break_time':  data['break_time'],
            'focus':       data['focus'],
            'distraction': data['distraction']
        })
    return jsonify({"message": "Session logged successfully!"}), 200
@app.route('/dashboard-data', methods=['GET'])
def dashboard_data():
    name = request.args.get('name', '').strip()
    df = load_data()
    if name:
        df = df[df['name'].str.lower() == name.lower()]
    if len(df) == 0:
        return jsonify({'error': 'No data found for this name'}), 404
    return jsonify({
        'summary':       get_summary(df),
        'efficiency':    get_efficiency(df),
        'subject_hours': get_subject_hours(df),
        'daily_hours':   get_daily_hours(df),
        'focus_trend':   get_focus_trend(df),
        'distraction':   get_distraction_analysis(df),
        'insights':      get_insights(df)
    })


if __name__ == '__main__':
    create_csv_if_not_exists()
    app.run(debug=True)