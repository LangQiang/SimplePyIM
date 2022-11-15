import sqlite3

DATABASE = './IMDB.db'


def connect_db():
    return sqlite3.connect(DATABASE, check_same_thread=False)


def initdb():
    # 用户表
    connect_db().execute('''CREATE TABLE if not exists ChatRecord(
        ID integer PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR(20),
        nick_name VARCHAR(20),
        sid VARCHAR(20),
        msg TEXT,
        user_avatar TEXT,
        msg_type INTEGER,
        pic_width INTEGER, 
        pic_height INTEGER,
        created_time TimeStamp NOT NULL DEFAULT (DATETIME('now', 'localtime'))
        )''')

    connect_db().commit()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
