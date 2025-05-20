import logger  # 日志重定向

from flask import Blueprint, request, jsonify
import numpy as np
from database import Database
from config import Config

task_bp = Blueprint('task', __name__)

@task_bp.route('/getTaskInfo', methods=['POST'])
def gettaskinfo():
    database = Config.DATABASE_TASKS
    
    #读取输入内容
    content = request.json
    key_value_list = np.array([list(item) for item in content.items()])
    input_args = key_value_list[:,1].tolist()

    #解析输入的账户名和密码
    name = input_args[0]
    userid = input_args[1]

    try:
        #打开数据库
        db = Database()

        task_info_sql  = f"""SELECT a.*
                    FROM 
                    `{database}` a
                    WHERE
                    a.`responser` = '{name}'"""
        
        task_info_data = db.execute_query(task_info_sql)
        return jsonify({"data":task_info_data,"code":1,"message":'ok'})
    except Exception as e:
        return jsonify({"data":'',"error":str(e)}),500
    finally:
        db.close()