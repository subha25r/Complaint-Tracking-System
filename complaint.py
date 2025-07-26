from db_config import connect

def file_complaint(user_id, title, description):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO complaints (user_id, title, description) VALUES (%s, %s, %s)", (user_id, title, description))
    conn.commit()
    cur.close()
    conn.close()

def get_user_complaints(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM complaints WHERE user_id = %s", (user_id,))
    complaints = cur.fetchall()
    cur.close()
    conn.close()
    return complaints
