-- =====================================================
-- Smart Study Analyzer - Database Schema
-- =====================================================
-- This file creates all tables needed for the application.
-- Run this ONCE to set up the database structure.
-- =====================================================


-- Drop table if it exists (safe for re-runs during development)
DROP TABLE IF EXISTS study_sessions CASCADE;


-- =====================================================
-- Main Table: study_sessions
-- Stores every study session logged by users
-- =====================================================
CREATE TABLE study_sessions (
    id SERIAL PRIMARY KEY,
    
    -- Student identification (simple version, no login yet)
    student_name VARCHAR(100) NOT NULL,
    
    -- When the study session happened
    study_date DATE NOT NULL,
    study_time TIME,
    
    -- What was studied
    subject VARCHAR(100) NOT NULL,
    
    -- Duration details
    study_hours DECIMAL(4, 2) NOT NULL CHECK (study_hours > 0),
    break_minutes INTEGER DEFAULT 0 CHECK (break_minutes >= 0),
    
    -- Quality indicators (1-5 scale)
    focus_rating INTEGER NOT NULL CHECK (focus_rating BETWEEN 1 AND 5),
    distraction_level INTEGER NOT NULL CHECK (distraction_level BETWEEN 1 AND 5),
    
    -- Context
    study_location VARCHAR(50),
    study_method VARCHAR(50),
    
    -- Mood tracking
    mood_before VARCHAR(20),
    mood_after VARCHAR(20),
    
    -- Goal completion flag
    goal_completed BOOLEAN DEFAULT FALSE,
    
    -- Optional notes for future use
    notes TEXT,
    
    -- Timestamps for record keeping
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- Indexes for faster queries
-- =====================================================
CREATE INDEX idx_study_sessions_student_name ON study_sessions(student_name);
CREATE INDEX idx_study_sessions_study_date ON study_sessions(study_date);
CREATE INDEX idx_study_sessions_subject ON study_sessions(subject);
CREATE INDEX idx_study_sessions_student_date ON study_sessions(student_name, study_date);


-- =====================================================
-- Sample data for testing
-- (You can delete this section later)
-- =====================================================
INSERT INTO study_sessions 
    (student_name, study_date, study_time, subject, study_hours, break_minutes, 
     focus_rating, distraction_level, study_location, study_method, 
     mood_before, mood_after, goal_completed, notes)
VALUES
    ('Demo Student', '2026-07-01', '09:00:00', 'Mathematics', 2.0, 15, 5, 2, 
     'Home', 'Active Recall', 'Tired', 'Focused', TRUE, 'Solved calculus problems'),
    
    ('Demo Student', '2026-07-01', '14:00:00', 'Physics', 1.5, 10, 4, 3, 
     'Library', 'Practice Problems', 'Neutral', 'Confident', TRUE, 'Mechanics chapter'),
    
    ('Demo Student', '2026-07-02', '10:00:00', 'Mathematics', 2.5, 20, 4, 2, 
     'Home', 'Active Recall', 'Fresh', 'Focused', TRUE, 'Integration practice'),
    
    ('Demo Student', '2026-07-02', '20:00:00', 'Chemistry', 1.0, 5, 3, 4, 
     'Home', 'Reading', 'Tired', 'Neutral', FALSE, 'Organic chemistry basics'),
    
    ('Demo Student', '2026-07-03', '08:00:00', 'English', 1.5, 10, 5, 1, 
     'Library', 'Reading', 'Fresh', 'Energized', TRUE, 'Grammar and vocabulary'),
    
    ('Demo Student', '2026-07-03', '16:00:00', 'Mathematics', 2.0, 15, 4, 2, 
     'Home', 'Practice Problems', 'Neutral', 'Focused', TRUE, 'Solved past papers'),
    
    ('Demo Student', '2026-07-04', '09:30:00', 'Physics', 2.0, 15, 5, 1, 
     'Library', 'Active Recall', 'Fresh', 'Focused', TRUE, 'Thermodynamics'),
    
    ('Demo Student', '2026-07-04', '19:00:00', 'Chemistry', 1.5, 10, 3, 3, 
     'Home', 'Practice Problems', 'Tired', 'Neutral', TRUE, 'Reaction mechanisms'),
    
    ('Demo Student', '2026-07-05', '10:00:00', 'Mathematics', 3.0, 20, 4, 2, 
     'Home', 'Practice Problems', 'Fresh', 'Energized', TRUE, 'Mock test'),
    
    ('Demo Student', '2026-07-05', '21:00:00', 'English', 1.0, 5, 3, 4, 
     'Home', 'Reading', 'Tired', 'Tired', FALSE, 'Light reading');


-- =====================================================
-- Verification Query
-- =====================================================
SELECT 
    COUNT(*) AS total_sessions,
    SUM(study_hours) AS total_hours,
    ROUND(AVG(focus_rating), 2) AS avg_focus
FROM study_sessions;
