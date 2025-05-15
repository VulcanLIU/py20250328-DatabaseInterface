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

@purchase_bp.route('/upsert_part', methods=['POST'])
def upsert_part():
    db = Database()
    try:
        database_xvqiu = Config.DATABASE_A

        #获取客户端发来的数据
        data = request.get_json()
        print(data)
        #字段映射
        sql = f"SHOW COLUMNS FROM {database_xvqiu}"
        fields_info = db.execute_query(sql)
        fields = [row['Field'] for row in fields_info]
        values = [data.get(f, None) for f in fields]

        #读取SQL语言并结合数据进行填充
        upsert_sql_path = 'routes/sql/upsert_parts.sql'
        with open(upsert_sql_path, 'r', encoding='utf-8') as f:
            upsert_sql_template = f.read()
        upsert_sql = upsert_sql_template \
            .replace('{{ table_name }}', database_xvqiu) \
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

@purchase_bp.route('/delete_part', methods=['POST'])
def delete_part():
    db = Database()
    try:
        database_xvqiu = Config.DATABASE_A
        data = request.get_json()
        part_number = data.get('图号')
        if not part_number:
            return jsonify({"success": False, "error": "缺少图号参数"}), 400

        delete_sql = f"DELETE FROM {database_xvqiu} WHERE `图号` = '{part_number}'"
        print(delete_sql)
        db.execute_query(delete_sql)
        return jsonify({"success": True, "message": "删除成功"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

