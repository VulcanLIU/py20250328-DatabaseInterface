from flask_socketio import SocketIO

socketio = SocketIO()  # 只做初始化，不传 app

import routes.user_socketio