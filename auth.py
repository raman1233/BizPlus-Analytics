import mysql.connector
import hashlib

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # your MySQL user
        password="raman@1234",  # your MySQL password
        database="bizpulse_db"
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
        conn.commit()
        return True
    except:
        return False
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, hashed_pw))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def save_file_metadata(username, filename):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO uploaded_files (username, filename) VALUES (%s, %s)",
        (username, filename)
    )
    conn.commit()
    cursor.close()
    conn.close()
