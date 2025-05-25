from flask import request,current_app
from socketio_app import socketio
from flask_socketio import emit, join_room
import logger
# 假设有用户房间映射
users = {'user1': 'room_user1', 'user2': 'room_user2'}

@socketio.on('connect')
def handle_connect():
    userid = request.args.get('userid')

    try:
        with current_app.test_client() as client:
            resp = client.post('/api/user_connected',json={"userid":userid,"is_connected":1})
        print(resp.get_json())
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