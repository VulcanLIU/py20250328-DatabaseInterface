from flask import Blueprint, request, jsonify
from database import Database
from config import Config

purchase_bp = Blueprint('purchase', __name__)

@purchase_bp.route('/perchase_data', methods=['GET'])
def get_perchase_data():
    db = Database()
    args = ['product_name','product_number']
    column_name = ['所属产品名称','所属产品图号']
    object_array = [None]*len(args)

    try:
        # 使用app.config获取配置
        database_a = Config.DATABASE_A
        database_b = Config.DATABASE_B
        # 原实现逻辑...
        # 基础SQL
        sql_path = 'routes/sql/purchase_data.sql'
        with open(sql_path, 'r', encoding='utf-8') as f:
            _base_sql = f.read()
        base_sql = _base_sql.replace('{{ database_a }}', database_a)\
                           .replace('{{ database_b }}', database_b)

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
        print(base_sql+add_sql)      
        data = db.execute_query(base_sql+add_sql)
            
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@purchase_bp.route('/product_number', methods=['GET'])
def get_product_number():
    db = Database()
    try:
        database_a = Config.DATABASE_A
        database_b = Config.DATABASE_B
        # 挑选基础SQL
        base_sql = f""" SELECT DISTINCT a.`所属产品图号`
                        FROM
                          `{database_a}` a
                        LEFT JOIN
                          `{database_b}` b
                        ON 
                          a.`清单编号` = b.`物料编号`"""
        data = db.execute_query(base_sql)
            
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()  