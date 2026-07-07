"""
AI Study Coach Routes
Endpoints for analytics, recommendations, and personality detection.
"""
from flask import Blueprint, request, jsonify
from database import get_connection, close_connection
from analytics import StudyAnalytics
from utils.helpers import format_date, format_time

coach_bp = Blueprint("coach", __name__, url_prefix="/api/coach")


@coach_bp.route("/report", methods=["GET"])
def get_coach_report():
    """
    Get full AI Study Coach report for a student.
    Includes stats, productivity score, personality, achievements, recommendations.
    """
    try:
        student_name = request.args.get("student_name")
        
        if not student_name:
            return jsonify({
                "success": False,
                "error": "student_name query parameter is required"
            }), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Fetch all sessions for the student
        cur.execute("""
            SELECT * FROM study_sessions
            WHERE student_name = %s
            ORDER BY study_date DESC, study_time DESC;
        """, (student_name,))
        
        sessions = cur.fetchall()
        
        # Convert to list of dicts (RealDictCursor already gives dicts)
        sessions_list = [dict(s) for s in sessions]
        
        if not sessions_list:
            return jsonify({
                "success": True,
                "data": {
                    "stats": {
                        "total_sessions": 0,
                        "total_hours": 0,
                        "average_focus": 0,
                        "average_distraction": 0,
                        "longest_session": 0,
                        "goal_completion_rate": 0,
                        "current_streak": 0,
                        "most_studied_subject": "N/A",
                        "best_study_time": "Unknown"
                    },
                    "productivity": {"score": 0, "grade": "N/A", "level": "New Learner"},
                    "personality": {
                        "name": "New Learner",
                        "description": "Log your first session to discover your study personality!",
                        "icon": "🌱"
                    },
                    "achievements": [],
                    "recommendations": [{
                        "type": "info",
                        "icon": "🚀",
                        "title": "Welcome!",
                        "message": "Log your first study session to unlock personalized insights and recommendations."
                    }],
                    "weekly_summary": {}
                }
            }), 200
        
        # Run analytics
        analytics = StudyAnalytics(sessions_list)
        report = analytics.get_full_report()
        
        return jsonify({
            "success": True,
            "data": report
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@coach_bp.route("/recommendations", methods=["GET"])
def get_recommendations():
    """Get just the AI recommendations for a student."""
    try:
        student_name = request.args.get("student_name")
        
        if not student_name:
            return jsonify({"success": False, "error": "student_name required"}), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM study_sessions
            WHERE student_name = %s
            ORDER BY study_date DESC;
        """, (student_name,))
        
        sessions = cur.fetchall()
        sessions_list = [dict(s) for s in sessions]
        
        analytics = StudyAnalytics(sessions_list)
        recommendations = analytics.generate_recommendations()
        
        return jsonify({
            "success": True,
            "count": len(recommendations),
            "data": recommendations
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@coach_bp.route("/productivity", methods=["GET"])
def get_productivity():
    """Get just the productivity score."""
    try:
        student_name = request.args.get("student_name")
        
        if not student_name:
            return jsonify({"success": False, "error": "student_name required"}), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM study_sessions
            WHERE student_name = %s;
        """, (student_name,))
        
        sessions = cur.fetchall()
        sessions_list = [dict(s) for s in sessions]
        
        analytics = StudyAnalytics(sessions_list)
        score = analytics.calculate_productivity_score()
        
        return jsonify({
            "success": True,
            "data": {
                "score": score,
                "grade": analytics.get_productivity_grade(score),
                "level": "Excellent" if score >= 80 else "Good" if score >= 60 else "Developing"
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@coach_bp.route("/personality", methods=["GET"])
def get_personality():
    """Get just the study personality."""
    try:
        student_name = request.args.get("student_name")
        
        if not student_name:
            return jsonify({"success": False, "error": "student_name required"}), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM study_sessions
            WHERE student_name = %s;
        """, (student_name,))
        
        sessions = cur.fetchall()
        sessions_list = [dict(s) for s in sessions]
        
        analytics = StudyAnalytics(sessions_list)
        personality = analytics.detect_study_personality()
        
        return jsonify({
            "success": True,
            "data": personality
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)
