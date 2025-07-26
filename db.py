import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="complaint_db",
        user="postgres",
        password="your_password_here",  # replace this
        host="localhost",
        port="5432"
    )
