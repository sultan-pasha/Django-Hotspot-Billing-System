import pymysql
from datetime import datetime, timedelta

def assign_radius_access(user):
    username = user.username
    password = user.raw_password
    plan = user.plan

    if plan == 'daily':
        speed = '512k/512k'
        expiration = datetime.now() + timedelta(days=1)
    elif plan == 'weekly':
        speed = '1M/1M'
        expiration = datetime.now() + timedelta(weeks=1)
    elif plan == 'monthly':
        speed = '2M/2M'
        expiration = datetime.now() + timedelta(days=30)
    else:
        speed = '512k/512k'
        expiration = datetime.now() + timedelta(days=1)

    expiration_str = expiration.strftime('%d %b %Y %H:%M')

    try:
        conn = pymysql.connect(
            host='localhost',
            user='radius',
            password='radiuspass',
            db='radius',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.Cursor
        )
        with conn.cursor() as cur:
            cur.execute("DELETE FROM radcheck WHERE username=%s", (username,))
            cur.execute("DELETE FROM radreply WHERE username=%s", (username,))

            cur.execute("INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, 'Cleartext-Password', ':=', %s)",
                        (username, password))

            cur.execute("INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Mikrotik-Rate-Limit', ':=', %s)",
                        (username, speed))

            cur.execute("INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Expiration', ':=', %s)",
                        (username, expiration_str))

        conn.commit()
        conn.close()
        print(f"[✔] RADIUS entry created for {username}")

    except Exception as e:
        print(f"[❌] Error adding user to RADIUS: {e}")
