import logger  # 日志重定向

from flask import Blueprint, request, jsonify

import numpy as np
from database import Database
from config import Config

from socketio_app import socketio  # 导入socketio实例

task_bp = Blueprint('task', __name__)

@task_bp.route('/getTaskInfo', methods=['POST'])
def gettaskinfo():
    database = Config.DATABASE_TASKS
    
    #读取输入内容
    content = request.json
    key_value_list = np.array([list(item) for item in content.items()])
    input_keys = key_value_list[:,0].tolist()
    input_args = key_value_list[:,1].tolist()

    #解析输入的账户名和密码
    key = input_keys[0]
    name = input_args[0]
    userid = input_args[1]
    isArchived = input_args[2]
    try:
        #打开数据库
        db = Database()

        task_info_sql  = f"""SELECT a.*
                    FROM 
                    `{database}` a
                    WHERE
                    a.`{key}` = '{name}' and a.is_archived = {isArchived}"""
        
        task_info_data = db.execute_query(task_info_sql)
        return jsonify({"data":task_info_data,"code":1,"message":'ok'})
    except Exception as e:
        return jsonify({"data":'',"error":str(e)}),500
    finally:
        db.close()

@task_bp.route('/upsertTaskInfo', methods=['POST'])
def upsertTaskInfo():
    db = Database()
    try:
        database_task = Config.DATABASE_TASKS

        #获取客户端发来的数据
        data_list = request.get_json()
        print(data_list)
        #字段映射
        sql = f"SHOW COLUMNS FROM {database_task}"
        fields_info = db.execute_query(sql)
        fields = [row['Field'] for row in fields_info]
        for data in data_list:
            values = [data.get(f, None) for f in fields]

            #读取SQL语言并结合数据进行填充
            upsert_sql_path = 'routes/sql/upsert_parts.sql'
            with open(upsert_sql_path, 'r', encoding='utf-8') as f:
                upsert_sql_template = f.read()
            upsert_sql = upsert_sql_template \
                .replace('{{ table_name }}', database_task) \
                .replace('{{ fields }}', ','.join(f'`{f}`' for f in fields)) \
                .replace('{{ values_placeholders }}',  ','.join(f'"{f}"' for f in values)) \
                .replace('{{ update_fields }}', ', '.join(f"`{f}`=VALUES(`{f}`)" for f in fields if f != "图号"))

            print(upsert_sql)
            resp = db.execute_query(upsert_sql)
            emit_task_update_event(data.get('issuer_id'), data.get('responser_id'))
        return jsonify({"success": True, "message": "操作成功"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@task_bp.route('/updateTaskInfo', methods=['POST'])
def updateTaskInfo():
    db = Database()
    try:
        database_task = Config.DATABASE_TASKS

        #获取客户端发来的数据
        data = request.get_json()
        print(data)
        #字段映射
        sql = f"SHOW COLUMNS FROM {database_task}"
        fields_info = db.execute_query(sql)
        fields = [row['Field'] for row in fields_info]
        values = [data.get(f, None) for f in fields]

        # 假设ID字段名为'id'
        if 'id' not in data or data['id'] is None:
            return jsonify({"success": False, "error": "缺少ID字段"}), 400

        # 构建SET部分
        set_clause = ', '.join([f"`{f}`=%s" for f in fields if f != 'id'])
        update_values = [data.get(f, None) for f in fields if f != 'id']

        update_sql = f"UPDATE `{database_task}` SET {set_clause} WHERE `id`=%s"
        params = update_values + [data['id']]
        db.execute_query(update_sql, params)

        # 查询更新后的taskInfo
        select_sql = f"SELECT * FROM `{database_task}` WHERE `id`=%s"
        task_info = db.execute_query(select_sql, [data['id']])
        emit_task_update_event(data.get('issuer_id'), data.get('responser_id'))
        return jsonify({"success": True, "message": "更新成功", "taskInfo": task_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@task_bp.route('/getAllTaskCategories', methods=['GET'])
def getAllTaskCategories():
    """
    获取所有任务类别
    """
    db = Database()
    try:
        database_task = Config.DATABASE_TASKS
        sql = f"SELECT DISTINCT `category` FROM `{database_task}`"
        categories = db.execute_query(sql)
        return jsonify({"data": categories, "code": 1, "message": 'ok'})
    except Exception as e:
        return jsonify({"data": '', "code": -1, "error": str(e)}), 500
    finally:
        db.close()

def emit_task_update_event(issuer_id, responser_id):
    """
    发送任务更新事件到所有连接的客户端
    """
    try:
        socketio.emit('task_update', {'task_info': 'updated!'}, room=f"room_{issuer_id}")
        socketio.emit('task_update', {'task_info': 'updated!'}, room=f"room_{responser_id}")
        logger.sys.stdout.write(f"Task update event emitted to rooms: room_{issuer_id}, room_{responser_id}\n")
    except Exception as e:
        logger.sys.stdout.write(f"Error emitting task update event: {str(e)}")