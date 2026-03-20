from flask import Flask, request, jsonify
from flask_cors import CORS
from analyze import get_summary, get_efficiency, get_subject_hours, get_daily_hours, get_focus_trend, get_distraction_analysis, get_insights, load_data
import csv
import os

app = Flask(__name__)
CORS(app, origins=["https://swaroop0612.github.io", "https://69bd180--tranquil-cocada-9ef323.netlify.app"])
CSV_FILE = 'study_data.csv'
COLUMNS = ['name', 'date', 'subject', 'hours', 'break_time', 'focus', 'distraction']


def create_csv_if_not_exists():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writeheader()


@app.route('/')
def home():
    return "Smart Study Analyzer backend is running!"
@app.route('/reset-csv')
def reset_csv():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    create_csv_if_not_exists()
    return "CSV reset successfully!"


@app.route('/log', methods=['POST'])
def log_session():
    data = request.get_json()

    for col in COLUMNS:
        if col not in data:
            return jsonify({"error": f"Missing field: {col}"}), 400

    create_csv_if_not_exists()

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
