from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
import os
import numpy as np

app = Flask(__name__)
CORS(app)  # 限制为前端域名

database_a_name = "XvQiu20250401-b"
database_b_name = "DaoHuo20250401-b"
database_c_name = "accounts"

# 获取数据 API
@app.route('/api/data', methods=['GET'])
def get_data():
    db = Database()
    try:
        # 获取查询参数（如：/api/data?name=刘展鹏）
        search_name = request.args.get('name')
        
        # 基础SQL
        base_sql = "SELECT * FROM Sheet1"
        
        # 动态添加WHERE条件
        if search_name:
            sql = f"{base_sql} WHERE `姓名` = %s"
            data = db.execute_query(sql, (search_name,))
        else:
            data = db.execute_query(base_sql)
            
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

# 写入数据 API
@app.route('/api/data', methods=['POST'])
def add_data():
    #获取Json文件并转换为数组
    content = request.json
    key_value_list = np.array([list(item) for item in content.items()])
    second_column = key_value_list[:,1].tolist()

    db = Database()
    try:

        if not content:
            return jsonify({"success": False, "error": "Content required"}), 400
            
        db.execute_query(
            "INSERT INTO Sheet1 VALUES (%s,%s,%s)",
            tuple(second_column)
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@app.route('/api/perchase_data',methods = ['GET'])
def get_perchase_data():
    db = Database()
    args = ['product_name','product_number']
    column_name = ['所属产品名称','所属产品图号']
    object_array = [None]*len(args)
    try:
        # 基础SQL
        base_sql = f"""  SELECT 
                          a.*,COALESCE(b.`申报批次`,'未申报')AS`申报批次`,COALESCE(b.`是否到货`, '否') AS `是否到货`
                        FROM
                          `{database_a_name}` a
                        LEFT JOIN
                          `{database_b_name}` b
                        ON 
                          a.`清单编号` = b.`物料编号`"""
        
        # 获取查询参数（如：/api/data?name=刘展鹏）
        for index in range(len(args)):
            object_array[index] = request.args.get(args[index])
            
        add_sql = ""
        if object_array.count(None) != len(object_array):
            add_sql = " WHERE"
            _counter=0
            for index in range(len(object_array)):
                if object_array[index] != None and object_array[index] != '':
                    if _counter > 0:
                        add_sql =  f"{add_sql} &&"
                    add_sql = f"{add_sql} a.`{column_name[index]}` = '{object_array[index]}'"
                    _counter = _counter+1

        data = db.execute_query(base_sql+add_sql)
            
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

#获取采购需求中的产品图号
@app.route('/api/product_number',methods = ['GET'])
def get_product_number():
    db = Database()
    try:
        # 挑选基础SQL
        base_sql = f""" SELECT DISTINCT a.`所属产品图号`
                        FROM
                          `{database_a_name}` a
                        LEFT JOIN
                          `{database_b_name}` b
                        ON 
                          a.`清单编号` = b.`物料编号`"""
        data = db.execute_query(base_sql)
            
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()  

@app.route('/api/login',methods = ['POST'])
def login():
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
                            `{database_c_name}` a
                        WHERE
                            a.`userid` = {user_name}"""
        data = db.execute_query(base_sql)
        pwd_in_database = data[0]['password']

        #密码匹配
        if (pwd_in_database == user_password):
            #|-检索数据库中的用户名信息
            user_info_sql = f"""SELECT a.*
                            FROM 
                            `{database_c_name}` a
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # 生产环境应关闭debug  