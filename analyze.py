import pandas as pd

CSV_FILE = 'study_data.csv'


def load_data():
    df = pd.read_csv(CSV_FILE)
    if 'name' not in df.columns:
        df['name'] = 'default'
    df['date'] = pd.to_datetime(df['date'])
    return df


def get_summary(df):
    total_hours     = round(df['hours'].sum(), 1)
    avg_hours       = round(df['hours'].mean(), 1)
    total_sessions  = len(df)
    best_subject    = df.groupby('subject')['focus'].mean().idxmax()
    return {
        'total_hours':    total_hours,
        'avg_hours':      avg_hours,
        'total_sessions': total_sessions,
        'best_subject':   best_subject
    }


def get_efficiency(df):
    # Efficiency = study time / (study time + break time in hours)
    df = df.copy()
    df['break_hours'] = df['break_time'] / 60
    df['efficiency']  = df['hours'] / (df['hours'] + df['break_hours'])
    df['efficiency']  = (df['efficiency'] * 100).round(1)
    avg_efficiency    = round(df['efficiency'].mean(), 1)
    return avg_efficiency


def get_subject_hours(df):
    # Total hours per subject
    result = df.groupby('subject')['hours'].sum().round(1)
    return result.to_dict()


def get_daily_hours(df):
    # Hours studied per date
    result = df.groupby(df['date'].dt.strftime('%Y-%m-%d'))['hours'].sum().round(1)
    return result.to_dict()


def get_focus_trend(df):
    # Average focus per date
    result = df.groupby(df['date'].dt.strftime('%Y-%m-%d'))['focus'].mean().round(2)
    return result.to_dict()


def get_distraction_analysis(df):
    # Count of each distraction level
    result = df['distraction'].value_counts()
    return result.to_dict()


def get_insights(df):
    insights = []

    # Insight 1: Best focus time of day (we use subject as proxy for now)
    best_focus_subject = df.groupby('subject')['focus'].mean().idxmax()
    best_focus_score   = round(df.groupby('subject')['focus'].mean().max(), 1)
    insights.append(f"Your focus is highest when studying {best_focus_subject} (avg {best_focus_score}/5)")

    # Insight 2: Distraction warning
    high_distraction = len(df[df['distraction'] == 'High'])
    if high_distraction > 0:
        insights.append(f"You had high distraction in {high_distraction} session(s) — try removing phone during study")

    # Insight 3: Efficiency insight
    avg_efficiency = get_efficiency(df)
    if avg_efficiency >= 75:
        insights.append(f"Great efficiency at {avg_efficiency}% — your break time is well balanced")
    elif avg_efficiency >= 50:
        insights.append(f"Moderate efficiency at {avg_efficiency}% — try slightly shorter breaks")
    else:
        insights.append(f"Low efficiency at {avg_efficiency}% — your break time is too long compared to study time")

    # Insight 4: Study consistency
    avg_hours = round(df['hours'].mean(), 1)
    if avg_hours >= 3:
        insights.append(f"Strong consistency — you average {avg_hours} hours per session")
    else:
        insights.append(f"You average {avg_hours} hours per session — try pushing toward 3 hours for deeper learning")

    # Insight 5: Focus drop warning
    low_focus = df[df['focus'] <= 2]
    if len(low_focus) > 0:
        subjects = ', '.join(low_focus['subject'].unique())
        insights.append(f"Low focus detected in: {subjects} — consider studying these earlier in the day")

    return insights


def run_analysis():
    df = load_data()

    print("\n===== SMART STUDY ANALYZER =====\n")

    summary = get_summary(df)
    print("--- Summary ---")
    print(f"Total sessions  : {summary['total_sessions']}")
    print(f"Total hours     : {summary['total_hours']}")
    print(f"Average hours   : {summary['avg_hours']} per session")
    print(f"Best subject    : {summary['best_subject']}")

    print("\n--- Efficiency ---")
    print(f"Average efficiency: {get_efficiency(df)}%")

    print("\n--- Hours by Subject ---")
    for subject, hours in get_subject_hours(df).items():
        print(f"  {subject}: {hours}h")

    print("\n--- Daily Hours ---")
    for date, hours in get_daily_hours(df).items():
        print(f"  {date}: {hours}h")

    print("\n--- Distraction Levels ---")
    for level, count in get_distraction_analysis(df).items():
        print(f"  {level}: {count} session(s)")

    print("\n--- Insights ---")
    for i, insight in enumerate(get_insights(df), 1):
        print(f"  {i}. {insight}")

    print("\n================================\n")


if __name__ == '__main__':
    run_analysis()