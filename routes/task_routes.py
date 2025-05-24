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
    input_keys = key_value_list[:,0].tolist()
    input_args = key_value_list[:,1].tolist()

    #解析输入的账户名和密码
    key = input_keys[0]
    name = input_args[0]
    userid = input_args[1]

    try:
        #打开数据库
        db = Database()

        task_info_sql  = f"""SELECT a.*
                    FROM 
                    `{database}` a
                    WHERE
                    a.`{key}` = '{name}'"""
        
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
        data = request.get_json()
        print(data)
        #字段映射
        sql = f"SHOW COLUMNS FROM {database_task}"
        fields_info = db.execute_query(sql)
        fields = [row['Field'] for row in fields_info]
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
        data = db.execute_query(upsert_sql)
        return jsonify({"success": True, "message": "操作成功"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

