import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "students.db")


def connect():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id TEXT,
        name TEXT,
        age INTEGER,
        gwa REAL,
        program TEXT,
        year INTEGER
    )
    """)

    conn.commit()
    conn.close()


def add_student(student):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)
    """, student)

    conn.commit()
    conn.close()


def get_all_students():
    conn = connect()
    cursor = conn.cursor()

    # Latest inserted first (stack-like order)
    cursor.execute("SELECT * FROM students ORDER BY rowid DESC")
    data = cursor.fetchall()

    conn.close()
    return data


def delete_student(student_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))

    conn.commit()
    conn.close()


def delete_all_students():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students")

    conn.commit()
    conn.close()


def student_id_exists(student_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()

    conn.close()
    return row is not None
