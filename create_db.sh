#!/bin/bash

DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="localhost"
DB_NAME="teach_easy"

export PGPASSWORD="$DB_PASSWORD"

execute_sql() {
    local db_name="$1"
    local sql_command="$2"
    echo "Executing SQL on $db_name: $sql_command"
    psql -h "$DB_HOST" -U "$DB_USER" -d "$db_name" -c "$sql_command"
}

# --- Check if Database Exists ---
if psql -h "$DB_HOST" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Database $DB_NAME already exists."
else
    echo "Creating database: $DB_NAME"
    execute_sql "postgres" "CREATE DATABASE \"$DB_NAME\";"
fi

# --- Table Creation SQL (Organized for Readability) ---

CREATE_TEACHERS_TABLE_SQL="
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    portfolio TEXT,
    password TEXT NOT NULL
);
"
CREATE_COURSES_TABLE_SQL="
CREATE TABLE IF NOT EXISTS courses (
    course_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    teacher_id INTEGER NOT NULL,
    icon_id INTEGER UNIQUE, -- Add icon_id column (assuming one icon per course)
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
);
"

CREATE_SUBJECTS_TABLE_SQL="
CREATE TABLE IF NOT EXISTS subjects (
    subject_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
"


CREATE_STUDENTS_TABLE_SQL="
CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    birthday DATE NOT NULL
);
"

CREATE_CLASSES_TABLE_SQL="
CREATE TABLE IF NOT EXISTS classes (
    class_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    subject_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    class_time DATE NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
);
"

# Adding ENUM for attendance status
CREATE_ATTENDANCE_STATUS_TYPE_SQL="
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'attendance_status') THEN
        CREATE TYPE attendance_status AS ENUM ('Attend', 'Absent', 'Late');
    END IF;
END
\$\$;
"

CREATE_ATTENDANCE_TABLE_SQL="
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status attendance_status NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);
"

CREATE_MARKS_TABLE_SQL="
CREATE TABLE IF NOT EXISTS marks (
    mark_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    mark DECIMAL NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);
"

CREATE_ICONS_TABLE_SQL="
CREATE TABLE IF NOT EXISTS icons (
    icon_id SERIAL PRIMARY KEY,
    icon_name TEXT,
    link TEXT
);
"



echo "Creating or updating tables in $DB_NAME"

# Correct Order: Create or update tables in dependency order
execute_sql "$DB_NAME" "$CREATE_TEACHERS_TABLE_SQL"
execute_sql "$DB_NAME" "$CREATE_ICONS_TABLE_SQL"
execute_sql "$DB_NAME" "$CREATE_COURSES_TABLE_SQL"
execute_sql "$DB_NAME" "$CREATE_SUBJECTS_TABLE_SQL"
execute_sql "$DB_NAME" "$CREATE_STUDENTS_TABLE_SQL"
execute_sql "$DB_NAME" "$CREATE_CLASSES_TABLE_SQL"
execute_sql "$DB_NAME" "$CREATE_ATTENDANCE_STATUS_TYPE_SQL"
execute_sql "$DB_NAME" "$CREATE_ATTENDANCE_TABLE_SQL"
execute_sql "$DB_NAME" "$CREATE_MARKS_TABLE_SQL"



echo "Database setup complete."


INSERT_ICONS_SQL="
INSERT INTO icons (icon_name, link) VALUES
    ('Deutsch', 'https://uxwing.com/wp-content/themes/uxwing/download/communication-chat-call/de-language-icon.png'),
    ('Astrology', 'https://uxwing.com/wp-content/themes/uxwing/download/nature-and-environment/planet-space-icon.png');
"

INSERT_TEACHER_SQL="
INSERT INTO teachers (name, surname, email, password, portfolio)
VALUES ('Default', 'Teacher', 'default.teacher@example.com', 'securepassword', 'https://www.example.com/portfolio');
"

echo "Creating or updating tables and inserting initial data in $DB_NAME"

DROP_ICON_ID_CONSTRAINT_SQL="
ALTER TABLE courses DROP CONSTRAINT IF EXISTS courses_icon_id_key;
"

execute_sql "$DB_NAME" "$DROP_ICON_ID_CONSTRAINT_SQL"
execute_sql "$DB_NAME" "$CREATE_COURSES_TABLE_SQL"
