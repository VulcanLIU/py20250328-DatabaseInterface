from flask import request,current_app
from socketio_app import socketio
from flask_socketio import emit, join_room
import logger

@socketio.on('connect')
def handle_connect():
    userid = request.args.get('userid')

    try:
        with current_app.test_client() as client:
            resp = client.post('/api/user_connected',json={"userid":userid,"is_connected":1})
        print(resp.get_json())
        room_name = f"room_{userid}"  # 新建房间名
        join_room(room_name)  # 将用户加入到对应的房间
        emit('connection_status', {'status': 'connected'})
    except Exception as e:
        logger.sys.stdout.write(str(e))
        
@socketio.on('disconnect')
def handle_disconnect():
    userid = request.args.get('userid')

    try:
        with current_app.test_client() as client:
            resp = client.post('/api/user_connected',json={"userid":userid,"is_connected":0})
        print(resp.get_json())
        emit('connection_status', {'status': 'disconnected'})
    except Exception as e:
        logger.sys.stdout.write(str(e))

