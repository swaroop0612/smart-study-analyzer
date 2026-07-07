"""
Data Models — Python representations of database tables.
Used for type hints and future ORM-like operations.
"""
from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional


@dataclass
class StudySession:
    """Represents a study session record."""
    id: Optional[int] = None
    student_name: str = ""
    study_date: date = None
    study_time: Optional[time] = None
    subject: str = ""
    study_hours: float = 0.0
    break_minutes: int = 0
    focus_rating: int = 3
    distraction_level: int = 3
    study_location: Optional[str] = None
    study_method: Optional[str] = None
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None
    goal_completed: bool = False
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON responses."""
        return {
            "id": self.id,
            "student_name": self.student_name,
            "study_date": self.study_date.isoformat() if self.study_date else None,
            "study_time": self.study_time.isoformat() if self.study_time else None,
            "subject": self.subject,
            "study_hours": self.study_hours,
            "break_minutes": self.break_minutes,
            "focus_rating": self.focus_rating,
            "distraction_level": self.distraction_level,
            "study_location": self.study_location,
            "study_method": self.study_method,
            "mood_before": self.mood_before,
            "mood_after": self.mood_after,
            "goal_completed": self.goal_completed,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
