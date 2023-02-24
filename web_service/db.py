# myproject/pybo/db.py
from pymysql import cursors, connect
db = connect(host='localhost',
                user='sesac',
                password='1111',
                port=8945,
                database='project',
                cursorclass=cursors.DictCursor)