from flask import Flask
from flask import request
from flask_socketio import SocketIO, emit
from db_init import *
import json
from redis_utils import Redis
from datetime import datetime


port = 8001
app = Flask(__name__)
socket_io = SocketIO(app)


@socket_io.on('connect', namespace='/chat_room')
def test_connect():
    print("connect:  sid:" + str(request.sid) + "    args:" + str(request.args))
    accountInfo = Redis.read(request.args.get('token'))
    if accountInfo is None:
        return False
    print(accountInfo)
    emit('connect_response', {'ret': 'success', 'sid': request.sid}, to=request.sid, namespace='/chat')


@socket_io.on('disconnect', namespace='/chat_room')  # 有客户端断开WebSocket会触发该函数
def on_disconnect():
    # 连接对象关闭 删除对象ID
    print(u'connection id=[%s] exit' % (request.sid,))


@socket_io.on('new_message', namespace='/chat_room')
def new_message(message):
    print(message)
    jsonObj = json.loads(message)
    token = jsonObj.get('token')
    accountInfo = json.loads(Redis.read(token))
    if accountInfo is None:
        return False
    data = (accountInfo.get('user_id'), request.sid, jsonObj.get('msg'), accountInfo.get('nick_name'), accountInfo.get('user_avatar'), jsonObj.get('msg_type', 0))
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO ChatRecord(user_id, sid, msg, nick_name, user_avatar, msg_type) VALUES (?,?,?,?,?,?)',
                   data)
    accountInfo['id'] = cursor.lastrowid
    accountInfo['msg'] = jsonObj.get('msg')
    accountInfo['sid'] = request.sid
    accountInfo['created_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    accountInfo['msg_type'] = jsonObj.get('msg_type', 0)
    db.commit()
    emit('send_broadcast', json.dumps(accountInfo), broadcast=True, namespace='/chat_room')


@socket_io.on('xxxx', namespace='/chat_room')
def new_message(message):
    print(message)


@app.route('/history/list', methods=['GET'])
def history_list():
    db = connect_db()
    db.row_factory = dict_factory
    cursor = db.execute('select * from ChatRecord')
    return json.dumps(cursor.fetchall())


@app.route('/unread', methods=['GET'])
def unread_count():
    split = request.args.get('last_read_id').split('_')
    db = connect_db()
    db.row_factory = dict_factory

    if len(split) == 1:
        cursor = db.execute('select count(id) as count from ChatRecord where ID > ?', (split[0],))
    else:
        cursor = db.execute('select count(id) as count from ChatRecord where ID >= ?', (split[0],))

    return str(cursor.fetchone()['count'])


initdb()

if __name__ == '__main__':
    socket_io.run(app=app, host="0.0.0.0", port=port)
