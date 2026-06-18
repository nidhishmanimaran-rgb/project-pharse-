import sqlite3
import os

root = os.environ.get('SQLI_PLAYGROUND_ROOT', 'D:\\SQLi-playground-data')
print('SQLI_PLAYGROUND_ROOT =', root)
db = os.path.join(root, 'users.db')
print('Database path =', db)
print('Database exists =', os.path.exists(db))
if os.path.exists(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print('tables =', cur.fetchall())
    conn.close()
else:
    print('No database file found')
