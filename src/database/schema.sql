-- Mental Math Training App Database Schema

-- Sessions table: tracks each practice session
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mode_type TEXT NOT NULL CHECK(mode_type IN ('sprint', 'marathon', 'targeted')),
    category TEXT NOT NULL CHECK(category IN ('arithmetic', 'percentage', 'fractions', 'ratios', 'compound', 'estimation', 'mixed')),
    difficulty TEXT NOT NULL CHECK(difficulty IN ('easy', 'medium', 'hard', 'adaptive')),
    duration_seconds INTEGER,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    total_score INTEGER NOT NULL,
    avg_time_per_question REAL NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 1
);

-- Questions answered: tracks each individual question
CREATE TABLE IF NOT EXISTS questions_answered (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    question_type TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    question_text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    user_answer TEXT,
    is_correct BOOLEAN NOT NULL,
    time_taken_seconds REAL NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Badges: predefined achievement badges
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    badge_name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    icon TEXT NOT NULL
);

-- User badges: tracks which badges the user has earned
CREATE TABLE IF NOT EXISTS user_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    badge_id INTEGER NOT NULL,
    earned_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE
);

-- Daily streaks: tracks daily practice activity
CREATE TABLE IF NOT EXISTS daily_streaks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,
    sessions_completed INTEGER NOT NULL DEFAULT 0
);

-- User preferences: stores user settings
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sessions_timestamp ON sessions(timestamp);
CREATE INDEX IF NOT EXISTS idx_sessions_category ON sessions(category);
CREATE INDEX IF NOT EXISTS idx_questions_session_id ON questions_answered(session_id);
CREATE INDEX IF NOT EXISTS idx_questions_type ON questions_answered(question_type);
CREATE INDEX IF NOT EXISTS idx_daily_streaks_date ON daily_streaks(date);
