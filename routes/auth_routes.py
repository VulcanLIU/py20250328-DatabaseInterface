from flask import Blueprint, request, jsonify
import numpy as np
from database import Database
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    # 原login实现...
    # 使用Config.DATABASE_ACCOUNTS访问配置
    database_c = Config.DATABASE_ACCOUNTS
    #读取输入内容
    content = request.json
    key_value_list = np.array([list(item) for item in content.items()])
    input_args = key_value_list[:,1].tolist()

    db = Database()

    try:
        #解析输入的账户名和密码
        user_name = input_args[0]
        user_password = input_args[1]

        #获取数据库中存在的密码
        base_sql = f"""SELECT a.password
                        FROM
                            `{database_c}` a
                        WHERE
                            a.`userid` = {user_name}"""
        data = db.execute_query(base_sql)
        pwd_in_database = data[0]['password']

        #密码匹配
        if (pwd_in_database == user_password):
            #|-检索数据库中的用户名信息
            user_info_sql = f"""SELECT a.*
                            FROM 
                            `{database_c}` a
                            WHERE 
                            a.`userid` = {user_name}"""
            
            user_info_data = db.execute_query(user_info_sql)
            return jsonify({"data":user_info_data[0],"code":1,"message":'ok'})
        else:
            return jsonify({"data":'',"code":-1,"message":'账号或密码错误！'})
    except Exception as e:
        return jsonify({"data":'',"code":-1,"error":str(e)}),500
    finally:
        db.close()