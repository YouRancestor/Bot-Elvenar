import sqlite3

sql_str = 'CREATE TABLE session_info (username VARCHAR (32) UNIQUE NOT NULL, password VARCHAR (32), cookies TEXT, world_id VARCHAR (3), json_h VARCHAR (16), hash_key VARCHAR (32))'
conn = sqlite3.connect('test.db')
cur = conn.cursor()
cur.execute(sql_str)
conn.commit()
conn.close()
