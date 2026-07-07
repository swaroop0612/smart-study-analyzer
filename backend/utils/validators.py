"""
Input Validation Utilities
Validates data sent by the user before saving to database.
"""


def validate_study_session(data):
    """
    Validate study session data.
    Returns (is_valid, error_message, cleaned_data)
    """
    if not data:
        return False, "No data provided", None
    
    # Required fields
    required_fields = [
        "student_name", "study_date", "subject",
        "study_hours", "focus_rating", "distraction_level"
    ]
    
    for field in required_fields:
        if field not in data or data[field] in [None, ""]:
            return False, f"Missing required field: {field}", None
    
    # Student name
    if len(data["student_name"].strip()) < 2:
        return False, "Student name must be at least 2 characters", None
    
    if len(data["student_name"]) > 100:
        return False, "Student name too long (max 100 chars)", None
    
    # Subject
    if len(data["subject"].strip()) < 1:
        return False, "Subject cannot be empty", None
    
    # Study hours
    try:
        hours = float(data["study_hours"])
        if hours <= 0 or hours > 24:
            return False, "Study hours must be between 0 and 24", None
    except (ValueError, TypeError):
        return False, "Study hours must be a number", None
    
    # Focus rating (1-5)
    try:
        focus = int(data["focus_rating"])
        if focus < 1 or focus > 5:
            return False, "Focus rating must be between 1 and 5", None
    except (ValueError, TypeError):
        return False, "Focus rating must be an integer", None
    
    # Distraction level (1-5)
    try:
        distraction = int(data["distraction_level"])
        if distraction < 1 or distraction > 5:
            return False, "Distraction level must be between 1 and 5", None
    except (ValueError, TypeError):
        return False, "Distraction level must be an integer", None
    
    # Break minutes (optional)
    break_min = 0
    if "break_minutes" in data and data["break_minutes"] not in [None, ""]:
        try:
            break_min = int(data["break_minutes"])
            if break_min < 0 or break_min > 600:
                return False, "Break minutes must be between 0 and 600", None
        except (ValueError, TypeError):
            return False, "Break minutes must be an integer", None
    
    # Cleaned data
    cleaned = {
        "student_name": data["student_name"].strip(),
        "study_date": data["study_date"],
        "subject": data["subject"].strip(),
        "study_hours": float(data["study_hours"]),
        "focus_rating": int(data["focus_rating"]),
        "distraction_level": int(data["distraction_level"]),
        "break_minutes": break_min,
        "study_time": data.get("study_time"),
        "study_location": data.get("study_location"),
        "study_method": data.get("study_method"),
        "mood_before": data.get("mood_before"),
        "mood_after": data.get("mood_after"),
        "goal_completed": bool(data.get("goal_completed", False)),
        "notes": data.get("notes")
    }
    
    return True, None, cleaned
