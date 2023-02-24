from flask import Flask, request, render_template
import pymysql
from pymysql.constants import CLIENT

app = Flask(__name__,static_folder='./static')

conn = {
    "host": "localhost",
    "password": "1111",
    "port": 8945,
    "user": "sesac",
    "db" : "project",
    "client_flag": CLIENT.MULTI_STATEMENTS
}


db = pymysql.connect(**conn)


@app.route('/')
def index():
    #------전일_시간대별_알림_횟수----
    
    sql = """
            SELECT IFNULL(counts.count, 0) AS count
        FROM (
        SELECT 6 AS hour
        UNION ALL SELECT 7
        UNION ALL SELECT 8
        UNION ALL SELECT 9
        UNION ALL SELECT 10
        UNION ALL SELECT 11
        UNION ALL SELECT 12
        UNION ALL SELECT 13
        UNION ALL SELECT 14
        UNION ALL SELECT 15
        UNION ALL SELECT 16
        UNION ALL SELECT 17
        UNION ALL SELECT 18
        UNION ALL SELECT 19
        UNION ALL SELECT 20
        UNION ALL SELECT 21
        UNION ALL SELECT 22
        UNION ALL SELECT 23
        ) AS hours
        LEFT JOIN (
        SELECT HOUR(time) AS hour, COUNT(*) AS count
        FROM dog
        WHERE time >= DATE_SUB(CURDATE(), INTERVAL 1 DAY) AND time < CURDATE()
        GROUP BY hour
        ) AS counts ON hours.hour = counts.hour
        ORDER BY hours.hour;
    """
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    y_list = []
    for r in result :
        y_list.append(r[0])

    sql2 = '''SELECT IFNULL(counts.count, 0) AS count
            FROM (
            SELECT 6 AS hour
            UNION ALL SELECT 7
            UNION ALL SELECT 8
            UNION ALL SELECT 9
            UNION ALL SELECT 10
            UNION ALL SELECT 11
            UNION ALL SELECT 12
            UNION ALL SELECT 13
            UNION ALL SELECT 14
            UNION ALL SELECT 15
            UNION ALL SELECT 16
            UNION ALL SELECT 17
            UNION ALL SELECT 18
            UNION ALL SELECT 19
            UNION ALL SELECT 20
            UNION ALL SELECT 21
            UNION ALL SELECT 22
            UNION ALL SELECT 23
            ) AS hours
            LEFT JOIN (
            SELECT HOUR(time) AS hour, COUNT(*) AS count
            FROM dog
            WHERE DATE(TIME) = DATE(NOW())
            GROUP BY hour
            ) AS counts ON hours.hour = counts.hour
            ORDER BY hours.hour;'''

    cursor = db.cursor()
    cursor.execute(sql2)
    result2 = cursor.fetchall()
    t_list = []
    for r in result2 :
        t_list.append(r[0])

    #---------기록---------
    question_list = {}
    cursor = db.cursor()
    number = 8
    page = request.args.get('page', type=int, default=1)
    sql3 = 'SELECT * FROM dog WHERE DATE(TIME) = DATE(NOW()) ORDER BY TIME DESC LIMIT {} OFFSET {};'.format(number, number * (page - 1))
    cursor = db.cursor()
    cursor.execute(sql3)
    item  = cursor.fetchall()
    sql4 = 'SELECT count(*) as count FROM dog WHERE DATE(TIME) = DATE(NOW()) ORDER BY TIME DESC;'
    cursor = db.cursor()
    cursor.execute(sql4)
    get_length = cursor.fetchone()

    print(get_length[0])

    db.commit()

    max_page = (get_length[0] - 1) // number + 1
    question_list['item'] = item
    question_list['max_page'] = list(range(1,max_page+1))

    question_list['page'] = page
    question_list['total'] = get_length[0]
    question_list['number'] = number

    doglist = []
    print(question_list['item'])

    for e in question_list['item']:
        datetime = e[3]        

        time = datetime.strftime("%H:%M:%S")        
        temp = {'filename': './assets/images/capture/' + e[1],'location':e[2],'time':time}
        doglist.append(temp)

    question_list['item'] = doglist
    print(question_list['item'])

    # # return render_template('capturedata.html', doglist=doglist)
    return render_template('index.html', doglist=doglist,question_list=question_list, y_list=y_list, t_list=t_list)


@app.route('/data')
def data():
    curs = db.cursor()
    sql = "select * from dog ORDER BY TIME DESC ;SELECT COUNT(*) FROM dog WHERE DATE(TIME) = DATE(NOW()) ORDER BY TIME DESC;"


    curs.execute(sql)

    rows = curs.fetchall()
    doglist = []
    # print(rows)
    for e in rows:
        datetime = e[3]        
        date = datetime.strftime("%y년 %m월 %d일")
        time = datetime.strftime("%H:%M:%S")        
        temp = {'filename': './assets/images/capture/' + e[1],'location':e[2],'date':date,'time':time}
        doglist.append(temp)
        
    db.commit()


    question_list = {}
    cursor = db.cursor()
    number = 10
    page = request.args.get('page', type=int, default=1)
    sql = 'SELECT * FROM dog ORDER BY TIME DESC LIMIT {} OFFSET {};'.format(number, number * (page - 1))
    cursor.execute(sql)
    item  = cursor.fetchall()
    sql = 'SELECT count(*) as count FROM dog;'
    cursor.execute(sql)
    get_length = cursor.fetchone()
    max_page = (get_length[0] - 1) // number + 1
    question_list['item'] = item
    question_list['max_page'] = list(range(1,max_page+1))

    question_list['page'] = page
    question_list['total'] = get_length[0]
    question_list['number'] = number

    print(doglist)
    doglist = []
    print()
    print()
    print(question_list['item'])
    for e in question_list['item']:
        datetime = e[3]        
        date = datetime.strftime("%y년 %m월 %d일")
        time = datetime.strftime("%H:%M:%S")        
        temp = {'filename': './assets/images/capture/' + e[1],'location':e[2],'date':date,'time':time}
        doglist.append(temp)

    question_list['item'] = doglist
    # print(question_list['item'])

    # return render_template('capturedata.html', doglist=doglist)
    return render_template('capturedata.html', doglist=doglist, question_list=question_list)

app.run(host="0.0.0.0", port=8944, debug=True) 

db.close()
