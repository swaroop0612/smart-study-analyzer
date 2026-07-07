"""
Dashboard Routes
Provides aggregated stats for the dashboard page.
"""
from flask import Blueprint, request, jsonify
from database import get_connection, close_connection
from utils.helpers import safe_round

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/stats", methods=["GET"])
def get_stats():
    """Get overall stats for a student."""
    try:
        student_name = request.args.get("student_name")
        
        if not student_name:
            return jsonify({
                "success": False,
                "error": "student_name query parameter is required"
            }), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Basic stats
        cur.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                COALESCE(SUM(study_hours), 0) as total_hours,
                COALESCE(AVG(focus_rating), 0) as avg_focus,
                COALESCE(AVG(distraction_level), 0) as avg_distraction,
                COALESCE(MAX(study_hours), 0) as longest_session,
                COALESCE(AVG(break_minutes), 0) as avg_break,
                SUM(CASE WHEN goal_completed THEN 1 ELSE 0 END) as goals_completed
            FROM study_sessions
            WHERE student_name = %s;
        """, (student_name,))
        
        stats = cur.fetchone()
        
        # Most studied subject
        cur.execute("""
            SELECT subject, SUM(study_hours) as hours
            FROM study_sessions
            WHERE student_name = %s
            GROUP BY subject
            ORDER BY hours DESC
            LIMIT 1;
        """, (student_name,))
        fav_subject = cur.fetchone()
        
        return jsonify({
            "success": True,
            "data": {
                "total_sessions": stats["total_sessions"] or 0,
                "total_hours": safe_round(stats["total_hours"]),
                "average_focus": safe_round(stats["avg_focus"]),
                "average_distraction": safe_round(stats["avg_distraction"]),
                "longest_session": safe_round(stats["longest_session"]),
                "average_break": safe_round(stats["avg_break"]),
                "goals_completed": stats["goals_completed"] or 0,
                "goal_completion_rate": safe_round(
                    (stats["goals_completed"] or 0) / max(stats["total_sessions"], 1) * 100
                ),
                "most_studied_subject": fav_subject["subject"] if fav_subject else "N/A"
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@dashboard_bp.route("/daily-hours", methods=["GET"])
def get_daily_hours():
    """Get study hours grouped by date for line chart."""
    try:
        student_name = request.args.get("student_name")
        days = request.args.get("days", 30, type=int)
        
        if not student_name:
            return jsonify({"success": False, "error": "student_name required"}), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                study_date,
                SUM(study_hours) as total_hours,
                AVG(focus_rating) as avg_focus
            FROM study_sessions
            WHERE student_name = %s
              AND study_date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY study_date
            ORDER BY study_date ASC;
        """, (student_name, days))
        
        rows = cur.fetchall()
        
        return jsonify({
            "success": True,
            "data": {
                "labels": [str(r["study_date"]) for r in rows],
                "hours": [safe_round(r["total_hours"]) for r in rows],
                "focus": [safe_round(r["avg_focus"]) for r in rows]
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@dashboard_bp.route("/subject-distribution", methods=["GET"])
def get_subject_distribution():
    """Get hours per subject for bar chart."""
    try:
        student_name = request.args.get("student_name")
        
        if not student_name:
            return jsonify({"success": False, "error": "student_name required"}), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT subject, SUM(study_hours) as total_hours
            FROM study_sessions
            WHERE student_name = %s
            GROUP BY subject
            ORDER BY total_hours DESC;
        """, (student_name,))
        
        rows = cur.fetchall()
        
        return jsonify({
            "success": True,
            "data": {
                "labels": [r["subject"] for r in rows],
                "hours": [safe_round(r["total_hours"]) for r in rows]
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@dashboard_bp.route("/distraction-distribution", methods=["GET"])
def get_distraction_distribution():
    """Get count of sessions by distraction level for pie chart."""
    try:
        student_name = request.args.get("student_name")
        
        if not student_name:
            return jsonify({"success": False, "error": "student_name required"}), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT distraction_level, COUNT(*) as count
            FROM study_sessions
            WHERE student_name = %s
            GROUP BY distraction_level
            ORDER BY distraction_level;
        """, (student_name,))
        
        rows = cur.fetchall()
        
        labels_map = {1: "None", 2: "Low", 3: "Medium", 4: "High", 5: "Very High"}
        
        return jsonify({
            "success": True,
            "data": {
                "labels": [labels_map.get(r["distraction_level"], f"Level {r['distraction_level']}") for r in rows],
                "counts": [r["count"] for r in rows]
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@dashboard_bp.route("/weekly-hours", methods=["GET"])
def get_weekly_hours():
    """Get total study hours grouped by day of week."""
    try:
        student_name = request.args.get("student_name")
        
        if not student_name:
            return jsonify({"success": False, "error": "student_name required"}), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                EXTRACT(DOW FROM study_date) as day_num,
                TO_CHAR(study_date, 'Day') as day_name,
                SUM(study_hours) as total_hours
            FROM study_sessions
            WHERE student_name = %s
            GROUP BY day_num, day_name
            ORDER BY day_num;
        """, (student_name,))
        
        rows = cur.fetchall()
        
        # PostgreSQL returns 0=Sunday, 1=Monday, ..., 6=Saturday
        # We want Monday=0, Sunday=6 for a typical week display
        day_order = {
            1: "Monday",
            2: "Tuesday", 
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            0: "Sunday"
        }
        
        # Build full week with zeros for missing days
        result = {day: 0 for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        
        for row in rows:
            day_name = row['day_name'].strip()
            if day_name in result:
                result[day_name] = safe_round(row['total_hours'])
        
        return jsonify({
            "success": True,
            "data": {
                "labels": list(result.keys()),
                "hours": list(result.values())
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)


@dashboard_bp.route("/focus-trend", methods=["GET"])
def get_focus_trend():
    """Get focus rating over time for line chart."""
    try:
        student_name = request.args.get("student_name")
        
        if not student_name:
            return jsonify({"success": False, "error": "student_name required"}), 400
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT study_date, focus_rating, study_hours
            FROM study_sessions
            WHERE student_name = %s
            ORDER BY study_date ASC;
        """, (student_name,))
        
        rows = cur.fetchall()
        
        return jsonify({
            "success": True,
            "data": {
                "labels": [str(r["study_date"]) for r in rows],
                "focus": [r["focus_rating"] for r in rows],
                "hours": [float(r["study_hours"]) for r in rows]
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        close_connection(conn, cur)
