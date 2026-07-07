"""
Analytics Engine
The brain of the application. Analyzes study patterns
and generates personalized insights.
"""
from datetime import datetime, timedelta, date
from collections import defaultdict


class StudyAnalytics:
    """Analyzes study session data and generates insights."""
    
    def __init__(self, sessions):
        """
        Initialize with a list of session dictionaries.
        Each session has: study_date, study_time, subject, study_hours,
        break_minutes, focus_rating, distraction_level, etc.
        """
        self.sessions = sessions
        self.total_sessions = len(sessions)
    
    # ==========================================
    # Basic Statistics
    # ==========================================
    
    def get_total_hours(self):
        """Calculate total study hours."""
        return sum(float(s.get('study_hours', 0)) for s in self.sessions)
    
    def get_average_focus(self):
        """Calculate average focus rating (1-5)."""
        if not self.sessions:
            return 0
        total = sum(int(s.get('focus_rating', 0)) for s in self.sessions)
        return round(total / len(self.sessions), 2)
    
    def get_average_distraction(self):
        """Calculate average distraction level (1-5)."""
        if not self.sessions:
            return 0
        total = sum(int(s.get('distraction_level', 0)) for s in self.sessions)
        return round(total / len(self.sessions), 2)
    
    def get_longest_session(self):
        """Find the longest single session."""
        if not self.sessions:
            return 0
        return max(float(s.get('study_hours', 0)) for s in self.sessions)
    
    def get_goal_completion_rate(self):
        """Percentage of sessions where goal was completed."""
        if not self.sessions:
            return 0
        completed = sum(1 for s in self.sessions if s.get('goal_completed'))
        return round((completed / len(self.sessions)) * 100, 1)
    
    # ==========================================
    # Subject Analysis
    # ==========================================
    
    def get_subject_distribution(self):
        """Get hours per subject."""
        distribution = defaultdict(float)
        for s in self.sessions:
            subject = s.get('subject', 'Unknown')
            distribution[subject] += float(s.get('study_hours', 0))
        
        # Sort by hours descending
        return sorted(
            [{"subject": k, "hours": round(v, 2)} for k, v in distribution.items()],
            key=lambda x: x['hours'],
            reverse=True
        )
    
    def get_most_studied_subject(self):
        """Get the subject with most hours."""
        dist = self.get_subject_distribution()
        if dist:
            return dist[0]['subject']
        return "N/A"
    
    def get_weakest_subject(self):
        """Get the subject with least hours (min 1 session)."""
        dist = self.get_subject_distribution()
        if dist:
            return dist[-1]['subject']
        return "N/A"
    
    # ==========================================
    # Time Analysis
    # ==========================================
    
    def get_best_study_time(self):
        """
        Determine the time of day when user studies best
        (highest average focus).
        """
        time_focus = defaultdict(list)
        
        for s in self.sessions:
            study_time = s.get('study_time')
            if study_time:
                # study_time is a string like "09:00:00"
                try:
                    if isinstance(study_time, str):
                        hour = int(study_time.split(':')[0])
                    else:
                        hour = study_time.hour
                    
                    if 5 <= hour < 12:
                        period = "Morning"
                    elif 12 <= hour < 17:
                        period = "Afternoon"
                    elif 17 <= hour < 21:
                        period = "Evening"
                    else:
                        period = "Night"
                    
                    time_focus[period].append(int(s.get('focus_rating', 0)))
                except (ValueError, AttributeError):
                    continue
        
        if not time_focus:
            return "Unknown"
        
        # Find period with highest average focus
        avg_focus = {k: sum(v)/len(v) for k, v in time_focus.items()}
        best = max(avg_focus, key=avg_focus.get)
        return best
    
    def get_weekly_summary(self):
        """Get study hours for each day of the week."""
        weekly = defaultdict(float)
        for s in self.sessions:
            study_date = s.get('study_date')
            if study_date:
                if isinstance(study_date, str):
                    try:
                        study_date = datetime.strptime(study_date, "%Y-%m-%d").date()
                    except ValueError:
                        continue
                
                day_name = study_date.strftime("%A")
                weekly[day_name] += float(s.get('study_hours', 0))
        
        return dict(weekly)
    
    # ==========================================
    # Streak Calculation
    # ==========================================
    
    def calculate_streak(self):
        """
        Calculate current consecutive study streak.
        Returns the number of consecutive days with at least one session.
        """
        if not self.sessions:
            return 0
        
        # Get unique study dates
        study_dates = set()
        for s in self.sessions:
            study_date = s.get('study_date')
            if study_date:
                if isinstance(study_date, str):
                    try:
                        study_date = datetime.strptime(study_date, "%Y-%m-%d").date()
                    except ValueError:
                        continue
                study_dates.add(study_date)
        
        if not study_dates:
            return 0
        
        # Sort dates
        sorted_dates = sorted(study_dates, reverse=True)
        
        # Check streak from today backwards
        today = date.today()
        streak = 0
        
        # If most recent session is more than 1 day ago, streak is 0
        if (today - sorted_dates[0]).days > 1:
            return 0
        
        # Count consecutive days
        current_date = sorted_dates[0]
        for d in sorted_dates:
            if d == current_date:
                streak += 1
                current_date = current_date - timedelta(days=1)
            else:
                break
        
        return streak
    
    # ==========================================
    # Focus Drop Detection
    # ==========================================
    
    def detect_focus_drop(self):
        """
        Detect if focus drops during long sessions.
        Returns insight message or None.
        """
        if len(self.sessions) < 3:
            return None
        
        # Group sessions by duration category
        short = [s for s in self.sessions if float(s.get('study_hours', 0)) <= 1.5]
        medium = [s for s in self.sessions if 1.5 < float(s.get('study_hours', 0)) <= 2.5]
        long_sessions = [s for s in self.sessions if float(s.get('study_hours', 0)) > 2.5]
        
        if not (short and long_sessions):
            return None
        
        avg_focus_short = sum(int(s['focus_rating']) for s in short) / len(short)
        avg_focus_long = sum(int(s['focus_rating']) for s in long_sessions) / len(long_sessions)
        
        drop = avg_focus_short - avg_focus_long
        
        if drop >= 1.0:
            return {
                "type": "warning",
                "title": "Focus Drops in Long Sessions",
                "message": f"Your focus is {round(drop, 1)} points lower in sessions over 2.5 hours. Try taking breaks every 60-90 minutes to maintain concentration.",
                "icon": "⚠️"
            }
        return None
    
    # ==========================================
    # Distraction Pattern
    # ==========================================
    
    def get_distraction_pattern(self):
        """Find when distraction is highest."""
        if not self.sessions:
            return None
        
        avg_distraction = self.get_average_distraction()
        
        if avg_distraction >= 4:
            return {
                "type": "warning",
                "title": "High Distraction Alert",
                "message": f"Your average distraction level is {avg_distraction}/5. Try using focus modes, blocking apps, or studying in quieter locations like a library.",
                "icon": "😵"
            }
        elif avg_distraction >= 3:
            return {
                "type": "info",
                "title": "Moderate Distraction",
                "message": f"You face moderate distraction ({avg_distraction}/5). Consider using the Pomodoro technique or noise-canceling headphones.",
                "icon": "😐"
            }
        return None
    
    # ==========================================
    # Productivity Score
    # ==========================================
    
    def calculate_productivity_score(self):
        """
        Calculate composite productivity score (0-100).
        
        Formula:
        - 40% Consistency (regular studying)
        - 30% Average Focus
        - 20% Goal Completion
        - 10% Low Distraction
        """
        if not self.sessions:
            return 0
        
        # 1. Consistency score (40%)
        # Based on number of unique study days
        unique_days = len(set(str(s.get('study_date', '')) for s in self.sessions if s.get('study_date')))
        # Max 14 days = full score
        consistency = min((unique_days / 14) * 100, 100)
        
        # 2. Average focus score (30%)
        focus = self.get_average_focus()
        focus_score = (focus / 5) * 100
        
        # 3. Goal completion (20%)
        goal_rate = self.get_goal_completion_rate()
        
        # 4. Low distraction (10%)
        # Lower distraction = higher score
        distraction = self.get_average_distraction()
        distraction_score = ((5 - distraction) / 5) * 100
        
        # Weighted total
        total = (
            consistency * 0.40 +
            focus_score * 0.30 +
            goal_rate * 0.20 +
            distraction_score * 0.10
        )
        
        return round(total, 1)
    
    def get_productivity_grade(self, score):
        """Convert score to letter grade."""
        if score >= 90: return "A+"
        if score >= 80: return "A"
        if score >= 70: return "B"
        if score >= 60: return "C"
        if score >= 50: return "D"
        return "F"
    
    # ==========================================
    # Study Personality
    # ==========================================
    
    def detect_study_personality(self):
        """
        Determine user's study personality based on patterns.
        Returns a personality archetype.
        """
        if not self.sessions:
            return {
                "name": "New Learner",
                "description": "Log more sessions to discover your study personality!",
                "icon": "🌱"
            }
        
        # Analyze patterns
        best_time = self.get_best_study_time()
        avg_hours = self.get_total_hours() / max(self.total_sessions, 1)
        streak = self.calculate_streak()
        avg_focus = self.get_average_focus()
        
        # Night Owl
        if best_time == "Night":
            return {
                "name": "Night Owl",
                "description": "You do your best studying after dark. Schedule challenging subjects during late evening hours.",
                "icon": "🦉"
            }
        
        # Morning Learner
        if best_time == "Morning":
            return {
                "name": "Morning Star",
                "description": "You're at your sharpest in the morning. Tackle difficult subjects before noon.",
                "icon": "🌅"
            }
        
        # Deep Focus Learner (long sessions, high focus)
        if avg_hours >= 2.5 and avg_focus >= 4:
            return {
                "name": "Deep Focus Learner",
                "description": "You excel in long, immersive study sessions with excellent concentration.",
                "icon": "🎯"
            }
        
        # Short Burst Learner
        if avg_hours <= 1.0:
            return {
                "name": "Short Burst Learner",
                "description": "You prefer shorter, focused study sessions. Try Pomodoro technique to build on this strength.",
                "icon": "⚡"
            }
        
        # Weekend Warrior (most sessions on weekends)
        weekly = self.get_weekly_summary()
        weekend_hours = weekly.get('Saturday', 0) + weekly.get('Sunday', 0)
        weekday_hours = sum(v for k, v in weekly.items() if k not in ['Saturday', 'Sunday'])
        
        if weekend_hours > weekday_hours * 0.5 and self.total_sessions >= 5:
            return {
                "name": "Weekend Warrior",
                "description": "You study most intensively on weekends. Balance with weekday sessions for better retention.",
                "icon": "📅"
            }
        
        # Balanced Learner (default)
        return {
            "name": "Balanced Learner",
            "description": "You have a well-rounded study pattern. Keep up the consistent approach!",
            "icon": "⚖️"
        }
    
    # ==========================================
    # Achievements / Badges
    # ==========================================
    
    def get_achievements(self):
        """Check which achievements/badges the user has unlocked."""
        achievements = []
        
        # 7 Day Streak
        if self.calculate_streak() >= 7:
            achievements.append({
                "id": "streak_7",
                "name": "7 Day Streak",
                "description": "Studied 7 days in a row",
                "icon": "🔥",
                "unlocked": True
            })
        
        # 50 Hours
        if self.get_total_hours() >= 50:
            achievements.append({
                "id": "hours_50",
                "name": "50 Hours Studied",
                "description": "Logged 50 total study hours",
                "icon": "⏱️",
                "unlocked": True
            })
        
        # 100 Sessions
        if self.total_sessions >= 100:
            achievements.append({
                "id": "sessions_100",
                "name": "100 Sessions",
                "description": "Completed 100 study sessions",
                "icon": "💯",
                "unlocked": True
            })
        
        # Goal Master
        if self.get_goal_completion_rate() >= 90:
            achievements.append({
                "id": "goal_master",
                "name": "Goal Master",
                "description": "Completed 90%+ of your goals",
                "icon": "🏆",
                "unlocked": True
            })
        
        # Focus Master
        if self.get_average_focus() >= 4.5:
            achievements.append({
                "id": "focus_master",
                "name": "Focus Master",
                "description": "Maintained 4.5+ average focus",
                "icon": "🧠",
                "unlocked": True
            })
        
        # Early Bird (sessions before 8 AM)
        early_sessions = 0
        for s in self.sessions:
            study_time = s.get('study_time')
            if study_time:
                if isinstance(study_time, str):
                    try:
                        hour = int(study_time.split(':')[0])
                        if hour < 8:
                            early_sessions += 1
                    except (ValueError, IndexError):
                        pass
        
        if early_sessions >= 5:
            achievements.append({
                "id": "early_bird",
                "name": "Early Bird",
                "description": "Studied before 8 AM at least 5 times",
                "icon": "🐦",
                "unlocked": True
            })
        
        return achievements
    
    # ==========================================
    # AI Recommendations
    # ==========================================
    
    def generate_recommendations(self):
        """
        Generate personalized AI recommendations.
        These are rule-based (no LLM) but feel intelligent.
        """
        recommendations = []
        
        if not self.sessions:
            return [{
                "type": "info",
                "icon": "🚀",
                "title": "Get Started!",
                "message": "Log your first study session to unlock personalized insights."
            }]
        
        # Best time recommendation
        best_time = self.get_best_study_time()
        if best_time in ["Morning", "Night"]:
            time_icons = {"Morning": "🌅", "Night": "🌙"}
            recommendations.append({
                "type": "success",
                "icon": time_icons.get(best_time, "⏰"),
                "title": f"You're a {best_time} Learner!",
                "message": f"Your focus is highest during {best_time.lower()} sessions. Schedule difficult subjects like {self.get_most_studied_subject()} during this time."
            })
        
        # Focus drop recommendation
        focus_insight = self.detect_focus_drop()
        if focus_insight:
            recommendations.append(focus_insight)
        
        # Distraction recommendation
        distraction_insight = self.get_distraction_pattern()
        if distraction_insight:
            recommendations.append(distraction_insight)
        
        # Subject balance
        subjects = self.get_subject_distribution()
        if len(subjects) >= 2:
            weakest = subjects[-1]
            strongest = subjects[0]
            if weakest['hours'] < strongest['hours'] * 0.3:
                recommendations.append({
                    "type": "info",
                    "icon": "📚",
                    "title": "Balance Your Subjects",
                    "message": f"{weakest['subject']} has only received {weakest['hours']} hours. Consider increasing practice time to stay balanced with {strongest['subject']} ({strongest['hours']} hours)."
                })
        
        # Goal completion
        goal_rate = self.get_goal_completion_rate()
        if goal_rate < 70 and self.total_sessions >= 5:
            recommendations.append({
                "type": "warning",
                "icon": "🎯",
                "title": "Set More Realistic Goals",
                "message": f"You complete {goal_rate}% of your goals. Try setting smaller, more achievable goals to build momentum."
            })
        elif goal_rate >= 90 and self.total_sessions >= 5:
            recommendations.append({
                "type": "success",
                "icon": "🌟",
                "title": "Goal Crusher!",
                "message": f"You complete {goal_rate}% of your goals. Consider challenging yourself with more ambitious targets."
            })
        
        # Streak
        streak = self.calculate_streak()
        if streak == 0 and self.total_sessions >= 3:
            recommendations.append({
                "type": "info",
                "icon": "🔥",
                "title": "Start a New Streak",
                "message": "You haven't studied today. A study streak starts with just one session — log one now!"
            })
        elif streak >= 3:
            recommendations.append({
                "type": "success",
                "icon": "🔥",
                "title": f"{streak} Day Streak!",
                "message": f"Amazing! You've studied {streak} days in a row. Keep the momentum going!"
            })
        
        # Average session length
        avg_hours = self.get_total_hours() / max(self.total_sessions, 1)
        if avg_hours < 0.75 and self.total_sessions >= 5:
            recommendations.append({
                "type": "info",
                "icon": "⏱️",
                "title": "Try Longer Sessions",
                "message": f"Your average session is only {round(avg_hours, 1)} hours. Try extending to 1.5-2 hours for deeper learning."
            })
        elif avg_hours > 3.5 and self.total_sessions >= 3:
            recommendations.append({
                "type": "warning",
                "icon": "😴",
                "title": "Avoid Burnout",
                "message": f"Your sessions average {round(avg_hours, 1)} hours. Consider breaking them into 90-minute focused blocks with breaks."
            })
        
        # Add at least one general tip
        recommendations.append({
            "type": "tip",
            "icon": "💡",
            "title": "Pro Tip",
            "message": "Try the Active Recall method: after reading a page, close the book and explain it to yourself. It boosts retention by 50%."
        })
        
        return recommendations
    
    # ==========================================
    # Full Analytics Report
    # ==========================================
    
    def get_full_report(self):
        """Generate complete analytics report."""
        productivity_score = self.calculate_productivity_score()
        
        return {
            "stats": {
                "total_sessions": self.total_sessions,
                "total_hours": round(self.get_total_hours(), 2),
                "average_focus": self.get_average_focus(),
                "average_distraction": self.get_average_distraction(),
                "longest_session": self.get_longest_session(),
                "goal_completion_rate": self.get_goal_completion_rate(),
                "current_streak": self.calculate_streak(),
                "most_studied_subject": self.get_most_studied_subject(),
                "best_study_time": self.get_best_study_time()
            },
            "productivity": {
                "score": productivity_score,
                "grade": self.get_productivity_grade(productivity_score),
                "level": "Excellent" if productivity_score >= 80 else "Good" if productivity_score >= 60 else "Developing"
            },
            "personality": self.detect_study_personality(),
            "achievements": self.get_achievements(),
            "recommendations": self.generate_recommendations(),
            "weekly_summary": self.get_weekly_summary()
        }
