import logger  # 日志重定向

from flask import Flask
from flask_cors import CORS
from config import Config
from routes.data_routes import data_bp
from routes.purchase_routes import purchase_bp
from routes.auth_routes import auth_bp
from routes.task_routes import task_bp
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# 注册蓝图
app.register_blueprint(data_bp, url_prefix='/api')
app.register_blueprint(purchase_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(task_bp, url_prefix='/api')

if __name__ == '__main__':
    logger.sys.stdout.write("111")
    app.run(host='0.0.0.0', port=5000, debug=False)