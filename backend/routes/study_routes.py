"""
Study Session Routes
Handles creating, reading, updating, and deleting study sessions.
"""
from flask import Blueprint, request, jsonify
from database import get_connection, close_connection
from utils.validators import validate_study_session
from utils.helpers import format_date, format_time


study_bp = Blueprint("study", __name__, url_prefix="/api/study")


@study_bp.route("/sessions", methods=["POST"])
def create_session():
    """Create a new study session."""
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error, cleaned = validate_study_session(data)
        if not is_valid:
            return jsonify({"success": False, "error": error}), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Insert into database
        cur.execute("""
            INSERT INTO study_sessions 
            (student_name, study_date, study_time, subject, study_hours, 
             break_minutes, focus_rating, distraction_level, study_location,
             study_method, mood_before, mood_after, goal_completed, notes)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at;
        """, (
            cleaned["student_name"],
            cleaned["study_date"],
            cleaned["study_time"],
            cleaned["subject"],
            cleaned["study_hours"],
            cleaned["break_minutes"],
            cleaned["focus_rating"],
            cleaned["distraction_level"],
            cleaned["study_location"],
            cleaned["study_method"],
            cleaned["mood_before"],
            cleaned["mood_after"],
            cleaned["goal_completed"],
            cleaned["notes"]
        ))
        
        result = cur.fetchone()
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": "Study session created successfully",
            "data": {
                "id": result["id"],
                "created_at": format_date(result["created_at"])
            }
        }), 201
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@study_bp.route("/sessions", methods=["GET"])
def get_sessions():
    """Get all study sessions for a student."""
    try:
        # Optional query params
        student_name = request.args.get("student_name")
        limit = request.args.get("limit", 100, type=int)
        
        conn = get_connection()
        cur = conn.cursor()
        
        if student_name:
            cur.execute("""
                SELECT * FROM study_sessions
                WHERE student_name = %s
                ORDER BY study_date DESC, study_time DESC
                LIMIT %s;
            """, (student_name, limit))
        else:
            cur.execute("""
                SELECT * FROM study_sessions
                ORDER BY study_date DESC, study_time DESC
                LIMIT %s;
            """, (limit,))
        
        sessions = cur.fetchall()
        
        # Format dates
        formatted = []
        for s in sessions:
            formatted.append({
                "id": s["id"],
                "student_name": s["student_name"],
                "study_date": format_date(s["study_date"]),
                "study_time": format_time(s["study_time"]),
                "subject": s["subject"],
                "study_hours": float(s["study_hours"]),
                "break_minutes": s["break_minutes"],
                "focus_rating": s["focus_rating"],
                "distraction_level": s["distraction_level"],
                "study_location": s["study_location"],
                "study_method": s["study_method"],
                "mood_before": s["mood_before"],
                "mood_after": s["mood_after"],
                "goal_completed": s["goal_completed"],
                "notes": s["notes"],
                "created_at": format_date(s["created_at"])
            })
        
        return jsonify({
            "success": True,
            "count": len(formatted),
            "data": formatted
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@study_bp.route("/sessions/<int:session_id>", methods=["GET"])
def get_session(session_id):
    """Get a single study session by ID."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM study_sessions WHERE id = %s;", (session_id,))
        session = cur.fetchone()
        
        if not session:
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        return jsonify({"success": True, "data": dict(session)}), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@study_bp.route("/sessions/<int:session_id>", methods=["DELETE"])
def delete_session(session_id):
    """Delete a study session."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM study_sessions WHERE id = %s RETURNING id;", (session_id,))
        deleted = cur.fetchone()
        
        if not deleted:
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Session {session_id} deleted"
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@study_bp.route("/students", methods=["GET"])
def get_students():
    """Get list of all unique student names."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT student_name, COUNT(*) as session_count
            FROM study_sessions
            GROUP BY student_name
            ORDER BY student_name;
        """)
        
        students = cur.fetchall()
        
        return jsonify({
            "success": True,
            "data": [
                {"name": s["student_name"], "session_count": s["session_count"]}
                for s in students
            ]
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)
