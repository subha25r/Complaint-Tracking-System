from db_config import connect

def register_user(name, email, password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    conn.commit()
    cur.close()
    conn.close()

def login_user(email, password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user
